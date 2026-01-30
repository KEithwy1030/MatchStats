"""Test Football-Data.org API range"""
import asyncio
import aiohttp

async def main():
    with open('.env', 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('FD_API_TOKEN='):
                token = line.split('=', 1)[1].strip()
                break

    headers = {'X-Auth-Token': token}

    async with aiohttp.ClientSession() as session:
        print("=" * 60)
        print("Football-Data.org API - Data Range Test")
        print("=" * 60)

        leagues = [("PL", "Premier League"), ("BL1", "Bundesliga"),
                   ("SA", "Serie A"), ("PD", "La Liga"),
                   ("FL1", "Ligue 1"), ("CL", "Champions League")]

        print("\n[SCHEDULED - Upcoming matches] No limit")
        print("-" * 60)
        total = 0

        for code, name in leagues:
            async with session.get(
                f'https://api.football-data.org/v4/competitions/{code}/matches?status=SCHEDULED',
                headers=headers
            ) as resp:
                data = await resp.json()
                matches = data.get('matches', [])
                count = len(matches)
                total += count

                if count > 0:
                    first = matches[0].get('utcDate', '')[:10]
                    last = matches[-1].get('utcDate', '')[:10]
                    print(f"{name:20} {count:3} matches  {first} ~ {last}")

        print("-" * 60)
        print(f"{'TOTAL':20} {total:3} upcoming matches")
        print("=" * 60)

        print("\n[FINISHED - Past matches] limit=100")
        print("-" * 60)

        async with session.get(
            'https://api.football-data.org/v4/competitions/PL/matches?status=FINISHED&limit=100',
            headers=headers
        ) as resp:
            data = await resp.json()
            matches = data.get('matches', [])
            count = len(matches)

            if count > 0:
                first = matches[0].get('utcDate', '')[:10]  # newest
                last = matches[-1].get('utcDate', '')[:10]  # oldest
                print(f"Premier League: {count} matches")
                print(f"  Time range: {last} ~ {first}")

        print("\n" + "=" * 60)
        print("CONCLUSION:")
        print("=" * 60)
        print("1. SCHEDULED: Returns ALL matches from NOW to END OF SEASON")
        print("2. No need to sync SCHEDULED frequently (rarely changes)")
        print("3. FINISHED: Needs frequent sync for latest results")
        print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
