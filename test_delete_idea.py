#!/usr/bin/env python3
"""Isolated regression test for owner-scoped idea deletion."""

import os
import tempfile
import unittest
from pathlib import Path


_TEMP_DIRECTORY = tempfile.TemporaryDirectory(prefix="aihub-delete-idea-")
os.environ["AIHUB_DB_PATH"] = str(Path(_TEMP_DIRECTORY.name) / "delete.db")
os.environ["AIHUB_AUTH_PROVIDER"] = "demo"

from fastapi.testclient import TestClient

from api.app.main import app


class DeleteIdeaTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app)
        cls.owner_headers = cls._login("analista.finanzas")
        cls.other_headers = cls._login("analista.riesgo")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.client.close()
        _TEMP_DIRECTORY.cleanup()

    @classmethod
    def _login(cls, username: str) -> dict[str, str]:
        response = cls.client.post(
            "/auth/login",
            json={"username": username, "password": "Demo1234!"},
        )
        assert response.status_code == 200, response.text
        return {"Authorization": f"Bearer {response.json()['access_token']}"}

    def test_only_owner_can_delete_idea(self) -> None:
        created = self.client.post(
            "/ideas/intake",
            headers=self.owner_headers,
            json={
                "tenant_id": "contoso-demo",
                "title": "Disposable Regression Idea",
                "problem_statement": "This temporary idea verifies that deletion remains restricted to its owner.",
                "expected_value": "Save USD 10000 annually through automated regression coverage.",
                "affected_users": ["engineering"],
                "source_language": "en",
            },
        )
        self.assertEqual(created.status_code, 200, created.text)
        idea_id = created.json()["idea_id"]

        denied = self.client.delete(f"/ideas/{idea_id}", headers=self.other_headers)
        self.assertEqual(denied.status_code, 403, denied.text)

        deleted = self.client.delete(f"/ideas/{idea_id}", headers=self.owner_headers)
        self.assertEqual(deleted.status_code, 200, deleted.text)

        missing = self.client.get(f"/ideas/{idea_id}", headers=self.owner_headers)
        self.assertEqual(missing.status_code, 404, missing.text)


if __name__ == "__main__":
    unittest.main(verbosity=2)