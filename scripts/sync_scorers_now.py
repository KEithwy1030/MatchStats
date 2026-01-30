
import asyncio
from app.scheduler import SyncScheduler

async def main():
    scheduler = SyncScheduler()
    print("Manually triggering FD scorers sync...")
    count = await scheduler.sync_fd_scorers()
    print(f"Sync completed. Updated {count} scorers.")

if __name__ == "__main__":
    asyncio.run(main())
