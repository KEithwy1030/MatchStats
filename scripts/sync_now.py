
import asyncio
import sys
import os
import argparse

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.scheduler import SyncScheduler
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    parser.add_argument("--mode", choices=["fast", "full", "live_only"], default="full", help="Sync mode: fast (results), live_only (in-play), or full (everything)")
    args = parser.parse_args()

    scheduler = SyncScheduler()

    print("=" * 50)
    print(f"开始同步数据 (模式: {args.mode.upper()})...")
    print("=" * 50)

    if args.mode == "live_only":
        # ⭐ 超高频模式：每5分钟运行
        # 仅消耗 1 次 API 调用，极其安全
        print("\n[1/1] 同步实时比分 (LIVE)...")
        count = await scheduler.sync_fd_live_scores()
        print(f"实时比分同步完成: {count} 场")

    elif args.mode == "fast":
        # 快速同步：每30-60分钟运行
        # 消耗约 7 次 API 调用
        print("\n[1/3] 同步最近比赛结果...")
        await scheduler.sync_fd_results()
        
        print("\n[2/3] 同步竞彩数据...")
        await scheduler.sync_sporttery_matches()
        
        # 顺便也更新一下实时比分
        await scheduler.sync_fd_live_scores()

    else:
        # 深度同步：全量更新
        # 注意：为了遵守 API 频率限制，这里会比较慢
        print("\n[1/8] 同步联赛信息...")
        await scheduler.sync_fd_competitions()
        
        print("\n[2/8] 同步球队基础数据...")
        await scheduler.sync_fd_teams()
        
        print("\n[3/8] 同步完整赛程数据...")
        await scheduler.sync_fd_scheduled()
        
        print("\n[4/8] 同步历史结果...")
        await scheduler.sync_fd_results()
        
        print("\n[5/8] 同步积分榜...")
        await scheduler.sync_fd_standings()
        
        print("\n[6/8] 同步射手榜...")
        await scheduler.sync_fd_scorers()
        
        print("\n[7/8] 同步竞彩数据...")
        await scheduler.sync_sporttery_matches()
        
        print("\n[8/8] 同步进行中比赛细节(进球/红牌)...")
        await scheduler.sync_fd_live_match_details()

    print("\n" + "=" * 50)
    print("同步完成！")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
