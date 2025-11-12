#!/usr/bin/env python3
"""
Simple script to view the contents of the database.
Usage: python view_database.py
"""

import sqlite3
import os
from pathlib import Path

# Database path - now in the same directory as the script
DB_PATH = os.path.join(Path(__file__).parent, 'app.db')

def print_table(conn, table_name):
    """Print all rows from a table."""
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        if not rows:
            print(f"\n{table_name}: (empty)")
            return
        
        # Get column names
        columns = [description[0] for description in cursor.description]
        
        print(f"\n{'='*80}")
        print(f"Table: {table_name} ({len(rows)} rows)")
        print('='*80)
        
        # Print column headers
        header = " | ".join(f"{col:20}" for col in columns)
        print(header)
        print("-" * len(header))
        
        # Print rows
        for row in rows:
            row_str = " | ".join(f"{str(val):20}" for val in row)
            print(row_str)
            
    except sqlite3.Error as e:
        print(f"Error reading table {table_name}: {e}")

def main():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at: {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    # Get all table names
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    
    if not tables:
        print("No tables found in database.")
        return
    
    print(f"\nDatabase: {DB_PATH}")
    print(f"Tables: {', '.join(tables)}\n")
    
    # Print each table
    for table in tables:
        print_table(conn, table)
    
    conn.close()
    print(f"\n{'='*80}")
    print("Done!")

if __name__ == "__main__":
    main()

