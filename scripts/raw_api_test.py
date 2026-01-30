
import asyncio
import aiohttp
import os
import sys

# Load env manually or rely on default
from app.config import settings

sys.stdout.reconfigure(encoding='utf-8')

async def check_api_raw():
    token = settings.FD_API_TOKEN
    if not token:
        print("Error: FD_API_TOKEN not found in settings")
        return

    headers = {
        "X-Auth-Token": token
    }
    
    # Target: A specific active match (using the ID from previous logs: 551980 Arsenal vs Kairat)
    # If that match is over, it's fine, we just want to check fields.
    match_id = 551980 
    url = f"https://api.football-data.org/v4/matches/{match_id}"

    print(f"Requesting: {url}")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            print(f"Status Code: {resp.status}")
            
            # Print Rate Limit Headers
            print("\n--- Rate Limit Headers ---")
            for k, v in resp.headers.items():
                if 'request' in k.lower() or 'limit' in k.lower():
                    print(f"{k}: {v}")
            
            if resp.status == 200:
                data = await resp.json()
                print("\n--- Data Structure Analysis ---")
                
                # Check root keys
                print("Root Keys:", list(data.keys()))
                
                # Check specifics
                home_team = data.get('homeTeam', {})
                print(f"\nHome Team Keys: {list(home_team.keys())}")
                if 'lineup' in home_team:
                    print(f"Home Lineup Length: {len(home_team['lineup'])}")
                else:
                    print("Home Lineup Field: MISSING")
                    
                match_status = data.get('status')
                print(f"Match Status: {match_status}")
                
                goals = data.get('goals', [])
                print(f"Goals Field: {goals} (Type: {type(goals)})")
    
            elif resp.status == 429:
                print("Hit Rate Limit!")
            else:
                print(f"Error Body: {await resp.text()}")

if __name__ == "__main__":
    asyncio.run(check_api_raw())
