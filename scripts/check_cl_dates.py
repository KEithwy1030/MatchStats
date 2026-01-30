
import asyncio
from app.repositories import FDRepository
from datetime import datetime, timezone

async def check():
    repo = FDRepository()
    # Get all CL matches to check dates
    conn = await repo.get_connection()
    conn.row_factory = sqlite3.Row if 'sqlite3' in globals() else lambda c, r: dict(zip([col[0] for col in c.description], r))
    import sqlite3
    conn.row_factory = sqlite3.Row
    cursor = await conn.cursor()
    await cursor.execute("SELECT * FROM fd_matches WHERE league_code = 'CL' ORDER BY match_date DESC LIMIT 20")
    rows = await cursor.fetchall()
    
    print("Latest CL matches in DB:")
    for m in rows:
        print(f"[{m['status']}] {m['home_team_name']} vs {m['away_team_name']} @ {m['match_date']}")

if __name__ == "__main__":
    asyncio.run(check())
