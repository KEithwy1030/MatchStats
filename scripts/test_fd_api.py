"""测试 Football-Data.org API"""
import asyncio
import aiohttp

async def main():
    # 读取 API token
    with open('.env', 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('FD_API_TOKEN='):
                token = line.split('=', 1)[1].strip()
                break

    headers = {'X-Auth-Token': token}

    async with aiohttp.ClientSession() as session:
        print("=" * 50)
        print("测试 Football-Data.org API")
        print("=" * 50)

        # 1. 测试英超 SCHEDULED 比赛数
        print("\n1. 英超 即将进行的比赛 (不设置 limit):")
        async with session.get(
            'https://api.football-data.org/v4/competitions/PL/matches?status=SCHEDULED',
            headers=headers
        ) as resp:
            data = await resp.json()
            matches = data.get('matches', [])
            print(f"   返回比赛数: {len(matches)}")
            if matches:
                print(f"   最早: {matches[0].get('utcDate', '')[:10]}")
                print(f"   最晚: {matches[-1].get('utcDate', '')[:10]}")

        # 2. 测试英超 FINISHED 比赛数
        print("\n2. 英超 已结束的比赛 (limit=50):")
        async with session.get(
            'https://api.football-data.org/v4/competitions/PL/matches?status=FINISHED&limit=50',
            headers=headers
        ) as resp:
            data = await resp.json()
            matches = data.get('matches', [])
            print(f"   返回比赛数: {len(matches)}")
            if matches:
                print(f"   最早: {matches[-1].get('utcDate', '')[:10]}")
                print(f"   最晚: {matches[0].get('utcDate', '')[:10]}")

        # 3. 测试所有联赛的比赛数
        leagues = ["PL", "BL1", "SA", "PD", "FL1", "CL"]
        total = 0
        print("\n3. 各联赛 SCHEDULED 比赛数:")
        for league in leagues:
            async with session.get(
                f'https://api.football-data.org/v4/competitions/{league}/matches?status=SCHEDULED',
                headers=headers
            ) as resp:
                data = await resp.json()
                count = len(data.get('matches', []))
                total += count
                league_names = {"PL": "英超", "BL1": "德甲", "SA": "意甲", "PD": "西甲", "FL1": "法甲", "CL": "欧冠"}
                print(f"   {league_names[league]}: {count} 场")
        print(f"   合计: {total} 场")

if __name__ == "__main__":
    asyncio.run(main())
