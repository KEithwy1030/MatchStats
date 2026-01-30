
import asyncio
from app.scheduler import SyncScheduler
from app.scrapers import FootballDataScraper
from app.repositories import FDRepository

async def sync_cl():
    scheduler = SyncScheduler()
    print("Syncing CL scheduled matches...")
    # Directly pull from scraper to check what's available
    scraper = FootballDataScraper()
    matches = await scraper.get_matches(competition="CL", status="SCHEDULED")
    print(f"Scraper found {len(matches)} scheduled matches for CL")
    
    repo = FDRepository()
    for m in matches:
        print(f"Saving: {m.get('utcDate')} - {m.get('homeTeam', {}).get('name')} vs {m.get('awayTeam', {}).get('name')}")
        await repo.save_match({
            'fd_id': m.get('id'),
            'league_code': 'CL',
            'home_team_id': m.get('homeTeam', {}).get('id'),
            'away_team_id': m.get('awayTeam', {}).get('id'),
            'home_team_name': m.get('homeTeam', {}).get('name'),
            'away_team_name': m.get('awayTeam', {}).get('name'),
            'match_date': m.get('utcDate'),
            'status': m.get('status'),
            'home_score': None,
            'away_score': None,
            'home_half_score': None,
            'away_half_score': None,
            'referee': None,
            'attendance': None,
            'matchday': m.get('matchday'),
            'season': m.get('season', {}).get('id') if isinstance(m.get('season'), dict) else m.get('season')
        })
    print("Done.")

if __name__ == "__main__":
    asyncio.run(sync_cl())
