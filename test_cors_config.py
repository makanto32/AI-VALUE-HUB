#!/usr/bin/env python3
"""Isolated regression tests for configured browser origins."""

import os
import tempfile
import unittest
from pathlib import Path


_TEMP_DIRECTORY = tempfile.TemporaryDirectory(prefix="aihub-cors-")
os.environ["AIHUB_DB_PATH"] = str(Path(_TEMP_DIRECTORY.name) / "cors.db")
os.environ["AIHUB_AUTH_PROVIDER"] = "demo"
os.environ["AIHUB_ALLOWED_ORIGINS"] = "https://app.test.example"

from fastapi.testclient import TestClient

from api.app.main import app


class CorsConfigurationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.client.close()
        _TEMP_DIRECTORY.cleanup()

    def test_configured_origin_is_allowed(self) -> None:
        response = self.client.options(
            "/health",
            headers={
                "Origin": "https://app.test.example",
                "Access-Control-Request-Method": "GET",
            },
        )

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(
            response.headers.get("access-control-allow-origin"),
            "https://app.test.example",
        )

    def test_unconfigured_origin_is_rejected(self) -> None:
        response = self.client.options(
            "/health",
            headers={
                "Origin": "https://untrusted.example",
                "Access-Control-Request-Method": "GET",
            },
        )

        self.assertEqual(response.status_code, 400, response.text)
        self.assertNotIn("access-control-allow-origin", response.headers)


if __name__ == "__main__":
    unittest.main(verbosity=2)