import hashlib
import json
import os

class AuditLog:
    def __init__(self, path="data/audit.log"):
        self.path = path
        self.last_checksum = self._load_last_checksum()
        self.last_seq_id = self._load_last_seq_id()

    def _load_last_checksum(self):
        if not os.path.exists(self.path):
            return "GENESIS"
        try:
            with open(self.path, "r") as f:
                lines = f.readlines()
                if not lines:
                    return "GENESIS"
                last_entry = json.loads(lines[-1])
                return last_entry.get("checksum", "GENESIS")
        except Exception:
            return "GENESIS"

    def _load_last_seq_id(self):
        if not os.path.exists(self.path):
            return 0
        try:
            with open(self.path, "r") as f:
                lines = f.readlines()
                if not lines:
                    return 0
                last_entry = json.loads(lines[-1])
                return int(last_entry.get("seq_id", 0))
        except Exception:
            return 0

    def _checksum(self, data: str) -> str:
        return hashlib.sha256(data.encode()).hexdigest()

    def record(self, entity_id: str, action: str, reason: str):
        entry = {
            "seq_id": self.last_seq_id + 1,
            "entity_id": entity_id,
            "action": action,
            "reason": reason,
            "prev_checksum": self.last_checksum
        }

        raw = json.dumps(entry, sort_keys=True)
        checksum = self._checksum(raw)
        entry["checksum"] = checksum

        try:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            with open(self.path, "a") as f:
                f.write(json.dumps(entry) + "\n")

            self.last_checksum = checksum
            self.last_seq_id += 1

        except Exception as e:
            raise Exception("Audit write failed — rollback required") from e
