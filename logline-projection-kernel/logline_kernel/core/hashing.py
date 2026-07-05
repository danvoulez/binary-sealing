"""Content-addressed hashing for the LogLine Kernel.

Implements the canon hash profile ``jcs-rfc8785``: JSON Canonicalization
Scheme (RFC 8785) + SHA-256. Self-contained so the kernel stays
dependency-free; conformance is pinned by the vectors in
LogLine-Foundation/conformance and by tests/test_hashing.py.

The three places a naive `json.dumps(sort_keys=True)` breaks conformance:
  1. Numbers must follow ECMAScript ToString (RFC 8785 §3.2.2.3), not
     Python repr — e.g. 1e16 -> "10000000000000000", 1.5e-8 -> "1.5e-8".
  2. Object keys sort by UTF-16 code units, not Unicode code points —
     the orders diverge for keys containing astral-plane characters.
  3. NaN and Infinity must be rejected, not serialized.
"""
from __future__ import annotations

import hashlib
import json
import math

_MAX_SAFE_INT = 2**53  # I-JSON: integers beyond this are not IEEE-754 exact


def _es_number(x: float) -> str:
    """Serialize a float per ECMAScript Number::toString (base 10)."""
    if math.isnan(x) or math.isinf(x):
        raise ValueError("NaN and Infinity are not valid in canonical JSON")
    if x == 0:  # covers -0.0, which serializes as "0"
        return "0"
    sign = "-" if x < 0 else ""
    r = repr(abs(x))  # shortest digits that round-trip, per CPython
    if "e" in r:
        mant, _, exp_s = r.partition("e")
        exp = int(exp_s)
    else:
        mant, exp = r, 0
    int_part, _, frac_part = mant.partition(".")
    digits = int_part + frac_part
    stripped = digits.lstrip("0")
    lead = len(digits) - len(stripped)
    s = stripped.rstrip("0")
    # value == 0.s * 10^n  with s free of leading/trailing zeros
    n = len(int_part) - lead + exp
    k = len(s)
    if k <= n <= 21:
        body = s + "0" * (n - k)
    elif 0 < n <= 21:
        body = s[:n] + "." + s[n:]
    elif -6 < n <= 0:
        body = "0." + "0" * (-n) + s
    else:
        e = n - 1
        m = s[0] + ("." + s[1:] if k > 1 else "")
        body = f"{m}e{'+' if e >= 0 else '-'}{abs(e)}"
    return sign + body


def _serialize(obj, out: list[str]) -> None:
    if obj is None:
        out.append("null")
    elif obj is True:
        out.append("true")
    elif obj is False:
        out.append("false")
    elif isinstance(obj, str):
        out.append(json.dumps(obj, ensure_ascii=False))
    elif isinstance(obj, int):
        if abs(obj) > _MAX_SAFE_INT:
            raise ValueError(f"integer exceeds I-JSON safe range: {obj}")
        out.append(str(obj))
    elif isinstance(obj, float):
        out.append(_es_number(obj))
    elif isinstance(obj, (list, tuple)):
        out.append("[")
        for i, item in enumerate(obj):
            if i:
                out.append(",")
            _serialize(item, out)
        out.append("]")
    elif isinstance(obj, dict):
        out.append("{")
        # RFC 8785: sort keys by UTF-16 code units, not code points
        for i, key in enumerate(sorted(obj, key=lambda k: k.encode("utf-16-be"))):
            if not isinstance(key, str):
                raise TypeError(f"object keys must be strings, got {type(key).__name__}")
            if i:
                out.append(",")
            out.append(json.dumps(key, ensure_ascii=False))
            out.append(":")
            _serialize(obj[key], out)
        out.append("}")
    else:
        raise TypeError(f"type not representable in canonical JSON: {type(obj).__name__}")


def canonical_json(obj) -> bytes:
    """RFC 8785 (JCS) canonical serialization, UTF-8 encoded."""
    out: list[str] = []
    _serialize(obj, out)
    return "".join(out).encode("utf-8")


def content_hash(obj, prefix: str = "") -> str:
    raw = canonical_json(obj)
    digest = hashlib.sha256(raw).hexdigest()
    return f"{prefix}{digest}" if prefix else digest
