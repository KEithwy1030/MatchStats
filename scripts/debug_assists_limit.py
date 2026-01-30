
import asyncio
from app.scrapers import FootballDataScraper

async def main():
    scraper = FootballDataScraper()
    print("Fetching top 100 scorers for PL...")
    scorers = await scraper.get_scorers("PL", limit=100)
    
    if not scorers:
        print("No scorers found.")
        return

    # Handle None values
    by_assists = sorted(scorers, key=lambda x: x.get('assists') if x.get('assists') is not None else 0, reverse=True)
    
    print("\nTop 10 by Assists (within top 100 goalscorers):")
    for i, s in enumerate(by_assists[:20]):
        player = s.get('player', {}).get('name')
        assists = s.get('assists', 0)
        goals = s.get('goals', 0)
        print(f"{i+1}. {player}: {assists} Assists, {goals} Goals")

if __name__ == "__main__":
    asyncio.run(main())
