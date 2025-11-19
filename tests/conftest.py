"""
This file is special - pytest automatically finds and uses it.
It's where we set up test fixtures (reusable test setup).
"""

import pytest
import os
import sys
from pathlib import Path

# Add parent directory to path (same as app.py does)
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import database
from database.database import init_database

# Path for our test database
TEST_DB_PATH = os.path.join(os.path.dirname(__file__), 'test_app.db')

@pytest.fixture
def test_db(monkeypatch):
    """
    This fixture creates a fresh test database before each test
    and cleans it up after the test is done.
    
    It temporarily changes where the database functions look for the database file.
    """
    # Remove test database if it exists (cleanup from previous test)
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    
    # Temporarily change the database path to our test database
    # This makes all database operations use the test database instead
    monkeypatch.setattr(database, 'DB_PATH', TEST_DB_PATH)
    
    # Initialize the test database with all tables
    init_database()
    
    yield TEST_DB_PATH  # This gives the test the database path
    
    # Clean up after test - remove the test database
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

