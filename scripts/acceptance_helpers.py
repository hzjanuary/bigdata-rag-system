"""Numerical comparison preserves citation/text identity across vector round trips."""

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
