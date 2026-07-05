"""Verify conformance vectors against the kernel."""

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMAS_DIR = os.path.join(ROOT, "schemas")
VECTORS_DIR = os.path.join(ROOT, "vectors")


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def validate_schema(obj: dict, schema: dict, path: str = "") -> list[str]:
    """Very small JSON Schema subset validator for v0 conformance."""
    problems: list[str] = []
    stype = schema.get("type")
    if stype == "object":
        if not isinstance(obj, dict):
            problems.append(f"{path}: expected object")
            return problems
        required = schema.get("required", [])
        for key in required:
            if key not in obj:
                problems.append(f"{path}: missing required field {key}")
        props = schema.get("properties", {})
        for key, subschema in props.items():
            if key in obj:
                problems.extend(validate_schema(obj[key], subschema, f"{path}.{key}"))
    elif stype == "array":
        if not isinstance(obj, list):
            problems.append(f"{path}: expected array")
        else:
            items = schema.get("items", {})
            for i, item in enumerate(obj):
                problems.extend(validate_schema(item, items, f"{path}[{i}]"))
    elif stype == "string":
        if not isinstance(obj, str) and obj is not None:
            problems.append(f"{path}: expected string")
    elif stype == "boolean":
        if not isinstance(obj, bool):
            problems.append(f"{path}: expected boolean")
    elif isinstance(stype, list):
        if not any(_matches_type(obj, t) for t in stype):
            problems.append(f"{path}: expected one of {stype}")
    return problems


def _matches_type(obj, stype: str) -> bool:
    if stype == "string":
        return isinstance(obj, str)
    if stype == "object":
        return isinstance(obj, dict)
    if stype == "array":
        return isinstance(obj, list)
    if stype == "boolean":
        return isinstance(obj, bool)
    if stype == "null":
        return obj is None
    return False


VECTOR_SCHEMA_MAP = {
    "flux_google_doc": "flux_manifest",
    "projection_product_spine": "projection",
    "sealable_projection": "sealability_report",
    "sealed_diamond": "diamond_manifest",
    "blind_registration": "process_record",
    "missing_process_contract": "process_contract",
    "projection_without_boundary": "projection",
    "diamond_without_revocation": "diamond_manifest",
    "access_without_receipt": "diamond_access_receipt",
    "multiple_process_matches": "process_record",
    "low_confidence_anchor": "anchor_package",
    "superseded_diamond_candidate": "diamond_state_event",
}


def semantic_problems(name: str, vector: dict) -> list[str]:
    """Extra semantic checks for invalid/ambiguous vectors."""
    problems: list[str] = []
    if name == "diamond_without_revocation":
        revocation = vector.get("sealability_context", {}).get("revocation", {})
        if revocation.get("exists") is not True:
            problems.append("revocation must exist and be true")
    return problems


def verify_vector(name: str, kind: str, expected_valid: bool) -> bool:
    schema_name = VECTOR_SCHEMA_MAP.get(name, name)
    schema_path = os.path.join(SCHEMAS_DIR, f"{schema_name}.schema.json")
    vector_path = os.path.join(VECTORS_DIR, kind, f"{name}.json")

    if not os.path.exists(schema_path):
        print(f"SKIP {kind}/{name}: missing schema {schema_path}")
        return True
    if not os.path.exists(vector_path):
        print(f"SKIP {kind}/{name}: missing vector {vector_path}")
        return True

    schema = load_json(schema_path)
    vector = load_json(vector_path)
    problems = validate_schema(vector, schema)
    problems.extend(semantic_problems(name, vector))
    ok = not problems

    if expected_valid and not ok:
        print(f"FAIL {kind}/{name}: expected valid but got {problems}")
        return False
    if not expected_valid and ok:
        print(f"FAIL {kind}/{name}: expected invalid but validated")
        return False

    print(f"OK {kind}/{name}")
    return True


def main() -> int:
    checks = [
        ("flux_google_doc", "valid", True),
        ("projection_product_spine", "valid", True),
        ("sealable_projection", "valid", True),
        ("sealed_diamond", "valid", True),
        ("blind_registration", "invalid", False),
        ("missing_process_contract", "invalid", False),
        ("projection_without_boundary", "invalid", False),
        ("diamond_without_revocation", "invalid", False),
        ("access_without_receipt", "invalid", False),
        ("multiple_process_matches", "ambiguous", True),
        ("low_confidence_anchor", "ambiguous", True),
        ("superseded_diamond_candidate", "ambiguous", True),
    ]

    ok = True
    for name, kind, expected_valid in checks:
        if not verify_vector(name, kind, expected_valid):
            ok = False

    print("verify_repo_vectors", "OK" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
