"""
手动同步竞彩数据到 Supabase
"""
import sys
import os
import asyncio
sys.path.append(os.getcwd())

from app.scrapers import SportteryScraper
from app.repositories import SportteryRepository

async def sync_sporttery():
    print("=" * 70)
    print("竞彩数据同步工具")
    print("=" * 70)

    scraper = SportteryScraper()
    repo = SportteryRepository()

    print("\n[1] 调用竞彩官网 API...")
    matches = await scraper.get_matches()

    print(f"获取到 {len(matches)} 场比赛")

    if len(matches) == 0:
        print("[ERROR] 未能获取到任何比赛数据")
        return

    print("\n[2] 保存到 Supabase...")
    saved_count = 0
    failed_count = 0

    for match in matches:
        success = await repo.save_match(match)
        if success:
            saved_count += 1
        else:
            failed_count += 1

    print(f"\n同步完成:")
    print(f"  成功: {saved_count} 场")
    print(f"  失败: {failed_count} 场")

    # 验证数据
    print("\n[3] 验证数据库...")
    db_matches = await repo.get_matches(limit=5)
    print(f"数据库中共有 {len(db_matches)} 场比赛")

    if len(db_matches) > 0:
        print("\n最新的 3 场比赛:")
        for i, match in enumerate(db_matches[:3], 1):
            print(f"\n  {i}. {match.get('league')}")
            print(f"     {match.get('home_team')} vs {match.get('away_team')}")
            print(f"     时间: {match.get('match_time')}")
            print(f"     状态: {match.get('status')}")

    print("\n" + "=" * 70)

if __name__ == "__main__":
    asyncio.run(sync_sporttery())
