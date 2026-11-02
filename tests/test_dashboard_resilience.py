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

        # 6. Dashboard page
        res = await client.get("/dashboard")
        assert res.status_code == 200
        assert "MatchStats" in res.text
