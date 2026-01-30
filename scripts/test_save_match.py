"""Test save_match"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.scrapers import FootballDataScraper
from app.repositories import FDRepository
from app.config import settings

async def main():
    scraper = FootballDataScraper()
    repo = FDRepository()

    # 测试获取 FINISHED 比赛
    print("Testing FINISHED matches...")
    matches = await scraper.get_matches(
        competition="PL",
        status="FINISHED",
        limit=5
    )

    print(f"Got {len(matches)} matches")

    for i, match in enumerate(matches[:3]):
        print(f"\nMatch {i+1}:")
        print(f"  ID: {match.get('id')}")
        print(f"  Home: {match.get('homeTeam', {}).get('name')}")
        print(f"  Away: {match.get('awayTeam', {}).get('name')}")
        print(f"  Status: {match.get('status')}")

        score = match.get('score', {})
        full_time = score.get('fullTime', {})
        half_time = score.get('halfTime', {})

        print(f"  FullTime: {full_time}")
        print(f"  HalfTime: {half_time}")
        print(f"  Referee: {match.get('referee')}")
        print(f"  Attendance: {match.get('attendance')}")
        print(f"  Matchday: {match.get('matchday')}")
        print(f"  Season: {match.get('season')}")

        # 尝试保存
        match_data = {
            'fd_id': match.get('id'),
            'league_code': 'PL',
            'home_team_id': match.get('homeTeam', {}).get('id'),
            'away_team_id': match.get('awayTeam', {}).get('id'),
            'home_team_name': match.get('homeTeam', {}).get('name'),
            'away_team_name': match.get('awayTeam', {}).get('name'),
            'match_date': match.get('utcDate'),
            'status': match.get('status'),
            'home_score': full_time.get('home'),
            'away_score': full_time.get('away'),
            'home_half_score': half_time.get('home') if half_time else None,
            'away_half_score': half_time.get('away') if half_time else None,
            'referee': match.get('referee', {}).get('name') if match.get('referee') else None,
            'attendance': match.get('attendance'),
            'matchday': match.get('matchday'),
            'season': match.get('season')
        }

        print(f"\n  Saving match_data (keys={list(match_data.keys())})...")
        result = await repo.save_match(match_data)
        print(f"  Result: {result}")

asyncio.run(main())
