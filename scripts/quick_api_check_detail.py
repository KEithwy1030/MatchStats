
import asyncio
import aiohttp
import json
from datetime import datetime, timedelta

async def check():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # 1. Get a matchId from results
    res_url = "https://webapi.sporttery.cn/gateway/uniform/football/getUniformMatchResultV1.qry?pageSize=1&pageNo=1&matchPage=1"
    async with aiohttp.ClientSession() as session:
        async with session.get(res_url, headers=headers) as resp:
            data = await resp.json()
            item = data.get('value', {}).get('matchResult', [])[0]
            match_id = item.get('matchId')
            print(f"Got matchId: {match_id}")

        # 2. Get details
        detail_url = f"https://webapi.sporttery.cn/gateway/lottery/getMatchDetailV1.qry?clientCode=3001&matchId={match_id}"
        async with session.get(detail_url, headers=headers) as resp:
            d = await resp.json()
            if d.get('value'):
                 print("matchTime in detail:", d.get('value').get('matchTime'))
            else:
                 print("No value in detail response")

if __name__ == "__main__":
    asyncio.run(check())
