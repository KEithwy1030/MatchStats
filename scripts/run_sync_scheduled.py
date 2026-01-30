
import asyncio
from app.scheduler import SyncScheduler

async def main():
    scheduler = SyncScheduler()
    print("Starting full FD scheduled/timed sync...")
    await scheduler.sync_fd_scheduled()
    print("Sync complete.")

if __name__ == "__main__":
    asyncio.run(main())
