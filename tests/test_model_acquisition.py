import copy
import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "acquisition", Path(__file__).parents[1] / "scripts/acquire_model.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def metadata():
    return {
        "sha": module.MODEL_REVISION,
        "cardData": {"license": "apache-2.0"},
        "siblings": [
            {
                "rfilename": module.FILES[0],
                "size": module.SIZES[module.FILES[0]],
                "lfs": {"sha256": module.ONNX_SHA256},
            },
            {
                "rfilename": module.FILES[1],
                "size": module.SIZES[module.FILES[1]],
                "blobId": module.VOCAB_GIT_OBJECT,
            },
        ],
    }


def test_only_exact_official_assets_allowed():
    assert set(module.validate_metadata(metadata())) == set(module.FILES)


@pytest.mark.parametrize("field", ["revision", "license", "oversize", "digest", "object"])
def test_changed_upstream_metadata_rejected_before_download(field):
    value = copy.deepcopy(metadata())
    if field == "revision":
        value["sha"] = "0" * 40
    elif field == "license":
        value["cardData"]["license"] = "unknown"
    elif field == "oversize":
        value["siblings"][0]["size"] += 1
    elif field == "digest":
        value["siblings"][0]["lfs"]["sha256"] = "0" * 64
    else:
        value["siblings"][1]["blobId"] = "0" * 40
    with pytest.raises(ValueError):
        module.validate_metadata(value)


def test_corrupt_asset_and_wall_timeout_fail_closed():
    with pytest.raises(ValueError, match="integrity"):
        module.verify_file(module.FILES[0], b"corrupt", {})
    with pytest.raises(TimeoutError):
        module.deadline(None, None)
