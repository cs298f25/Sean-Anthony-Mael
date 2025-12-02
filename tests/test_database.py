import sqlite3

import pytest


def test_validate_username_and_hashing(test_env):
    db = test_env["db"]

    assert db.validate_username("  alice ") == "alice"
    with pytest.raises(ValueError):
        db.validate_username("")

    password_hash = db.hash_password("secret")
    assert ":" in password_hash
    assert db.verify_password("secret", password_hash)
    assert not db.verify_password("wrong", password_hash)
    assert db.constant_time_compare(b"bytes", b"bytes")
    assert not db.constant_time_compare(b"a", b"bb")


def test_create_get_and_login_user_paths(test_env):
    db = test_env["db"]

    user_id = db.create_user("tester", "pass123")
    stored_user = db.get_user("tester")
    assert stored_user["id"] == user_id
    assert db.login_user("tester", "pass123")["id"] == user_id
    assert db.login_user("tester", "wrong") is None

    legacy_user_id = db.create_user("legacy_user")
    legacy_user = db.login_user("legacy_user", "newpass")
    assert legacy_user["id"] == legacy_user_id
    assert db.get_user("legacy_user")["password_hash"]

    with pytest.raises(ValueError):
        db.login_user("tester", "")


def test_schema_helpers_add_missing_columns(test_env):
    db = test_env["db"]
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT)")
    db.ensure_password_column(cursor)
    cursor.execute("PRAGMA table_info(users)")
    user_columns = [row[1] for row in cursor.fetchall()]
    assert "password_hash" in user_columns

    cursor.execute(
        "CREATE TABLE questions (id INTEGER PRIMARY KEY, question_type TEXT, prompt TEXT, answer TEXT, category TEXT)"
    )
    cursor.execute("INSERT INTO questions (question_type, prompt, answer, category) VALUES (NULL, 'p', 'a', 'c')")
    db.ensure_choices_column(cursor)
    cursor.execute("PRAGMA table_info(questions)")
    question_columns = [row[1] for row in cursor.fetchall()]
    assert "choices" in question_columns
    cursor.execute("SELECT question_type FROM questions")
    assert cursor.fetchone()[0] == "text_input"


def test_read_sql_file_supports_absolute_paths(test_env, tmp_path):
    db = test_env["db"]
    sql_file = tmp_path / "sample.sql"
    sql_file.write_text("SELECT 1;")
    assert db.read_sql_file(str(sql_file)) == "SELECT 1;"


def test_get_db_connection_uses_patched_path(test_env):
    db = test_env["db"]
    with db.get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}
    assert "users" in tables
    assert str(db.DB_PATH).endswith("app.db")
