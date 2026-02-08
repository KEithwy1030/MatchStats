
import asyncio
import argparse
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.scheduler import scheduler

async def main():
    parser = argparse.ArgumentParser(description="Unified synchronization script for MatchStats")
    parser.add_argument("--mode", choices=["live_only", "full", "results"], default="full", help="Sync mode")
    args = parser.parse_args()

    if args.mode == "live_only":
        print("Starting LIVE Score Sync...")
        count = await scheduler.sync_fd_live_scores()
        print(f"Live Score Sync Finished. Matches updated: {count}")
    
    elif args.mode == "results":
        print("Starting FD Results Sync...")
        count = await scheduler.sync_fd_results()
        print(f"Results Sync Finished. Records updated: {count}")

    elif args.mode == "full":
        print("Starting FULL Synchronization (Calendar, Results, Standings, Scorers)...")
        
        print("[1/4] Syncing Scheduled matches...")
        await scheduler.sync_fd_scheduled()
        
        print("[2/4] Syncing Match results...")
        await scheduler.sync_fd_results()
        
        print("[3/4] Syncing Standings...")
        await scheduler.sync_fd_standings()
        
        print("[4/4] Syncing Scorers...")
        await scheduler.sync_fd_scorers()
        
        print("Full Sync Complete.")

if __name__ == "__main__":
    asyncio.run(main())
