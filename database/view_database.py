#!/usr/bin/env python3
"""
Script to view all database tables in a nicely formatted output file.
Usage: python view_database.py [output_file.txt]
"""

import os
import sys
import sqlite3
from datetime import datetime

# Database file path
DB_PATH = os.path.join(os.path.dirname(__file__), 'app.db')
OUTPUT_FILE = sys.argv[1] if len(sys.argv) > 1 else 'database_view.txt'

def get_db_connection():
    """Get a database connection."""
    if not os.path.exists(DB_PATH):
        print(f"Error: Database file not found at {DB_PATH}")
        sys.exit(1)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_table_names(conn):
    """Get all table names from the database."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """)
    return [row[0] for row in cursor.fetchall()]

def get_table_info(conn, table_name):
    """Get column information for a table."""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    return cursor.fetchall()

def format_table_output(conn, table_name, output_lines):
    """Format a table's data for output."""
    cursor = conn.cursor()
    
    # Get table info
    table_info = get_table_info(conn, table_name)
    columns = [col[1] for col in table_info]
    
    # Get all rows
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    
    # Header
    output_lines.append(f"\n{'='*80}")
    output_lines.append(f"TABLE: {table_name.upper()}")
    output_lines.append(f"{'='*80}")
    output_lines.append(f"Total rows: {len(rows)}")
    output_lines.append("")
    
    if len(rows) == 0:
        output_lines.append("(No data)")
        output_lines.append("")
        return
    
    # Calculate column widths
    col_widths = {}
    for col in columns:
        col_widths[col] = max(len(col), max([len(str(row[col]) if row[col] is not None else 'NULL') for row in rows], default=0))
    
    # Print header
    header = " | ".join([col.ljust(col_widths[col]) for col in columns])
    output_lines.append(header)
    output_lines.append("-" * len(header))
    
    # Print rows
    for row in rows:
        row_data = []
        for col in columns:
            value = str(row[col]) if row[col] is not None else 'NULL'
            row_data.append(value.ljust(col_widths[col]))
        output_lines.append(" | ".join(row_data))
    
    output_lines.append("")

def main():
    """Main function to generate database view."""
    try:
        conn = get_db_connection()
        table_names = get_table_names(conn)
        
        if not table_names:
            print("No tables found in database.")
            return
        
        output_lines = []
        output_lines.append("="*80)
        output_lines.append("DATABASE VIEW")
        output_lines.append("="*80)
        output_lines.append(f"Database: {DB_PATH}")
        output_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output_lines.append(f"Total tables: {len(table_names)}")
        output_lines.append("")
        
        # Format each table
        for table_name in table_names:
            format_table_output(conn, table_name, output_lines)
        
        # Write to file
        output_content = "\n".join(output_lines)
        with open(OUTPUT_FILE, 'w') as f:
            f.write(output_content)
        
        print(f"Database view saved to: {OUTPUT_FILE}")
        print(f"Total tables exported: {len(table_names)}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

