"""Golden path 12: seal a real binary Diamond.

Bytes in, portable sealed-binary.v0 shell out — with custody and
compilation receipts emitted per the binding order, then the full
verification chain run back over the result.
"""
import json
import os
import sys

# Allow running examples without installing the package.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from logline_kernel.diamonds import receipts_v0, seal_binary, shell_v0

# The "compiled artifact": in real life a LoRA delta, adapter, or feature
# shard. Here: bytes that stand in for one.
payload = bytes.fromhex("00010203040506070809")

# Private sources: consumed, committed by digest, never distributed.
sources = [b"clause library v3", b"annotated rulings 2024-2026", b"internal playbook"]

result = seal_binary.seal_portable(
    payload,
    sources,
    who="compiler.lab.v1",
    compiler_hash="c" * 64,
    process_contract_hash="a" * 64,
    rights_policy_hash="f" * 64,
    unverified={"note": "demo shell for golden path 12"},
)

print("1. diamond_id       ", result.diamond_id)
print("2. payload_digest   ", result.payload_digest)
print("3. source_merkle    ", result.source_merkle_root)
print("4. portable         ", result.portable)
for receipt in result.receipts:
    print(f"5. receipt {receipt['did']:<18} id={receipt['id'][:16]}…  "
          f"conformant={not receipts_v0.diamond_receipt_problems(receipt)}")

# Anyone with the shell + bytes can re-verify everything:
digests = [seal_binary.source_digest(s) for s in sources]
problems = shell_v0.verify_sealed_binary(
    result.manifest, payload, digests, result.diamond_id)
print("6. re-verification  ", problems or "CLEAN")

classification, _ = shell_v0.classify_shell(result.manifest)
print("7. claim bins       ", json.dumps(classification, indent=2))
print("golden_path_12_complete")
