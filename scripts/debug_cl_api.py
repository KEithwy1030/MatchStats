
import asyncio
from app.scrapers import FootballDataScraper

async def check():
    scraper = FootballDataScraper()
    # Get all matches for CL to see what's happening today
    data = await scraper._get("/competitions/CL/matches")
    matches = data.get('matches', [])
    print(f"Total matches in CL response: {len(matches)}")
    
    import datetime
    today = datetime.datetime.now(datetime.timezone.utc).date()
    # Also check tomorrow just in case
    
    print(f"Searching for matches near {today}...")
    for m in matches:
        m_date = datetime.datetime.fromisoformat(m['utcDate'].replace('Z', '+00:00')).date()
        if m_date == today:
             print(f"[{m['status']}] {m.get('homeTeam', {}).get('name')} vs {m.get('awayTeam', {}).get('name')} @ {m['utcDate']}")

if __name__ == "__main__":
    asyncio.run(check())
