"""
API 路由
"""
from fastapi import APIRouter, Query
from typing import Optional, List
from datetime import datetime
import logging

from app.models import *
from app.repositories import FDRepository, SportteryRepository, LogRepository
from app.config import settings

logger = logging.getLogger(__name__)

# 创建 Router
fd_router = APIRouter(prefix="/api/v1/fd", tags=["Football-Data"])
sporttery_router = APIRouter(prefix="/api/v1/sporttery", tags=["竞彩"])
system_router = APIRouter(prefix="/api/v1", tags=["系统"])

# Repository 实例
fd_repo = FDRepository()
sporttery_repo = SportteryRepository()
log_repo = LogRepository()


# ============== Football-Data API ==============

@fd_router.get("/matches", response_model=ApiResponse[List[FDMatch]])
async def get_fd_matches(
    date: Optional[str] = Query(None, description="日期 YYYY-MM-DD"),
    league: Optional[str] = Query(None, description="联赛代码"),
    status: Optional[str] = Query(None, description="状态 SCHEDULED/LIVE/FINISHED"),
    limit: int = Query(100, ge=1, le=500)
):
    """获取比赛列表"""
    matches = await fd_repo.get_matches(date=date, league=league, status=status, limit=limit)
    return ApiResponse(data=matches, total=len(matches))


@fd_router.get("/matches/{match_id}", response_model=ApiResponse[FDMatch])
async def get_fd_match(match_id: int):
    """获取单场比赛"""
    match = await fd_repo.get_match_by_id(match_id)
    if not match:
        return ApiResponse(success=False, error="比赛不存在")
    return ApiResponse(data=match)

@fd_router.get("/matches/{match_id}/details", response_model=ApiResponse[FDMatchDetail])
async def get_fd_match_details(match_id: int):
    """获取单场比赛详情（阵容+进球）"""
    detail = await fd_repo.get_match_details(match_id)
    if not detail:
        return ApiResponse(success=False, error="详情不存在（比赛可能未开始）")
    return ApiResponse(data=detail)


@fd_router.get("/leagues", response_model=ApiResponse[List[FDLeague]])
async def get_fd_leagues():
    """获取联赛列表"""
    conn = await fd_repo.get_connection()
    conn.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))
    cursor = await conn.cursor()
    await cursor.execute("SELECT * FROM fd_leagues ORDER BY code")
    rows = await cursor.fetchall()
    await conn.close()
    return ApiResponse(data=rows, total=len(rows))


@fd_router.get("/leagues/{code}/standings", response_model=ApiResponse[List[FDStanding]])
async def get_fd_standings(code: str, season: Optional[int] = None):
    """获取积分榜"""
    standings = await fd_repo.get_standings(code, season)
    return ApiResponse(data=standings, total=len(standings))


@fd_router.get("/leagues/{code}/scorers", response_model=ApiResponse[List[FDScorer]])
async def get_fd_scorers(
    code: str, 
    season: Optional[int] = None, 
    order_by: str = Query('goals', pattern='^(goals|assists)$')
):
    """获取射手榜/助攻榜"""
    logger.info(f"Fetching scorers for {code}, order_by={order_by}")
    scorers = await fd_repo.get_scorers(code, season, order_by=order_by)
    return ApiResponse(data=scorers, total=len(scorers))


@fd_router.get("/teams", response_model=ApiResponse[List[FDTeam]])
async def get_fd_teams(league: Optional[str] = None):
    """获取球队列表"""
    conn = await fd_repo.get_connection()
    conn.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))
    cursor = await conn.cursor()

    if league:
        await cursor.execute('''
            SELECT DISTINCT t.* FROM fd_teams t
            INNER JOIN fd_matches m ON (m.home_team_id = t.fd_id OR m.away_team_id = t.fd_id)
            WHERE m.league_code = ?
        ''', (league,))
    else:
        await cursor.execute("SELECT * FROM fd_teams ORDER BY name")

    rows = await cursor.fetchall()
    await conn.close()
    return ApiResponse(data=rows, total=len(rows))


# ============== 竞彩 API ==============

@sporttery_router.get("/matches", response_model=ApiResponse[List[SportteryMatch]])
async def get_sporttery_matches(
    date: Optional[str] = Query(None, description="日期 YYYY-MM-DD"),
    status: Optional[str] = Query(None, description="状态 pending/finished"),
    limit: int = Query(100, ge=1, le=500)
):
    """获取竞彩比赛列表"""
    matches = await sporttery_repo.get_matches(date=date, status=status, limit=limit)
    return ApiResponse(data=matches, total=len(matches))


@sporttery_router.get("/matches/{match_code}", response_model=ApiResponse[SportteryMatch])
async def get_sporttery_match(match_code: str):
    """获取单场竞彩比赛"""
    match = await sporttery_repo.get_match_by_code(match_code)
    if not match:
        return ApiResponse(success=False, error="比赛不存在")
    return ApiResponse(data=match)


# ============== 系统 API ==============

@system_router.get("/health", response_model=HealthResponse)
async def health():
    """健康检查"""
    return HealthResponse(status="ok", timestamp=datetime.now().isoformat())


@system_router.get("/debug")
async def get_debug():
    """调试信息终端"""
    import os
    from fastapi.responses import PlainTextResponse
    db_exists = os.path.exists(settings.DB_PATH)
    tmp_exists = os.path.exists("/tmp/matchstats.db")
    # 打印 /var/task 的内容
    try:
        task_files = os.listdir("/var/task")
    except:
        task_files = "error"
    return PlainTextResponse(f"CWD: {os.getcwd()}\nDB_PATH: {settings.DB_PATH}\nDB_EXISTS: {db_exists}\nTMP_EXISTS: {tmp_exists}\nTASK_FILES: {task_files}\n")

@system_router.get("/stats", response_model=StatsResponse)
async def get_stats():
    """获取统计信息"""
    fd_stats = await fd_repo.get_stats()
    sporttery_stats = await sporttery_repo.get_stats()

    last_fd = await log_repo.get_last_sync_time("football_data")
    last_sporttery = await log_repo.get_last_sync_time("sporttery")

    last_sync = None
    if last_fd and last_sporttery:
        last_sync = max(last_fd, last_sporttery)
    elif last_fd:
        last_sync = last_fd
    elif last_sporttery:
        last_sync = last_sporttery

    return StatsResponse(
        fd_matches=fd_stats.get("fd_matches", 0),
        sporttery_matches=sporttery_stats.get("sporttery_matches", 0),
        last_sync=last_sync,
        sync_status="ok"
    )


@system_router.get("/logs", response_model=ApiResponse[List[SyncLog]])
async def get_logs(
    source: Optional[str] = Query(None, description="数据源 fd/sporttery"),
    limit: int = Query(50, ge=1, le=200)
):
    """获取同步日志"""
    logs = await log_repo.get_logs(source=source, limit=limit)
    return ApiResponse(data=logs, total=len(logs))
