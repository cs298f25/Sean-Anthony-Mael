#!/usr/bin/env python3
"""
Initialize the database for the application.
Run this script once to set up the database tables.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database.database import init_database

if __name__ == '__main__':
    print("Initializing database...")
    init_database()
    print("Database initialized successfully!")