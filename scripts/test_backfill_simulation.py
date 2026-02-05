
import asyncio
import logging
import sys
import os

# 增加项目根目录到路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.scrapers import SportteryScraper
from app.repositories import SportteryRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def simulate_backfill():
    print("--- 启动比分回填模拟测试 ---")
    scraper = SportteryScraper()
    repo = SportteryRepository()
    
    # 1. 第一步：抓取官网比分结果
    print("步骤1: 正在从官网拉取最新比分...")
    results = await scraper.get_match_results()
    print(f"官网数据：共拉取到 {len(results)} 场比赛结果")
    
    # 2. 第二步：回填到数据库
    print("步骤2: 正在将比分填入数据库...")
    success_count = 0
    for res in results:
        success = await repo.update_match_score(
            res['match_code'],
            res['home_team'],
            res['away_team'],
            res['actual_score'],
            res['half_score']
        )
        if success:
            # 只有当数据库里确实有这场比赛时，Supabase的update才会有返回值(通过maybe_single判断)
            # 但仓库里的update_match_score目前没检查是否真的更新了行数，我稍微改下逻辑手动验证
            success_count += 1
            
    print(f"回填完成！尝试执行了 {success_count} 条更新指令。")
    
    # 3. 第三步：验证结果
    print("\n--- 验证当前数据库状态 ---")
    # 再次查询数据库，看看是不是真的有比分了
    from app.config import settings
    from supabase import create_client
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    
    res = supabase.table('sporttery_matches').select('match_code, home_team, away_team, actual_score, status').execute()
    matches = res.data
    
    filled = [m for m in matches if m['actual_score'] is not None]
    print(f"数据库统计：当前库内总比赛 {len(matches)} 场，其中已回填比分 {len(filled)} 场。")
    
    if filled:
        print("\n抽样比分检查:")
        for m in filled[:5]:
            print(f"[{m['match_code']}] {m['home_team']} {m['actual_score']} {m['away_team']} ({m['status']})")
    else:
        print("警告：没有发现被填充的比分！可能是官网返回的比赛在库中不存在。")

if __name__ == "__main__":
    asyncio.run(simulate_backfill())
