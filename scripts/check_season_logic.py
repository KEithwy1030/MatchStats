import asyncio
import os
import sys

# Ensure app can be imported
sys.path.append(os.getcwd())

from app.scrapers import FootballDataScraper

async def check():
    scraper = FootballDataScraper()
    scorers, season_info = await scraper.get_scorers('PL', limit=1)
    print(f"Season Info: {season_info}")
    
    season_year = None
    if season_info and season_info.get('startDate'):
            try:
                season_year = int(season_info.get('startDate').split('-')[0])
            except:
                pass
    print(f"Calculated Season Year: {season_year}")

if __name__ == "__main__":
    asyncio.run(check())
