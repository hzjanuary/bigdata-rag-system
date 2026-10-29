import json
import os
import re
import secrets
import stat
from pathlib import Path
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .errors import RagError

MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
MODEL_REVISION = "10dbd2f06a8baf40ad285b037edda610c1b9a57c"
SCHEMA = "onnx-mean-mask-l2-256/chunk-800-100/v1"
MAX_FILE = 4 * 1024 * 1024


def identifier(value: str) -> str:
    if not re.fullmatch(r"[0-9a-f]{32}", value):
        raise RagError("invalid_id")
    return value


def slug(value: str) -> str:
    if not re.fullmatch(r"[a-z][a-z0-9-]{0,47}", value):
        raise RagError("invalid_slug")
    return value


def filename(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_. -]{0,95}\.(txt|pdf|docx)", value):
        raise RagError("invalid_filename")
    if ".." in value:
        raise RagError("invalid_filename")
    return value


def private_path(path: Path, directory: bool = False) -> Path:
    """Reject symlinks in every component, including dangling links."""
    path = path.absolute()
    for part in [*reversed(path.parents), path]:
        if part.is_symlink():
            raise RagError("unsafe_private_path")
    if not path.exists():
        raise RagError("private_path_missing")
    info = path.stat()
    if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) & 0o077:
        raise RagError("private_permissions_required")
    if directory != path.is_dir() or (not directory and not stat.S_ISREG(info.st_mode)):
        raise RagError("unsafe_private_path")
    return path


class Settings(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    state_dir: Path
    owner_token: str = Field(repr=False)
    api_url: str = "http://127.0.0.1:8000"
    qdrant_url: str = "http://127.0.0.1:6333"
    qdrant_key: str | None = Field(default=None, repr=False)
    model_dir: Path | None = None
    model_id: str = MODEL_ID
    model_revision: str = MODEL_REVISION
    dimension: int = 384
    schema_version: str = SCHEMA
    generation_enabled: bool = False
    provider_url: str | None = None
    provider_model: str | None = None
    provider_key_env: str = "RAG_PROVIDER_KEY"
    provider_timeout: int = Field(default=20, ge=1, le=30)
    provider_max_tokens: int = Field(default=256, ge=16, le=512)
    provider_context_chars: int = Field(default=6000, ge=800, le=8000)

    @field_validator("owner_token")
    @classmethod
    def token_valid(cls, v: str) -> str:
        if not re.fullmatch(r"[0-9a-f]{64}", v) or len(set(v)) < 12:
            raise ValueError("private generated owner token required")
        return v

    @model_validator(mode="after")
    def validate_settings(self):
        if not self.state_dir.is_absolute():
            raise ValueError("absolute state directory required")
        if (
            self.dimension != 384
            or self.model_id != MODEL_ID
            or self.model_revision != MODEL_REVISION
            or self.schema_version != SCHEMA
        ):
            raise ValueError("unsupported embedding/index version; explicit migration required")
        for url in (self.api_url, self.qdrant_url):
            u = urlsplit(url)
            if (
                u.scheme not in {"http", "https"}
                or not u.hostname
                or u.username
                or u.password
                or u.query
                or u.fragment
                or u.path not in {"", "/"}
            ):
                raise ValueError("invalid service URL")
        if self.generation_enabled:
            u = urlsplit(self.provider_url or "")
            local = u.hostname in {"localhost", "127.0.0.1", "::1"}
            if (
                (u.scheme != "https" and not (local and u.scheme == "http"))
                or not u.hostname
                or u.username
                or u.password
                or u.query
                or u.fragment
            ):
                raise ValueError("provider requires HTTPS or loopback HTTP")
            if not self.provider_model or not re.fullmatch(
                r"[A-Z][A-Z0-9_]{0,63}", self.provider_key_env
            ):
                raise ValueError("explicit provider model/key environment required")
        return self

    @property
    def index_metadata(self) -> dict:
        return {
            "model_id": self.model_id,
            "revision": self.model_revision,
            "dimension": self.dimension,
            "normalization": "l2",
            "schema": self.schema_version,
        }


def config_path() -> Path:
    return Path(os.environ.get("RAG_CONFIG", "~/.config/rag-core/config.json")).expanduser()


def load_settings(path: Path | None = None) -> Settings:
    try:
        path = private_path(path or config_path())
        settings = Settings.model_validate_json(path.read_bytes())
        private_path(settings.state_dir, directory=True)
        return settings
    except RagError:
        raise
    except Exception:
        raise RagError("invalid_private_config", 503) from None


def initialize(path: Path, state_dir: Path) -> None:
    path, state_dir = path.absolute(), state_dir.absolute()
    if path.exists() or path.is_symlink() or state_dir.exists() or state_dir.is_symlink():
        raise RagError("installation_already_exists")
    for item in (path, state_dir):
        for parent in item.parents:
            if parent.is_symlink():
                raise RagError("unsafe_private_path")
    os.umask(0o077)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    private_path(path.parent, directory=True)
    state_dir.mkdir(parents=True, mode=0o700)
    settings = Settings(state_dir=state_dir, owner_token=secrets.token_hex(32))
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(settings.model_dump(mode="json"), f, indent=2)
