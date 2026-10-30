"""Desired cross-process BM25 contract; reproduces run 41029994294 offline."""

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]
PROBE = """
import json, socket, sys
def reject(*args, **kwargs):
    raise AssertionError('Network forbidden in ranking regression')
socket.socket.connect = reject
socket.create_connection = reject
from rag_core.service import rank
data = json.load(sys.stdin)
print(json.dumps({'reranked':rank(data['query'], data['chunks'], data['dense'], True),
                  'unreranked':rank(data['query'], data['chunks'], data['dense'], False),
                  'no_match':rank('zxqv123987unmatchable',data['chunks'],[('txt',0.1),('pdf2',0.1)],True)},sort_keys=True))
"""


def test_bm25_and_result_order_are_identical_across_process_hash_seeds():
    # Same public synthetic corpus/statistics as the failed restart checkpoint.
    data = {
        "query": "What is the blue rainwater tank capacity?",
        "chunks": [
            {"id": "txt", "text": (ROOT / "examples/corpus/orchard.txt").read_text()},
            {"id": "pdf1", "text": "Synthetic Cedar Orchard grows apples."},
            {"id": "pdf2", "text": "The blue rainwater tank holds 240 liters."},
        ],
        "dense": [("txt", 0.48518953), ("pdf2", 0.831784)],
    }
    outputs = []
    for seed in (0, 1, 2, 3, 7, 11):
        result = subprocess.run(
            [sys.executable, "-c", PROBE],
            cwd=ROOT,
            input=json.dumps(data),
            text=True,
            capture_output=True,
            timeout=20,
            env={**os.environ, "PYTHONHASHSEED": str(seed)},
            check=True,
        )
        outputs.append(json.loads(result.stdout))
    # Do not sort responses, discard scores or use a tolerance to hide the defect.
    assert all(value == outputs[0] for value in outputs)
    assert outputs[0]["no_match"] == []
    assert [hit["id"] for hit in outputs[0]["reranked"]] == ["txt", "pdf2"]
    assert all(hit["ranking"]["rrf"] == 1 / 61 + 1 / 62 for hit in outputs[0]["reranked"])
    assert all(hit["ranking"]["reranker"] == "disabled" for hit in outputs[0]["unreranked"])
