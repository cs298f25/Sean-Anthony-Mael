import importlib
import sqlite3
import sys
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def test_env(monkeypatch, tmp_path):
    """Provide a fresh database and reloaded modules for each test."""
    project_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(project_root))
    db_path = tmp_path / "app.db"

    db_module = importlib.import_module("database.database")
    db_module = importlib.reload(db_module)
    monkeypatch.setattr(db_module, "DB_PATH", str(db_path))

    db_services_module = importlib.import_module("database.db_services")
    db_services_module = importlib.reload(db_services_module)

    services_module = importlib.import_module("src.services")
    services_module = importlib.reload(services_module)

    db_module.init_database()

    with db_module.get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("ALTER TABLE questions ADD COLUMN correct_answers INTEGER DEFAULT 0")
        cursor.execute("ALTER TABLE questions ADD COLUMN incorrect_answers INTEGER DEFAULT 0")
        cursor.execute(
            "UPDATE questions SET correct_answers = COALESCE(correct_answers, 0), incorrect_answers = COALESCE(incorrect_answers, 0)"
        )

        cursor.execute("INSERT INTO skill_tests (name, description) VALUES ('Sample Test', 'Sample Description')")
        skill_test_id = cursor.lastrowid

        cursor.execute(
            """
            INSERT INTO questions (skill_test_id, question_type, prompt, answer, category, choices, correct_answers, incorrect_answers)
            VALUES (?, 'multiple_choice', 'Pick A', 'A', 'general', '["A", "B"]', 0, 0)
            """,
            (skill_test_id,),
        )
        first_question_id = cursor.lastrowid

        cursor.execute(
            """
            INSERT INTO questions (skill_test_id, question_type, prompt, answer, category, choices, correct_answers, incorrect_answers)
            VALUES (?, 'text_input', 'Say hi', 'hi', 'general', NULL, 0, 0)
            """,
            (skill_test_id,),
        )
        second_question_id = cursor.lastrowid

        cursor.execute(
            "INSERT INTO study_guides (skill_test_id, content) VALUES (?, 'Guide 1'), (?, 'Guide 2')",
            (skill_test_id, skill_test_id),
        )

        conn.commit()

    yield {
        "db": db_module,
        "db_services": db_services_module,
        "services": services_module,
        "skill_test_id": skill_test_id,
        "question_ids": [first_question_id, second_question_id],
    }
