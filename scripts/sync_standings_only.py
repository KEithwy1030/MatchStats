"""
只同步积分榜
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.scheduler import SyncScheduler

async def main():
    scheduler = SyncScheduler()

    print("同步积分榜...")
    count = await scheduler.sync_fd_standings()
    print(f"完成! 同步了 {count} 条积分榜数据")

if __name__ == "__main__":
    asyncio.run(main())