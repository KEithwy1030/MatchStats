
import sqlite3
import os
import sys
import asyncio
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime

# Load environment variables
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
DB_PATH = os.getenv("DB_PATH", "./data/matchstats.db")

async def migrate():
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Supabase environment variables not set.")
        return

    # Initialize Supabase client
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Connect to local SQLite
    if not os.path.exists(DB_PATH):
        print(f"❌ Local database not found at {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    tables = [
        "fd_matches", 
        "fd_teams", 
        "fd_standings", 
        "fd_scorers", 
        "sporttery_matches", 
        "sync_logs"
    ]

    print(f"🚀 Starting migration from {DB_PATH} to Supabase...")

    for table_name in tables:
        print(f"\nProcessing table: {table_name}...")
        try:
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            if not rows:
                print(f"  - No data found in {table_name}. Skipping.")
                continue

            # Convert rows to list of dicts
            data = [dict(row) for row in rows]
            
            # Remove local auto-increment 'id' if exists to let Supabase handle it
            # Unless we want to keep it. For fd_id based tables, we usually rely on fd_id.
            # Local sync_logs has an 'id' that we might want to keep or skip.
            for item in data:
                if 'id' in item:
                    del item['id']

            # Supabase upsert in chunks to avoid size limits
            chunk_size = 100
            for i in range(0, len(data), chunk_size):
                chunk = data[i:i + chunk_size]
                supabase.table(table_name).upsert(chunk).execute()
                print(f"  - Uploaded {min(i + chunk_size, len(data))}/{len(data)} rows.")

            print(f"✅ Table {table_name} migrated successfully.")
        except Exception as e:
            print(f"❌ Error migrating {table_name}: {e}")

    conn.close()
    print("\n" + "="*50)
    print("🎉 All data migration completed!")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(migrate())
