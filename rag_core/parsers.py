"""Bounded parsers v1: UTF-8 text, PDF text pages, DOCX paragraphs (no OCR)."""

import io
import json
import os
import resource
import subprocess
import sys
import zipfile
from typing import TypedDict

from defusedxml import ElementTree

from .errors import RagError
from .settings import MAX_FILE


class ExtractedPage(TypedDict):
    page: int | None
    text: str


MAX_TEXT = 200_000
MAX_CHUNKS = 320


def extract(data: bytes, extension: str) -> list[dict]:
    pages: list[ExtractedPage]
    if not data or len(data) > MAX_FILE:
        raise RagError("file_size_limit", 413)
    if extension == ".txt":
        text = data.decode("utf-8", errors="strict")
        if "\0" in text:
            raise RagError("invalid_text")
        pages = [{"page": None, "text": text}]
    elif extension == ".pdf":
        if not data.startswith(b"%PDF-"):
            raise RagError("invalid_pdf")
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(data), strict=True)
        if reader.is_encrypted or len(reader.pages) > 100:
            raise RagError("pdf_limit")
        pages, total = [], 0
        for i, pdf_page in enumerate(reader.pages):
            # Reject huge decoded streams before the text parser handles operators.
            stream = pdf_page.get_contents()
            if stream and len(stream.get_data()) > 2 * 1024 * 1024:
                raise RagError("pdf_stream_limit")
            text = pdf_page.extract_text() or ""
            total += len(text)
            if total > MAX_TEXT:
                raise RagError("extraction_limit")
            pages.append({"page": i + 1, "text": text})
    elif extension == ".docx":
        if not data.startswith(b"PK\x03\x04"):
            raise RagError("invalid_docx")
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            entries = archive.infolist()
            if len(entries) > 256 or sum(e.file_size for e in entries) > 8 * 1024 * 1024:
                raise RagError("archive_limit")
            names = [e.filename for e in entries]
            if len(names) != len(set(names)) or "word/document.xml" not in names:
                raise RagError("invalid_docx")
            for e in entries:
                if e.flag_bits & 1 or e.file_size > max(1, e.compress_size) * 200:
                    raise RagError("archive_limit")
            root = ElementTree.fromstring(archive.read("word/document.xml"))
            ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
            paragraphs = [
                "".join(t.text or "" for t in p.iter(ns + "t")) for p in root.iter(ns + "p")
            ]
            pages = [{"page": None, "text": "\n".join(paragraphs)}]
    else:
        raise RagError("unsupported_format", 415)
    if sum(len(p["text"]) for p in pages) > MAX_TEXT:
        raise RagError("extraction_limit")
    chunks: list[dict] = []
    for page in pages:
        for start in range(0, len(page["text"]), 700):
            text = page["text"][start : start + 800]
            if not text.strip():
                continue
            chunks.append(
                {
                    "page": page["page"],
                    "ordinal": len(chunks),
                    "start": start,
                    "end": start + len(text),
                    "text": text,
                }
            )
            if len(chunks) > MAX_CHUNKS:
                raise RagError("chunk_limit")
    if not chunks:
        raise RagError("no_extractable_text")
    return chunks


def isolated_extract(data: bytes, extension: str) -> list[dict]:
    try:
        completed = subprocess.run(
            [sys.executable, "-m", "rag_core.parsers", extension],
            input=data,
            capture_output=True,
            timeout=15,
            env={"PATH": os.environ.get("PATH", ""), "PYTHONPATH": os.pathsep.join(sys.path)},
            check=False,
        )
    except subprocess.TimeoutExpired:
        raise RagError("parser_timeout") from None
    if completed.returncode != 0:
        raise RagError("parser_rejected")
    if len(completed.stdout) > 2_000_000:
        raise RagError("parser_output_limit")
    try:
        return json.loads(completed.stdout)
    except Exception:
        raise RagError("parser_rejected") from None


def main():
    resource.setrlimit(resource.RLIMIT_CPU, (10, 10))
    resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024,) * 2)
    resource.setrlimit(resource.RLIMIT_FSIZE, (0, 0))
    resource.setrlimit(resource.RLIMIT_NOFILE, (32, 32))
    try:
        print(json.dumps(extract(sys.stdin.buffer.read(MAX_FILE + 1), sys.argv[1])))
    except Exception:
        sys.exit(1)


if __name__ == "__main__":
    main()
