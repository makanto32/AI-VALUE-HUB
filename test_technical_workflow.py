#!/usr/bin/env python3
"""Isolated regression test for the current technical approval workflow."""

import os
import tempfile
import unittest
from pathlib import Path


_TEMP_DIRECTORY = tempfile.TemporaryDirectory(prefix="aihub-technical-workflow-")
os.environ["AIHUB_DB_PATH"] = str(Path(_TEMP_DIRECTORY.name) / "workflow.db")
os.environ["AIHUB_LOCAL_BLOB_ROOT"] = str(Path(_TEMP_DIRECTORY.name) / "blob")
os.environ["AIHUB_AUTH_PROVIDER"] = "demo"

from fastapi.testclient import TestClient

from api.app.main import app


class TechnicalWorkflowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app)
        cls.analyst_headers = cls._login("analista.finanzas", "Demo1234!")
        cls.technical_headers = cls._login("analista.tecnologia", "Demo1234!")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.client.close()
        _TEMP_DIRECTORY.cleanup()

    @classmethod
    def _login(cls, username: str, password: str) -> dict[str, str]:
        response = cls.client.post(
            "/auth/login",
            json={"username": username, "password": password},
        )
        assert response.status_code == 200, response.text
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def test_technical_approval_and_economic_gate(self) -> None:
        denied = self.client.get("/ideas/technical-queue", headers=self.analyst_headers)
        self.assertEqual(denied.status_code, 403)

        seeded = self.client.post("/ideas/demo-samples/seed", headers=self.analyst_headers)
        self.assertEqual(seeded.status_code, 200, seeded.text)
        self.assertEqual(len(seeded.json()), 7)

        queue_response = self.client.get("/ideas/technical-queue", headers=self.technical_headers)
        self.assertEqual(queue_response.status_code, 200, queue_response.text)
        queue = queue_response.json()
        self.assertEqual(len(queue), 7)
        self.assertIn("idea", queue[0])
        self.assertIn("value_economics", queue[0])

        queued_idea = queue[0]["idea"]
        self.assertTrue(queued_idea["agent_approved"])
        self.assertTrue(queued_idea["technical_interactions"])
        idea_id = queued_idea["idea_id"]

        approval = self.client.post(
            f"/ideas/{idea_id}/technical-approval",
            headers=self.technical_headers,
        )
        self.assertEqual(approval.status_code, 200, approval.text)
        approved_idea = approval.json()
        self.assertTrue(approved_idea["human_approved"])
        self.assertIsNotNone(approved_idea["architecture_package"])

        pdf_response = self.client.get(
            f"/ideas/{idea_id}/architecture-package-pdf",
            headers=self.technical_headers,
        )
        self.assertEqual(pdf_response.status_code, 200, pdf_response.text)
        self.assertEqual(pdf_response.headers["content-type"], "application/pdf")
        self.assertTrue(pdf_response.content.startswith(b"%PDF"))

        blocked = self.client.patch(
            f"/ideas/{idea_id}/move-to-funding",
            headers=self.technical_headers,
        )
        self.assertEqual(blocked.status_code, 409, blocked.text)

        overridden = self.client.patch(
            f"/ideas/{idea_id}/move-to-funding",
            params={"override_economics": "true"},
            headers=self.technical_headers,
        )
        self.assertEqual(overridden.status_code, 200, overridden.text)
        self.assertEqual(overridden.json()["deployment_status"], "funding")


if __name__ == "__main__":
    unittest.main(verbosity=2)
