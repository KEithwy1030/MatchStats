
import asyncio
from app.repositories import FDRepository
from datetime import datetime, timezone

async def check():
    repo = FDRepository()
    matches = await repo.get_matches(league='CL', limit=20)
    print(f"Total CL matches found: {len(matches)}")
    now = datetime.now(timezone.utc)
    print(f"Current UTC time: {now}")
    
    for m in matches:
        print(f"[{m['status']}] {m['home_team_name']} vs {m['away_team_name']} @ {m['match_date']}")

if __name__ == "__main__":
    asyncio.run(check())
