# ---------------------------------------------------------------------------
# Process contracts and processual ledger
# ---------------------------------------------------------------------------

import os
import json
from datetime import datetime, timezone
from typing import Iterator, Optional

from logline_kernel.acts.act import Act
from logline_kernel.core.errors import RegistrationError
from logline_kernel.core.hashing import content_hash
from logline_kernel.core.receipts import ReceiptLog
from logline_kernel.processes.contract import ProcessContract

class ProcessLedger:
    def __init__(self, path: str, receipts: Optional["ReceiptLog"] = None):
        self.path = path
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        self.receipts = receipts

    # -- reading ------------------------------------------------------------

    def entries(self) -> Iterator[dict]:
        if not os.path.exists(self.path):
            return

        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    yield json.loads(line)

    def records(self) -> list[Act]:
        return [Act.from_dict(e["record"]) for e in self.entries()]

    def get(self, process_record_id: str) -> Optional[Act]:
        for e in self.entries():
            if e["process_record_id"] == process_record_id:
                return Act.from_dict(e["record"])
        return None

    def head_hash(self) -> str:
        h = "process-ledger:genesis"
        for e in self.entries():
            h = e["entry_hash"]
        return h

    # -- registration -------------------------------------------------------

    def register(
        self,
        act: Act,
        process: ProcessContract,
        registered_by: str = "kernel",
    ) -> dict:
        """Register a processual record after consulting process rules.

        Correct registration:
          1. Does not declare truth.
          2. Does not activate effects.
          3. Ignites the correct process engine.
          4. Turns on the correct process light / colour.
        """

        light = process.light_for(act)
        problems = light["problems"]

        if problems:
            if self.receipts:
                self.receipts.emit(
                    "process.registration_denied",
                    {
                        "process_id": process.process_id,
                        "contract_hash": process.contract_hash,
                        "colour": "red",
                        "engine": "quarantine",
                        "problems": problems,
                        "who": act.who,
                        "did": act.did,
                        "this": act.this,
                    },
                    actor=registered_by,
                )
            raise RegistrationError(problems)

        prev = self.head_hash()

        process_record = {
            "process_id": process.process_id,
            "contract_hash": process.contract_hash,
            "record_id": act.process_id if hasattr(act, "process_id") else act.act_id,
            "record": act.body(),
            "registered_at": datetime.now(timezone.utc).isoformat(),
            "registered_by": registered_by,
            "registration_state": "ignited",
            "capability_state": "registered",
            "light": light,
            "prev_hash": prev,
        }

        process_record["process_record_id"] = content_hash(
            {
                "process_id": process_record["process_id"],
                "contract_hash": process_record["contract_hash"],
                "record_id": process_record["record_id"],
            },
            "preg:",
        )

        process_record["entry_hash"] = content_hash(
            {
                "process_record_id": process_record["process_record_id"],
                "process_id": process_record["process_id"],
                "contract_hash": process_record["contract_hash"],
                "record_id": process_record["record_id"],
                "record": process_record["record"],
                "light": process_record["light"],
                "prev_hash": process_record["prev_hash"],
            },
            "entry:",
        )

        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(process_record, ensure_ascii=False) + "\n")

        if self.receipts:
            self.receipts.emit(
                "process.registered",
                {
                    "process_record_id": process_record["process_record_id"],
                    "entry_hash": process_record["entry_hash"],
                    "process_id": process.process_id,
                    "contract_hash": process.contract_hash,
                    "colour": light["colour"],
                    "engine": light["engine"],
                    "lens_id": light["lens_id"],
                    "capability_state": "registered",
                },
                actor=registered_by,
            )

        return process_record

    # -- integrity ----------------------------------------------------------

    def verify_chain(self) -> tuple[bool, list[str]]:
        problems: list[str] = []
        prev = "process-ledger:genesis"

        for i, e in enumerate(self.entries()):
            if e["prev_hash"] != prev:
                problems.append(f"entry {i}: broken chain")

            expected_process_record_id = content_hash(
                {
                    "process_id": e["process_id"],
                    "contract_hash": e["contract_hash"],
                    "record_id": e["record_id"],
                },
                "preg:",
            )

            if e["process_record_id"] != expected_process_record_id:
                problems.append(f"entry {i}: process_record_id mismatch")

            expected_entry_hash = content_hash(
                {
                    "process_record_id": e["process_record_id"],
                    "process_id": e["process_id"],
                    "contract_hash": e["contract_hash"],
                    "record_id": e["record_id"],
                    "record": e["record"],
                    "light": e["light"],
                    "prev_hash": e["prev_hash"],
                },
                "entry:",
            )

            if e["entry_hash"] != expected_entry_hash:
                problems.append(f"entry {i}: tampered entry hash")

            reconstructed = Act.from_dict(e["record"])
            reconstructed_id = (
                reconstructed.process_id
                if hasattr(reconstructed, "process_id")
                else reconstructed.act_id
            )

            if reconstructed_id != e["record_id"]:
                problems.append(f"entry {i}: record body does not match record_id")

            prev = e["entry_hash"]

        return (not problems), problems
