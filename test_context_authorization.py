#!/usr/bin/env python3
"""Isolated regression tests for tenant context authorization."""

import os
import tempfile
import unittest
from pathlib import Path


_TEMP_DIRECTORY = tempfile.TemporaryDirectory(prefix="aihub-context-auth-")
os.environ["AIHUB_DB_PATH"] = str(Path(_TEMP_DIRECTORY.name) / "context.db")
os.environ["AIHUB_AUTH_PROVIDER"] = "demo"

from fastapi.testclient import TestClient

from api.app.main import app


class ContextAuthorizationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app)
        cls.analyst_headers = cls._login("analista.finanzas")
        cls.admin_headers = cls._login("admin.valuehub")

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

    def test_context_read_requires_authentication(self) -> None:
        response = self.client.get("/context/contoso-demo")
        self.assertEqual(response.status_code, 401, response.text)

    def test_authenticated_tenant_user_can_read_context(self) -> None:
        response = self.client.get(
            "/context/contoso-demo",
            headers=self.analyst_headers,
        )
        self.assertEqual(response.status_code, 200, response.text)

    def test_context_write_requires_admin(self) -> None:
        response = self.client.put(
            "/context/contoso-demo",
            headers=self.analyst_headers,
            json={
                "company_name": "Contoso Financial Services",
                "industry": "Financial services",
                "strategic_priorities": ["Operational efficiency"],
                "prohibited_domains": [],
                "regulatory_constraints": ["KYC"],
                "operating_model_summary": "Regulated retail banking.",
                "risk_tolerance": "low",
            },
        )
        self.assertEqual(response.status_code, 403, response.text)


if __name__ == "__main__":
    unittest.main(verbosity=2)