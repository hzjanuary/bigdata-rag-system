import hashlib
import json
import threading
from typing import TYPE_CHECKING

import numpy as np

from .errors import RagError
from .settings import MODEL_ID, MODEL_REVISION, Settings, private_path

if TYPE_CHECKING:
    from onnxruntime import InferenceSession


ONNX_SHA256 = "6fd5d72fe4589f189f8ebc006442dbb529bb7ce38f8082112682524616046452"
# Tokenizer pinned after upstream Git blob verification in acquisition.
VOCAB_GIT_OBJECT = "cb202bfe2e3c98645018a6d12f182a434c9d3e02"


def mean_pool_normalize(hidden, mask):
    mask = np.asarray(mask, dtype=np.float32)[..., None]
    pooled = (hidden * mask).sum(axis=1) / np.clip(mask.sum(axis=1), 1e-9, None)
    return pooled / np.clip(np.linalg.norm(pooled, axis=1, keepdims=True), 1e-9, None)


class OnnxEmbedder:
    dimension = 384

    def __init__(self, settings: Settings):
        self.settings = settings
        self.session: InferenceSession | None = None
        self.lock = threading.Lock()

    def _load(self):
        if not self.settings.model_dir:
            raise RagError("model_not_installed", 503)
        root = private_path(self.settings.model_dir, directory=True)
        try:
            manifest = json.loads(private_path(root / "manifest.json").read_bytes())
            if manifest["model_id"] != MODEL_ID or manifest["revision"] != MODEL_REVISION:
                raise ValueError()
            onnx = private_path(root / "onnx/model.onnx")
            if hashlib.sha256(onnx.read_bytes()).hexdigest() != ONNX_SHA256:
                raise ValueError()
            tokenizer_path = private_path(root / "tokenizer.json")
            content = tokenizer_path.read_bytes()
            if (
                hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()
                != VOCAB_GIT_OBJECT
            ):
                raise ValueError()
            import onnxruntime as ort
            from tokenizers import Tokenizer

            ort.disable_telemetry_events()

            self.tokenizer = Tokenizer.from_file(str(tokenizer_path))
            self.tokenizer.enable_truncation(max_length=256)
            self.tokenizer.enable_padding()
            options = ort.SessionOptions()
            options.intra_op_num_threads = 2
            options.inter_op_num_threads = 1
            self.session = ort.InferenceSession(
                str(onnx), sess_options=options, providers=["CPUExecutionProvider"]
            )
        except RagError:
            raise
        except Exception:
            raise RagError("model_integrity_error", 503) from None

    def encode(self, texts: list[str]) -> list[list[float]]:
        with self.lock:
            if self.session is None:
                self._load()
            if self.session is None:
                raise RagError("model_integrity_error", 503)
            vectors = []
            for start in range(0, len(texts), 16):
                tokens = self.tokenizer.encode_batch(texts[start : start + 16])
                inputs = {
                    "input_ids": np.array([t.ids for t in tokens], dtype=np.int64),
                    "attention_mask": np.array([t.attention_mask for t in tokens], dtype=np.int64),
                    "token_type_ids": np.array([t.type_ids for t in tokens], dtype=np.int64),
                }
                required = {v.name for v in self.session.get_inputs()}
                hidden = self.session.run(None, {k: v for k, v in inputs.items() if k in required})[
                    0
                ]
                result = mean_pool_normalize(hidden, inputs["attention_mask"])
                if result.shape != (len(tokens), self.dimension) or not np.isfinite(result).all():
                    raise RagError("embedding_dimension_error", 503)
                vectors.extend(result.tolist())
            return vectors
