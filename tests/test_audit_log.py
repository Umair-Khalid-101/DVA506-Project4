import unittest
import os
import json
from smartmove.persistence.audit_log import AuditLog


class TestAuditLog(unittest.TestCase):

    def setUp(self):
        self.test_log_path = "data/test_audit.log"

        if os.path.exists(self.test_log_path):
            os.remove(self.test_log_path)

        self.audit = AuditLog(path=self.test_log_path)

    def tearDown(self):
        if os.path.exists(self.test_log_path):
            os.remove(self.test_log_path)

    def test_audit_log_file_created(self):
        self.audit.record("V1", "AVAILABLE -> IN_USE", "Rental started")
        self.assertTrue(os.path.exists(self.test_log_path))

    def test_checksum_chain_is_linked(self):
        self.audit.record("V1", "AVAILABLE -> IN_USE", "Rental started")
        self.audit.record("V1", "IN_USE -> AVAILABLE", "Rental ended")

        with open(self.test_log_path, "r") as f:
            lines = f.readlines()

        first_entry = json.loads(lines[0])
        second_entry = json.loads(lines[1])

        self.assertEqual(second_entry["prev_checksum"], first_entry["checksum"])

    def test_audit_entries_contain_expected_fields(self):
        self.audit.record("V1", "AVAILABLE -> IN_USE", "Rental started")

        with open(self.test_log_path, "r") as f:
            entry = json.loads(f.readline())

        self.assertIn("entity_id", entry)
        self.assertIn("action", entry)
        self.assertIn("reason", entry)
        self.assertIn("prev_checksum", entry)
        self.assertIn("checksum", entry)


if __name__ == "__main__":
    unittest.main()