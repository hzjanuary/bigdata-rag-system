"""License evidence from locked installed distributions, with a reviewed allowlist."""

import argparse
import importlib.metadata
import json
from pathlib import Path

# Every installed runtime/dev/UI package must resolve to a reviewed license family.
APPROVED = {
    "MIT",
    "Apache-2.0",
    "BSD-2-Clause",
    "BSD-3-Clause",
    "PSF-2.0",
    "ISC",
    "MPL-2.0",
    "Unlicense",
    "Python-2.0",
    "CC0-1.0",
    "0BSD",
    "Zlib",
    "MIT-CMU",
}
CLASSIFIERS = {
    "MIT License": "MIT",
    "Apache Software License": "Apache-2.0",
    "BSD License": "BSD-3-Clause",
    "Python Software Foundation License": "PSF-2.0",
    "ISC License (ISCL)": "ISC",
    "Mozilla Public License 2.0 (MPL 2.0)": "MPL-2.0",
    "The Unlicense (Unlicense)": "Unlicense",
    "Public Domain": "CC0-1.0",
}
# Upstream metadata often omits an SPDX expression; these were reviewed from the
# package's bundled LICENSE/NOTICE or upstream project license, not inferred names.
OVERRIDES = {
    "workspace-rag-core": "MIT",
    "certifi": "MPL-2.0",
    "flatbuffers": "Apache-2.0",
    "onnxruntime": "MIT",
    "numpy": "BSD-3-Clause",
    "protobuf": "BSD-3-Clause",
    "pypdf": "BSD-3-Clause",
    "defusedxml": "PSF-2.0",
    "python-dateutil": "Apache-2.0 OR BSD-3-Clause",
    "six": "MIT",
    "pyyaml": "MIT",
    "pytz": "MIT",
    "zipp": "MIT",
    "packaging": "Apache-2.0 OR BSD-2-Clause",
    "tqdm": "MPL-2.0 AND MIT",
    "chardet": "LGPL-2.1-or-later",
    "rfc3987": "GPL-3.0-or-later",
    "pydeck": "Apache-2.0",
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--development-environment",
        action="store_true",
        help="Permit reviewed chardet/rfc3987 tooling licenses only; forbidden in runtime scope",
    )
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    rows, failures = [], []
    for distribution in sorted(
        importlib.metadata.distributions(), key=lambda d: d.metadata["Name"].lower()
    ):
        meta = distribution.metadata
        name = meta["Name"].lower().replace("_", "-")
        expression = meta.get("License-Expression") or OVERRIDES.get(name)
        if not expression:
            for classifier in meta.get_all("Classifier", []):
                expression = CLASSIFIERS.get(classifier.rsplit(" :: ", 1)[-1])
                if expression:
                    break
        if not expression:
            value = meta.get("License", "").strip()
            if value in APPROVED:
                expression = value
        if expression:
            import re

            tokens = set(re.findall(r"[A-Za-z0-9][A-Za-z0-9.+-]*", expression)) - {
                "OR",
                "AND",
                "WITH",
            }
            approved = tokens <= APPROVED
            if args.development_environment and name in {"chardet", "rfc3987"}:
                approved = expression == OVERRIDES[name]
        else:
            approved = False
        rows.append(
            {
                "name": name,
                "version": distribution.version,
                "license": expression,
                "approved": approved,
                "metadata_url": meta.get("Home-page")
                or next(iter(meta.get_all("Project-URL", [])), None),
            }
        )
        if not approved:
            failures.append(name)
    args.output.write_text(
        json.dumps(
            {
                "scope": (
                    "development tools and core" if args.development_environment else "runtime"
                ),
                "packages": rows,
                "unknown_or_unapproved": failures,
            },
            indent=2,
        )
        + "\n"
    )
    if not args.quiet:
        print(f"License inventory: {len(rows)} packages, {len(failures)} unknown/unapproved")
    if failures:
        print("Review required: " + ", ".join(failures))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
