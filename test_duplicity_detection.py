#!/usr/bin/env python3
"""Isolated regression test for the active intake duplicate gate."""

import os
import tempfile
import unittest
from pathlib import Path


_TEMP_DIRECTORY = tempfile.TemporaryDirectory(prefix="aihub-duplicate-gate-")
os.environ["AIHUB_DB_PATH"] = str(Path(_TEMP_DIRECTORY.name) / "duplicates.db")
os.environ["AIHUB_AUTH_PROVIDER"] = "demo"

from fastapi.testclient import TestClient

from api.app.main import app


class DuplicateGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app)
        login = cls.client.post(
            "/auth/login",
            json={"username": "analista.finanzas", "password": "Demo1234!"},
        )
        assert login.status_code == 200, login.text
        cls.headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    @classmethod
    def tearDownClass(cls) -> None:
        cls.client.close()
        _TEMP_DIRECTORY.cleanup()

    def test_normalized_title_duplicate_returns_conflict(self) -> None:
        original = {
            "tenant_id": "contoso-demo",
            "title": "Customer Churn Early Warning",
            "problem_statement": "Premium customers leave without enough warning for retention teams to intervene.",
            "expected_value": "Save USD 250000 annually by reducing premium customer churn by 20 percent.",
            "affected_users": ["customer-success"],
            "source_language": "en",
        }
        created = self.client.post("/ideas/intake", json=original, headers=self.headers)
        self.assertEqual(created.status_code, 200, created.text)

        duplicate = dict(original)
        duplicate["title"] = "  CUSTOMER CHURN: EARLY WARNING!  "
        duplicate["problem_statement"] = "Premium customer departures need earlier intervention signals for retention teams."
        conflict = self.client.post("/ideas/intake", json=duplicate, headers=self.headers)

        self.assertEqual(conflict.status_code, 409, conflict.text)
        detail = conflict.json()["detail"]
        self.assertEqual(detail["duplicate_idea"]["idea_id"], created.json()["idea_id"])
        self.assertEqual(detail["duplicate_idea"]["owner_display_name"], "Ana Finanzas")


if __name__ == "__main__":
    unittest.main(verbosity=2)