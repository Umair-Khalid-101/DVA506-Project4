# persistence/audit_log.py
import hashlib
import json
import os

class AuditLog:
    def __init__(self, path="data/audit.log"):
        self.path = path
        self.last_checksum = self._load_last_checksum()

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
            # If file is corrupted, force safe mode
            return "GENESIS"

    def _checksum(self, data):
        return hashlib.sha256(data.encode()).hexdigest()

    def record(self, entity_id, action, reason):
        entry = {
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

        except Exception as e:
            raise Exception("Audit write failed — rollback required") from e
