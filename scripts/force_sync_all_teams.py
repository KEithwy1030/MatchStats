
import asyncio
import sys
from app.scheduler import SyncScheduler
from app.repositories import FDRepository

# Fix encoding
sys.stdout.reconfigure(encoding='utf-8')

async def force_sync_teams():
    print("Starting Force Sync for Teams and Logos...")
    scheduler = SyncScheduler()
    
    # 1. First get all active competitions
    comps = await scheduler.fd_scraper.get_competitions()
    print(f"Found {len(comps)} available competitions.")
    
    # 2. For each competition, fetch teams and save them
    # We focus on the big leagues + CL first
    target_leagues = ['CL', 'PL', 'PD', 'SA', 'BL1', 'FL1'] 
    
    for comp in comps:
        code = comp.get('code')
        if code in target_leagues or True: # Sync ALL available in Free Tier (12 total)
            print(f"Syncing teams for {comp.get('name')} ({code})...")
            teams = await scheduler.fd_scraper.get_teams(code)
            
            count = 0
            for team in teams:
                # Direct save to repo
                await scheduler.fd_repo.save_team(team)
                count += 1
            print(f"  -> Saved {count} teams from {code}.")
            
            # Respect rate limit
            await asyncio.sleep(6)

    print("Force Sync Complete!")

if __name__ == "__main__":
    asyncio.run(force_sync_teams())
