"""
手动触发数据同步脚本
"""
import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.scheduler import SyncScheduler
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """手动同步所有数据"""
    scheduler = SyncScheduler()

    print("=" * 50)
    print("开始手动同步数据...")
    print("=" * 50)

    # 1. 同步联赛信息
    print("\n[1/9] 同步联赛信息...")
    count1 = await scheduler.sync_fd_competitions()
    print(f"联赛信息: {count1} 个")

    # 2. 同步欧洲球队
    print("\n[2/9] 同步欧洲球队数据...")
    count2 = await scheduler.sync_fd_teams()
    print(f"球队数据: {count2} 支")

    # 3. 同步欧洲赛程（SCHEDULED）
    print("\n[3/9] 同步欧洲赛程数据...")
    count3 = await scheduler.sync_fd_scheduled()
    print(f"赛程数据: {count3} 场")

    # 4. 同步比赛结果
    print("\n[4/9] 同步比赛结果...")
    count4 = await scheduler.sync_fd_results()
    print(f"比赛结果: {count4} 场")

    # 5. 同步积分榜
    print("\n[5/9] 同步积分榜数据...")
    count5 = await scheduler.sync_fd_standings()
    print(f"积分榜: {count5} 条")

    # 6. 同步射手榜
    print("\n[6/9] 同步射手榜数据...")
    count6 = await scheduler.sync_fd_scorers()
    print(f"射手榜: {count6} 条")

    # 7. 同步球队详情（教练、阵容）- 耗时较长
    print("\n[7/9] 同步球队详情（教练、阵容）...")
    count7 = await scheduler.sync_fd_team_details()
    print(f"球队详情: {count7} 支")

    # 8. 同步比赛详情（进球、红黄牌等）
    print("\n[8/9] 同步比赛详情...")
    count8 = await scheduler.sync_fd_live_match_details()
    print(f"比赛详情: {count8} 场")

    # 9. 同步竞彩数据
    print("\n[9/9] 同步竞彩比赛数据...")
    count9 = await scheduler.sync_sporttery_matches()
    print(f"竞彩数据: {count9} 场")

    print("\n" + "=" * 50)
    print("同步完成！")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
