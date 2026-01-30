"""测试 Football-Data.org API 返回范围"""
import asyncio
import aiohttp
from datetime import datetime

async def main():
    # 读取 API token
    with open('.env', 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('FD_API_TOKEN='):
                token = line.split('=', 1)[1].strip()
                break

    headers = {'X-Auth-Token': token}

    async with aiohttp.ClientSession() as session:
        print("=" * 60)
        print("Football-Data.org API 数据范围测试")
        print("=" * 60)

        # 测试各联赛 SCHEDULED 比赛的完整范围
        leagues = [
            ("PL", "英超"),
            ("BL1", "德甲"),
            ("SA", "意甲"),
            ("PD", "西甲"),
            ("FL1", "法甲"),
            ("CL", "欧冠"),
        ]

        print("\n【SCHEDULED - 即将进行的比赛】（去掉 limit）")
        print("-" * 60)
        total_matches = 0

        for code, name in leagues:
            async with session.get(
                f'https://api.football-data.org/v4/competitions/{code}/matches?status=SCHEDULED',
                headers=headers
            ) as resp:
                data = await resp.json()
                matches = data.get('matches', [])
                count = len(matches)

                if count > 0:
                    first_date = matches[0].get('utcDate', '')
                    last_date = matches[-1].get('utcDate', '')
                    first_match = f"{matches[0].get('homeTeam', {}).get('name')} vs {matches[0].get('awayTeam', {}).get('name')}"
                    last_match = f"{matches[-1].get('homeTeam', {}).get('name')} vs {matches[-1].get('awayTeam', {}).get('name')}"

                    print(f"\n{name} ({code}): {count} 场")
                    print(f"  时间范围: {first_date[:10]} ~ {last_date[:10]}")
                    print(f"  第一场: {first_match}")
                    print(f"  最后一场: {last_match}")

                    total_matches += count
                else:
                    print(f"\n{name} ({code}): 0 场")

        print(f"\n{'='*60}")
        print(f"合计: {total_matches} 场即将进行的比赛")
        print(f"{'='*60}")

        # 对比 FINISHED
        print("\n【FINISHED - 已结束的比赛】（limit=100）")
        print("-" * 60)

        async with session.get(
            'https://api.football-data.org/v4/competitions/PL/matches?status=FINISHED&limit=100',
            headers=headers
        ) as resp:
            data = await resp.json()
            matches = data.get('matches', [])
            count = len(matches)

            if count > 0:
                # FINISHED 返回的是倒序（最新的在前）
                first_date = matches[0].get('utcDate', '')
                last_date = matches[-1].get('utcDate', '')
                print(f"英超已结束比赛: {count} 场")
                print(f"  时间范围: {last_date[:10]} ~ {first_date[:10]}")
                print(f"  最新: {matches[0].get('homeTeam', {}).get('name')} vs {matches[0].get('awayTeam', {}).get('name')} ({first_date[:10]})")
                print(f"  最旧: {matches[-1].get('homeTeam', {}).get('name')} vs {matches[-1].get('awayTeam', {}).get('name')} ({last_date[:10]})")

        print("\n" + "=" * 60)
        print("结论分析:")
        print("=" * 60)
        print("1. SCHEDULED: 返回从今天到本赛季结束的 ALL 比赛赛程")
        print("2. FINISHED: 需要用 limit 控制返回最近的 N 场比赛")
        print("3. SCHEDULED 数据同步一次后，基本不需要频繁更新")
        print("   (除非有比赛时间变更或新增比赛)")
        print("4. FINISHED 需要频繁同步，获取最新比赛结果")

if __name__ == "__main__":
    asyncio.run(main())
