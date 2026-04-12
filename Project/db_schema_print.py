#!/usr/bin/env python3
"""
Extract and pretty print all table schemas from a Django SQLite database.
Provides context about the database structure for AI or debugging.
Usage: python script.py [path_to_db.sqlite3]
"""

import sqlite3
import sys
from pathlib import Path

def get_table_schemas(db_path):
    """Connect to SQLite DB and return structured schema info for all user tables."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all user tables (exclude internal sqlite_* tables)
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """)
    tables = [row[0] for row in cursor.fetchall()]

    schemas = {}

    for table in tables:
        # Column details
        cursor.execute(f"PRAGMA table_info(`{table}`)")
        columns = cursor.fetchall()  # each row: (cid, name, type, notnull, dflt_value, pk)

        # Foreign keys
        cursor.execute(f"PRAGMA foreign_key_list(`{table}`)")
        foreign_keys = cursor.fetchall()  # each row: (id, seq, table, from, to, on_update, on_delete, match)

        # Indexes
        cursor.execute(f"PRAGMA index_list(`{table}`)")
        indexes = cursor.fetchall()  # each row: (seq, name, unique, origin, partial)
        index_details = []
        for idx in indexes:
            idx_name = idx[1]
            cursor.execute(f"PRAGMA index_info(`{idx_name}`)")
            idx_cols = [row[2] for row in cursor.fetchall()]  # column names
            index_details.append({
                "name": idx_name,
                "unique": bool(idx[2]),
                "columns": idx_cols
            })

        schemas[table] = {
            "columns": columns,
            "foreign_keys": foreign_keys,
            "indexes": index_details
        }

    conn.close()
    return schemas

def pretty_print_schemas(schemas):
    """Format the schema information into a readable, AI‑friendly text block."""
    output_lines = []
    output_lines.append("=" * 80)
    output_lines.append("DATABASE SCHEMA OVERVIEW")
    output_lines.append("=" * 80)

    for table, info in schemas.items():
        output_lines.append(f"\n📁 TABLE: {table}")
        output_lines.append("-" * 60)

        # Columns
        output_lines.append("  COLUMNS:")
        for col in info["columns"]:
            cid, name, col_type, notnull, default, pk = col
            pk_marker = "🔑 PRIMARY KEY" if pk else ""
            nullable = "NOT NULL" if notnull else "NULL"
            default_str = f" DEFAULT {default}" if default is not None else ""
            output_lines.append(f"    - {name} ({col_type}) : {nullable}{default_str} {pk_marker}".strip())

        # Foreign keys
        if info["foreign_keys"]:
            output_lines.append("\n  FOREIGN KEYS:")
            for fk in info["foreign_keys"]:
                # fk: (id, seq, table, from, to, on_update, on_delete, match)
                _, _, ref_table, from_col, to_col, on_update, on_delete, _ = fk
                output_lines.append(f"    - {from_col} → {ref_table}.{to_col}")
                if on_update != "NO ACTION":
                    output_lines.append(f"        ON UPDATE {on_update}")
                if on_delete != "NO ACTION":
                    output_lines.append(f"        ON DELETE {on_delete}")

        # Indexes
        if info["indexes"]:
            output_lines.append("\n  INDEXES:")
            for idx in info["indexes"]:
                unique_str = "UNIQUE " if idx["unique"] else ""
                cols_str = ", ".join(idx["columns"])
                output_lines.append(f"    - {unique_str}INDEX {idx['name']} ON ({cols_str})")

        output_lines.append("")  # blank line between tables

    print("\n".join(output_lines))

def main():
    # Default Django SQLite file name
    # default_db = "db.sqlite3"
    default_db = Path(__file__).parent / "db.sqlite3"
    db_path = sys.argv[1] if len(sys.argv) > 1 else default_db

    if not Path(db_path).exists():
        print(f"Error: Database file '{db_path}' not found.", file=sys.stderr)
        sys.exit(1)

    try:
        schemas = get_table_schemas(db_path)
        if not schemas:
            print("No user tables found in the database.")
            sys.exit(0)
        pretty_print_schemas(schemas)
    except sqlite3.DatabaseError as e:
        print(f"Error reading database: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()