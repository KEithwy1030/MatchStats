
import asyncio
from app.scrapers import FootballDataScraper

async def main():
    scraper = FootballDataScraper()
    scorers = await scraper.get_scorers("PL", limit=1)
    if scorers:
        print("First scorer data structure:")
        print(scorers[0])
        print("Keys:", scorers[0].keys())
    else:
        print("No scorers found.")

if __name__ == "__main__":
    asyncio.run(main())
