import asyncio
import os
import sys

# Ensure app can be imported
sys.path.append(os.getcwd())

from app.scrapers import FootballDataScraper
from app.repositories import FDRepository
from app.config import settings

async def fix_all_seasons():
    scraper = FootballDataScraper()
    repo = FDRepository()
    
    print("Fetching season IDs for all leagues...")
    
    # We need to manually access the monitored leagues. 
    # settings.monitored_leagues_list is a property splitting the string.
    leagues = settings.monitored_leagues_list
    
    for league in leagues:
        print(f"Processing {league}...")
        try:
            # We use get_standings to get season info quickly
            # Note: The raw scraper method returns (data, season_info) now
            _, season_info = await scraper.get_standings(league)
            
            season_id = season_info.get('id')
            if not season_id:
                print(f"  Warning: No season ID found for {league}")
                continue
                
            print(f"  Season ID: {season_id}")
            
            # Update Scorers
            res = repo.client.table('fd_scorers').update({'season': season_id}).eq('league_code', league).execute()
            print(f"  Updated scorers: {len(res.data) if res.data else 0}")
            
            # Update Standings
            res = repo.client.table('fd_standings').update({'season': season_id}).eq('league_code', league).execute()
            print(f"  Updated standings: {len(res.data) if res.data else 0}")
            
             # Update Matches (Optional, they usually have it)
            res = repo.client.table('fd_matches').update({'season': season_id}).eq('league_code', league).is_('season', 'null').execute()
            print(f"  Updated matches (empty ones): {len(res.data) if res.data else 0}")

        except Exception as e:
            print(f"  Error processing {league}: {e}")

if __name__ == "__main__":
    asyncio.run(fix_all_seasons())
