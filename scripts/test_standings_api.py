"""
测试积分榜API返回格式
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.scrapers import FootballDataScraper

async def main():
    scraper = FootballDataScraper()

    print("=" * 50)
    print("测试英超积分榜API...")
    print("=" * 50)

    data = await scraper.get_standings("PL")

    print(f"返回类型: {type(data)}")
    print(f"返回内容: {data}")
    print()

if __name__ == "__main__":
    asyncio.run(main())
