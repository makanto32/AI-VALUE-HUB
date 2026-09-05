#!/usr/bin/env python3
"""Regression tests for an empty production database startup."""

import os
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path


_TEMP_DIRECTORY = tempfile.TemporaryDirectory(prefix="aihub-production-empty-")
_DATABASE_PATH = Path(_TEMP_DIRECTORY.name) / "production.db"
os.environ["AIHUB_DB_PATH"] = str(_DATABASE_PATH)
os.environ["AIHUB_AUTO_SEED_CONTEXT"] = "false"
os.environ["AIHUB_ENABLE_DEMO_SEED"] = "false"

from fastapi import HTTPException
from fastapi.testclient import TestClient

from api.app.main import (
    app,
    delete_demo_sample_idea,
    list_demo_sample_ideas,
    seed_demo_sample_ideas,
)


class ProductionEmptyDatabaseTest(unittest.TestCase):
    @classmethod
    def tearDownClass(cls) -> None:
        _TEMP_DIRECTORY.cleanup()

    def test_startup_leaves_application_tables_empty(self) -> None:
        with TestClient(app):
            pass

        with closing(sqlite3.connect(_DATABASE_PATH)) as connection:
            counts = {
                table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                for table in ("ideas", "company_contexts", "auth_sessions", "context_files")
            }

        self.assertEqual(
            counts,
            {"ideas": 0, "company_contexts": 0, "auth_sessions": 0, "context_files": 0},
        )

    def test_demo_sample_operations_are_disabled(self) -> None:
        operations = (
            lambda: list_demo_sample_ideas(None),
            lambda: seed_demo_sample_ideas(None),
            lambda: delete_demo_sample_idea("demo-sample", None),
        )

        for operation in operations:
            with self.subTest(operation=operation):
                with self.assertRaises(HTTPException) as raised:
                    operation()
                self.assertEqual(raised.exception.status_code, 404)


if __name__ == "__main__":
    unittest.main(verbosity=2)