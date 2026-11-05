import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import httpx
from app.main import app
from app.repositories import FDRepository, SportteryRepository
from app.repositories.baseline_data import (
    BASELINE_LEAGUES,
    BASELINE_STANDINGS,
    BASELINE_SCORERS,
    BASELINE_MATCHES
)

@pytest.mark.asyncio
async def test_sporttery_repository_contract():
    repo = SportteryRepository()
    assert hasattr(repo, 'save_match')
    assert hasattr(repo, 'update_match_score')
    assert hasattr(repo, 'get_matches')
    assert hasattr(repo, 'get_stats')

    matches = await repo.get_matches()
    assert isinstance(matches, list)
    assert len(matches) > 0

    stats = await repo.get_stats()
    assert isinstance(stats, dict)
    assert stats.get("sporttery_matches", 0) > 0

@pytest.mark.asyncio
async def test_fd_repository_baseline_coverage():
    repo = FDRepository()

    # 1. Leagues
    leagues = await repo.get_leagues()
    assert len(leagues) >= 6
    league_codes = [l['code'] for l in leagues]
    for expected in ['PL', 'PD', 'BL1', 'SA', 'FL1', 'CL']:
        assert expected in league_codes

    # 2. Standings & Scorers for all 6 leagues
    for code in ['PL', 'PD', 'BL1', 'SA', 'FL1', 'CL']:
        standings = await repo.get_standings(code)
        assert len(standings) > 0, f"Standings for {code} should not be empty"

        scorers_goals = await repo.get_scorers(code, order_by='goals')
        assert len(scorers_goals) > 0, f"Scorers (goals) for {code} should not be empty"

        scorers_assists = await repo.get_scorers(code, order_by='assists')
        assert len(scorers_assists) > 0, f"Scorers (assists) for {code} should not be empty"

    # 3. Matches by league
    for code in ['PL', 'PD', 'BL1', 'SA', 'FL1', 'CL']:
        matches = await repo.get_matches(league=code)
        assert len(matches) > 0, f"Matches for {code} should not be empty"

    # 4. Stats
    stats = await repo.get_stats()
    assert stats.get("fd_matches", 0) >= 1941

@pytest.mark.asyncio
async def test_api_endpoints_without_database():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        headers = {"Referer": "https://match-stats-keithwys-projects.vercel.app/dashboard"}

        # 1. Stats endpoint
        res = await client.get("/api/v1/stats", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data.get("fd_matches") >= 1941
        assert data.get("sporttery_matches") >= 50
        assert data.get("sync_status") == "ok"
        assert data.get("last_sync") is not None

        # 2. FD Matches endpoint for all 6 leagues
        for league in ["PL", "CL", "PD", "BL1", "SA", "FL1"]:
            res = await client.get(f"/api/v1/fd/matches?league={league}&limit=50", headers=headers)
            assert res.status_code == 200
            body = res.json()
            assert body.get("success") is True
            assert len(body.get("data", [])) > 0, f"API data for {league} matches should not be empty"

        # 3. FD Standings endpoint
        for league in ["PL", "CL", "PD", "BL1", "SA", "FL1"]:
            res = await client.get(f"/api/v1/fd/leagues/{league}/standings", headers=headers)
            assert res.status_code == 200
            body = res.json()
            assert body.get("success") is True
            assert len(body.get("data", [])) > 0, f"Standings for {league} should not be empty"

        # 4. FD Scorers endpoint
        for league in ["PL", "CL"]:
            res = await client.get(f"/api/v1/fd/leagues/{league}/scorers?order_by=goals", headers=headers)
            assert res.status_code == 200
            body = res.json()
            assert body.get("success") is True
            assert len(body.get("data", [])) > 0

        # 5. Sporttery Matches endpoint
        res = await client.get("/api/v1/sporttery/matches?limit=50", headers=headers)
        assert res.status_code == 200
        body = res.json()
        assert body.get("success") is True
        assert len(body.get("data", [])) > 0

        # 6. Dashboard page (Issue #17: /dashboard, /dashboard/, /matchstats, /matchstats/)
        res = await client.get("/dashboard")
        assert res.status_code == 200
        assert "MatchStats" in res.text
        assert "Opta AI" in res.text

        res_dash_slash = await client.get("/dashboard/")
        assert res_dash_slash.status_code == 200
        assert "MatchStats" in res_dash_slash.text

        res_matchstats = await client.get("/matchstats")
        assert res_matchstats.status_code == 200
        assert "MatchStats" in res_matchstats.text

        res_matchstats_slash = await client.get("/matchstats/")
        assert res_matchstats_slash.status_code == 200
        assert "MatchStats" in res_matchstats_slash.text

        res_app_static_html = await client.get("/app/static/index.html")
        assert res_app_static_html.status_code == 200
        assert "MatchStats" in res_app_static_html.text

        # 6.1 Static Assets & MatchBrief
        res_tokens = await client.get("/static/tokens.css")
        assert res_tokens.status_code == 200
        assert "--ms-bg-canvas" in res_tokens.text

        res_style = await client.get("/static/style.css")
        assert res_style.status_code == 200

        res_app_js = await client.get("/static/app.js")
        assert res_app_js.status_code == 200

        res_app_static_css = await client.get("/app/static/style.css")
        assert res_app_static_css.status_code == 200

        res_briefing = await client.get("/matchstats/briefing.html")
        assert res_briefing.status_code == 200
        assert "MatchBrief" in res_briefing.text

        # 7. Landing page (Issue #16)
        res_landing = await client.get("/")
        assert res_landing.status_code == 200
        assert "KEithWYong@Gmail.com" in res_landing.text
        assert "t.me/oldkclub" in res_landing.text

        # 8. Vercel fallback entry (Issue #16)
        res_fallback = await client.get("/api/index.py")
        assert res_fallback.status_code == 200
        assert "KEithWYong@Gmail.com" in res_fallback.text

@pytest.mark.asyncio
async def test_issue_15_match_status_and_nov3_matches():
    """验证 Issue #15：已结束比赛状态标记为 FINISHED，且具备 11月3日 当天比赛"""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        headers = {"Referer": "https://match-stats-keithwys-projects.vercel.app/dashboard"}

        # 获取英超比赛
        res = await client.get("/api/v1/fd/matches?league=PL&limit=100", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data.get("success") is True
        matches = data.get("data", [])
        assert len(matches) > 0

        # 1. 验证 11月1日切尔西1-1曼联 (fd_id 500109) 状态为 FINISHED
        chelsea_mu = next((m for m in matches if m.get("fd_id") == 500109), None)
        assert chelsea_mu is not None, "应包含切尔西 vs 曼联 (500109) 比赛"
        assert chelsea_mu.get("status") == "FINISHED", f"500109 应已完场，当前为 {chelsea_mu.get('status')}"
        assert chelsea_mu.get("home_score") == 1
        assert chelsea_mu.get("away_score") == 1

        # 2. 验证所有 11月2日及以前已开赛比赛状态均为 FINISHED
        for m in matches:
            m_date = m.get("match_date", "")
            if m_date and m_date < "2026-11-03T00:00:00Z":
                assert m.get("status") == "FINISHED", f"过去的比赛 {m.get('fd_id')} {m_date} 状态应为 FINISHED"

        # 3. 验证具备 11月3日当天比赛
        nov3_matches = [m for m in matches if (m.get("match_date") or "").startswith("2026-11-03")]
        assert len(nov3_matches) > 0, "看板必须包含 11月3日 当天比赛"
        for m in nov3_matches:
            assert m.get("status") in ["SCHEDULED", "TIMED", "LIVE", "IN_PLAY", "FINISHED"], "11月3日当天比赛状态应有效"
