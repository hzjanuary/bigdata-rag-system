"""Numerical comparison preserves citation/text identity across vector round trips."""

import hashlib
import json
import math


def equivalent_search(left, right):
    if left["status"] != right["status"] or len(left["matches"]) != len(right["matches"]):
        return False
    for old, new in zip(left["matches"], right["matches"], strict=True):
        old, new = dict(old), dict(new)
        a, b = old.pop("ranking"), new.pop("ranking")
        if old != new or a.keys() != b.keys():
            return False
        for key in a:
            if isinstance(a[key], float) and isinstance(b[key], float):
                if not math.isclose(a[key], b[key], rel_tol=1e-6, abs_tol=1e-6):
                    return False
            elif a[key] != b[key]:
                return False
    return True


def restart_observation(ready_status, job_state, state, search, search_http_status=200):
    """No text, credentials, configuration or database rows in restart evidence."""
    provenance = (
        "id",
        "workspace",
        "document",
        "filename",
        "content_hash",
        "page",
        "ordinal",
        "start",
        "end",
        "citation",
    )
    ranking = ("dense_cosine", "bm25", "rrf", "reranker", "term_coverage", "score")
    matches = []
    if search is not None:
        for hit in search.get("matches", []):
            matches.append(
                {
                    **{k: hit[k] for k in provenance if k in hit},
                    "excerpt_sha256": hashlib.sha256(hit.get("excerpt", "").encode()).hexdigest(),
                    "ranking": {k: hit["ranking"][k] for k in ranking if k in hit["ranking"]},
                    "provenance_sha256": hashlib.sha256(
                        json.dumps(
                            {k: v for k, v in hit.items() if k != "ranking"}, sort_keys=True
                        ).encode()
                    ).hexdigest(),
                    "ranking_sha256": hashlib.sha256(
                        json.dumps(hit["ranking"], sort_keys=True).encode()
                    ).hexdigest(),
                }
            )
    return {
        "ready_status": ready_status,
        "job_state": job_state,
        "documents": [
            {k: d[k] for k in ("id", "workspace", "content_hash")} for d in state["documents"]
        ],
        "chunks": [
            {
                k: c[k]
                for k in (
                    "id",
                    "workspace",
                    "document",
                    "page",
                    "ordinal",
                    "start",
                    "end",
                    "text_sha256",
                )
            }
            for c in state["chunks"]
        ],
        "search_http_status": search_http_status,
        "search": None if search is None else {"status": search.get("status"), "matches": matches},
    }


def restart_comparison(before, after):
    """Exact score/order checks, with safe numeric deltas recorded before assertion."""
    a, b = before["search"], after["search"]
    left, right = ([] if a is None else a["matches"]), ([] if b is None else b["matches"])

    def without_rank(rows):
        return [
            {k: v for k, v in m.items() if k not in {"ranking", "ranking_sha256"}} for m in rows
        ]

    checks = {
        "API readiness after restart": after["ready_status"] == 200,
        "persisted job COMPLETED after API restart": before["job_state"]
        == after["job_state"]
        == "COMPLETED",
        "persisted document identities after API restart": before["documents"]
        == after["documents"],
        "persisted chunk identities after API restart": before["chunks"] == after["chunks"],
        "retrieval status after API restart": a is not None
        and b is not None
        and after["search_http_status"] == 200
        and a["status"] == b["status"] == "matched",
        "retrieval hit IDs and order after API restart": [m["id"] for m in left]
        == [m["id"] for m in right],
        "source citation provenance after API restart": without_rank(left) == without_rank(right),
        "exact ranking scores after API restart": [m["ranking_sha256"] for m in left]
        == [m["ranking_sha256"] for m in right],
    }
    differences = []
    for i, (old, new) in enumerate(zip(left, right, strict=False)):
        for field in sorted(set(old["ranking"]) | set(new["ranking"])):
            x, y = old["ranking"].get(field), new["ranking"].get(field)
            if x != y:
                row = {"hit_index": i, "field": field, "before": x, "after": y}
                if isinstance(x, (int, float)) and isinstance(y, (int, float)):
                    row["absolute_delta"] = abs(x - y)
                differences.append(row)
    return {
        "phase": "observed",
        "before": before,
        "after": after,
        "checks": checks,
        "ranking_differences": differences,
    }
