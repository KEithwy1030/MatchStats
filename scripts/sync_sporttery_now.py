"""
手动同步竞彩数据到 Supabase
"""
import sys
import os
import asyncio
# 添加项目根目录到环境变量
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
os.chdir(project_root)  # 切换工作目录到项目根目录，方便读取 .env 等文件


from app.scrapers import SportteryScraper
from app.repositories import SportteryRepository

async def sync_sporttery():
    print("=" * 70)
    print("竞彩数据同步工具")
    print("=" * 70)

    scraper = SportteryScraper()
    repo = SportteryRepository()

    print("\n[1] 同步赛程数据 (get_matches)...")
    matches = await scraper.get_matches()
    print(f"获取到 {len(matches)} 场赛程")

    print("\n[2] 同步比分结果 (get_match_results)...")
    results = await scraper.get_match_results()
    print(f"获取到 {len(results)} 场比分记录")

    combined_data = matches + results
    print(f"\n[3] 汇总处理，共计 {len(combined_data)} 条记录保存到 Supabase...")
    
    saved_count = 0
    failed_count = 0

    for item in combined_data:
        success = await repo.save_match(item)
        if success:
            saved_count += 1
        else:
            failed_count += 1

    print(f"\n同步完成:")
    print(f"  成功: {saved_count} 场 (含更新)")
    print(f"  失败: {failed_count} 场")

    # 验证数据
    print("\n[4] 验证数据库比分...")
    
    # 查找最近有比分的 5 场
    import os
    from dotenv import load_dotenv
    from supabase import create_client
    load_dotenv()
    
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    if not url or not key:
        print("[WARN] 环境变量加载失败，跳过验证步骤。")
        return

    s = create_client(url, key)
    res = s.table('sporttery_matches').select('home_team, away_team, match_time, actual_score, status').not_.is_('actual_score', 'null').order('match_time', desc=True).limit(5).execute()
    
    if res.data:
        print("\n最新录入的比分:")
        for i, m in enumerate(res.data, 1):
            print(f"  {i}. [{m['match_time']}] {m['home_team']} {m['actual_score']} {m['away_team']} ({m['status']})")

    print("\n" + "=" * 70)

if __name__ == "__main__":
    asyncio.run(sync_sporttery())
