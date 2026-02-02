"""
测试多语言 API 功能
验证 lang 参数是否正常工作
"""
import httpx
import json

HEADERS = {"X-API-KEY": "mk_live_2024_secure_key_xyz123"}
BASE_URL = "https://kmatch-stats.vercel.app"

print("=" * 70)
print("MatchStats API - 多语言功能测试")
print("=" * 70)

with httpx.Client(timeout=30.0) as client:
    # 测试 1: 比赛列表 - 英文 vs 中文
    print("\n[测试 1] 比赛列表 - 语言对比")
    print("-" * 70)

    # 英文版本
    response_en = client.get(
        f"{BASE_URL}/api/v1/fd/matches?limit=2&lang=en",
        headers=HEADERS
    )

    # 中文版本
    response_zh = client.get(
        f"{BASE_URL}/api/v1/fd/matches?limit=2&lang=zh",
        headers=HEADERS
    )

    if response_en.status_code == 200 and response_zh.status_code == 200:
        data_en = response_en.json()['data']
        data_zh = response_zh.json()['data']

        if len(data_en) > 0 and len(data_zh) > 0:
            match_en = data_en[0]
            match_zh = data_zh[0]

            print(f"✓ 英文: {match_en['home_team_name']} vs {match_en['away_team_name']}")
            print(f"✓ 中文: {match_zh['home_team_name']} vs {match_zh['away_team_name']}")

            if match_en['home_team_name'] != match_zh['home_team_name']:
                print("  ✓ 语言切换成功！")
            else:
                print("  ⚠ 可能没有翻译，返回了相同的英文名")

    # 测试 2: 积分榜 - 英文 vs 中文
    print("\n[测试 2] 积分榜 - 语言对比")
    print("-" * 70)

    # 英文版本
    standings_en = client.get(
        f"{BASE_URL}/api/v1/fd/leagues/PL/standings?limit=3&lang=en",
        headers=HEADERS
    )

    # 中文版本
    standings_zh = client.get(
        f"{BASE_URL}/api/v1/fd/leagues/PL/standings?limit=3&lang=zh",
        headers=HEADERS
    )

    if standings_en.status_code == 200 and standings_zh.status_code == 200:
        data_en = standings_en.json()['data']
        data_zh = standings_zh.json()['data']

        if len(data_en) > 0 and len(data_zh) > 0:
            team_en = data_en[0]
            team_zh = data_zh[0]

            print(f"✓ 英文: Position {team_en['position']} - {team_en['team_name']}")
            print(f"✓ 中文: Position {team_zh['position']} - {team_zh['team_name']}")

            if team_en['team_name'] != team_zh['team_name']:
                print("  ✓ 语言切换成功！")
            else:
                print("  ⚠ 可能没有翻译")

    # 测试 3: 射手榜 - 英文 vs 中文
    print("\n[测试 3] 射手榜 - 语言对比")
    print("-" * 70)

    # 英文版本
    scorers_en = client.get(
        f"{BASE_URL}/api/v1/fd/leagues/PL/scorers?limit=3&lang=en",
        headers=HEADERS
    )

    # 中文版本
    scorers_zh = client.get(
        f"{BASE_URL}/api/v1/fd/leagues/PL/scorers?limit=3&lang=zh",
        headers=HEADERS
    )

    if scorers_en.status_code == 200 and scorers_zh.status_code == 200:
        data_en = scorers_en.json()['data']
        data_zh = scorers_zh.json()['data']

        if len(data_en) > 0 and len(data_zh) > 0:
            scorer_en = data_en[0]
            scorer_zh = data_zh[0]

            print(f"✓ 英文: {scorer_en['player_name']} ({scorer_en['team_name']}) - {scorer_en['goals']} goals")
            print(f"✓ 中文: {scorer_zh['player_name']} ({scorer_zh['team_name']}) - {scorer_zh['goals']} 进球")

            if scorer_en['team_name'] != scorer_zh['team_name']:
                print("  ✓ 语言切换成功！")
            else:
                print("  ⚠ 可能没有翻译")

    # 测试 4: 默认行为（不带 lang 参数）
    print("\n[测试 4] 默认行为（不带 lang 参数）")
    print("-" * 70)

    response_default = client.get(
        f"{BASE_URL}/api/v1/fd/teams?limit=3",
        headers=HEADERS
    )

    if response_default.status_code == 200:
        data = response_default.json()['data']
        if len(data) > 0:
            team = data[0]
            print(f"✓ 默认返回: {team.get('name', 'N/A')}")
            print("  注：默认应该是英文")

print("\n" + "=" * 70)
print("测试完成！")
print("=" * 70)
