#!/usr/bin/env python3
"""
Initialize the database for the application.
Run this script once to set up the database tables.
"""
import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.database import init_database

if __name__ == '__main__':
    print("Initializing database...")
    init_database()
    print("Database initialized successfully!")

