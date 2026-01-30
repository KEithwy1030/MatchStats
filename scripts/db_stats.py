import sqlite3
import os

db_path = "data/matchstats.db"

def list_tables_and_counts():
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in cursor.fetchall()]

    print(f"{'Table Name':<25} | {'Record Count':<12}")
    print("-" * 40)

    for table in tables:
        try:
            cursor.execute(f"SELECT count(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"{table:<25} | {count:<12}")
        except sqlite3.Error as e:
            print(f"{table:<25} | Error: {e}")

    conn.close()

if __name__ == "__main__":
    list_tables_and_counts()
