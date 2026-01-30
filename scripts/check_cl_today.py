
import asyncio
import sqlite3
from app.repositories import FDRepository

async def check():
    repo = FDRepository()
    conn = await repo.get_connection()
    conn.row_factory = sqlite3.Row
    cursor = await conn.cursor()
    
    # Check for matches on Jan 29, 2026 or Jan 28
    await cursor.execute("""
        SELECT m.*, th.name_cn as home_cn, ta.name_cn as away_cn
        FROM fd_matches m
        LEFT JOIN fd_teams th ON m.home_team_id = th.fd_id
        LEFT JOIN fd_teams ta ON m.away_team_id = ta.fd_id
        WHERE m.league_code = 'CL' 
        AND date(m.match_date) >= '2026-01-20'
        ORDER BY m.match_date ASC
    """)
    rows = await cursor.fetchall()
    
    print(f"Found {len(rows)} recent/upcoming CL matches:")
    for m in rows:
        home = m['home_cn'] or m['home_team_name']
        away = m['away_cn'] or m['away_team_name']
        print(f"[{m['status']}] {home} vs {away} @ {m['match_date']}")

if __name__ == "__main__":
    asyncio.run(check())
