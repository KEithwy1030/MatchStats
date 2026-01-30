
import asyncio
import json
from app.scrapers import FootballDataScraper

async def test_live_data():
    scraper = FootballDataScraper()
    
    # 1. Find a live match (or recent one if no live)
    print("Searching for LIVE/IN_PLAY matches...")
    matches = await scraper.get_matches(status="LIVE")
    if not matches:
        matches = await scraper.get_matches(status="IN_PLAY")
    
    target_id = None
    target_match = None
    
    if matches:
        target_match = matches[0]
        target_id = target_match['id']
        print(f"Found LIVE match: {target_match['homeTeam']['name']} vs {target_match['awayTeam']['name']} (ID: {target_id})")
    else:
        print("No LIVE matches found, falling back to recent FINISHED match for structure check...")
        matches = await scraper.get_matches(status="FINISHED", limit=1)
        if matches:
            target_match = matches[0]
            target_id = target_match['id']
            print(f"Found FINISHED match: {target_match['homeTeam']['name']} vs {target_match['awayTeam']['name']} (ID: {target_id})")
    
    if not target_id:
        print("No matches found to test.")
        return

    # 2. Fetch specific match details
    print(f"\nFetching details for match ID: {target_id}...")
    details = await scraper.get_match(target_id)
    
    if not details:
        print("Failed to fetch details.")
        return

    # 3. Analyze available data fields
    print("-" * 50)
    print("Available Data Analysis:")
    
    # Score
    score = details.get('score', {})
    print(f"Score: {score.get('fullTime')} (Half: {score.get('halfTime')})")
    
    # Goals
    goals = details.get('goals', [])
    print(f"Goals: {len(goals)} events found")
    if goals:
        print("Sample Goal:", json.dumps(goals[0], indent=2, ensure_ascii=False))
        
    # Lineups (Home)
    home_team = details.get('homeTeam', {})
    home_lineup = home_team.get('lineup', [])
    home_bench = home_team.get('bench', [])
    print(f"Home Team Lineup: {len(home_lineup)} players")
    print(f"Home Team Bench: {len(home_bench)} players")
    if home_lineup:
        print("Sample Starter:", json.dumps(home_lineup[0], indent=2, ensure_ascii=False))
        
    # Lineups (Away)
    away_team = details.get('awayTeam', {})
    away_lineup = away_team.get('lineup', [])
    print(f"Away Team Lineup: {len(away_lineup)} players")
    
    # Referees
    referees = details.get('referees', [])
    print(f"Referees: {len(referees)}")
    if referees:
        print("Referees List:", [r['name'] for r in referees])
        
    # Print distinct keys in root
    print("\nRoot Keys present:", list(details.keys()))

    print("-" * 50)
    print("Raw JSON (truncated):")
    print(json.dumps(details, indent=2, ensure_ascii=False)[:1000] + "...")

if __name__ == "__main__":
    asyncio.run(test_live_data())
