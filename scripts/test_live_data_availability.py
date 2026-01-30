
import asyncio
import json
import sys
from app.scrapers import FootballDataScraper

# Fix encoding
sys.stdout.reconfigure(encoding='utf-8')

async def test_live_data():
    scraper = FootballDataScraper()
    
    # 1. Find a live match (or recent one if no live)
    print("Searching for LIVE/IN_PLAY matches...")
    matches = await scraper.get_matches(status="LIVE")
    if not matches:
        matches = await scraper.get_matches(status="IN_PLAY")
    
    target_id = None
    
    if matches:
        target_match = matches[0]
        target_id = target_match['id']
        try:
            print(f"Found LIVE match: {target_match['homeTeam']['name']} vs {target_match['awayTeam']['name']} (ID: {target_id})")
        except:
            print(f"Found LIVE match ID: {target_id}")
    else:
        print("No LIVE matches found. Cannot test live data.")
        return

    # 2. Fetch specific match details
    print(f"\nFetching ALL details for match ID: {target_id}...")
    details = await scraper.get_match(target_id)
    
    if not details:
        print("Failed to fetch details.")
        return

    # 3. Analyze available data fields STRICTLY
    print("=" * 50)
    print("DATA AVAILABILITY REPORT")
    print("=" * 50)
    
    home_team = details.get('homeTeam', {})
    away_team = details.get('awayTeam', {})
    
    # Check Lineups
    has_home_lineup = 'lineup' in home_team and len(home_team['lineup']) > 0
    has_away_lineup = 'lineup' in away_team and len(away_team['lineup']) > 0
    
    print(f"Home Lineup Available: {has_home_lineup}")
    if not has_home_lineup:
        print("  - Keys in homeTeam:", list(home_team.keys()))

    print(f"Away Lineup Available: {has_away_lineup}")
    
    # Check Coach
    print(f"Home Coach Available: {'coach' in home_team}")
    print(f"Away Coach Available: {'coach' in away_team}")

    # Check Goals
    goals = details.get('goals', [])
    print(f"Goals Available: {True if goals else False} (Count: {len(goals)})")
    
    # Check Referees
    referees = details.get('referees', [])
    print(f"Referees Available: {True if referees else False}")
    
    # Check Venue
    print(f"Venue Available: {details.get('venue')}")
    
    # Check Score
    print(f"Score Available: {details.get('score')}")

    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test_live_data())
