"""
Pydantic 数据模型
"""
from pydantic import BaseModel
from typing import Optional, List, Generic, TypeVar, Dict
from datetime import datetime


T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    """统一API响应格式"""
    success: bool = True
    data: Optional[T] = None
    total: Optional[int] = None
    error: Optional[str] = None
    timestamp: str = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


# Football-Data 模型
class FDLeague(BaseModel):
    """联赛"""
    code: str
    name: str
    country: Optional[str] = None
    current_season: Optional[int] = None


class FDTeam(BaseModel):
    """球队"""
    fd_id: int
    name: str
    short_name: Optional[str] = None
    venue: Optional[str] = None


class FDMatch(BaseModel):
    """比赛"""
    fd_id: int
    league_code: str
    home_team_id: Optional[int] = None
    away_team_id: Optional[int] = None
    home_team_name: Optional[str] = None
    away_team_name: Optional[str] = None
    match_date: str
    status: Optional[str] = None
    home_score: Optional[int] = None
    away_score: Optional[int] = None


class FDStanding(BaseModel):
    """积分榜"""
    league_code: str
    team_id: int
    team_name: str
    season: Optional[int] = None
    position: Optional[int] = None
    played_games: Optional[int] = None
    won: Optional[int] = None
    draw: Optional[int] = None
    lost: Optional[int] = None
    points: Optional[int] = None
    goals_for: Optional[int] = None
    goals_against: Optional[int] = None
    goal_diff: Optional[int] = None


class FDScorer(BaseModel):
    """射手榜"""
    league_code: str
    season: Optional[int] = None
    player_id: int
    player_name: str
    team_id: int
    team_name: str
    position: Optional[int] = None
    goals: Optional[int] = 0
    assists: Optional[int] = 0
    penalties: Optional[int] = 0
    played_matches: Optional[int] = 0
# 竞彩模型
class SportteryMatch(BaseModel):
    """竞彩比赛"""
    match_code: str
    group_date: str
    home_team: str
    away_team: str
    league: str
    match_time: str
    status: str = "pending"
    actual_score: Optional[str] = None
    half_score: Optional[str] = None


# 系统模型
class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    timestamp: str



class FDMatchDetail(BaseModel):
    """比赛详情"""
    match_id: int
    home_formation: Optional[str] = None
    away_formation: Optional[str] = None
    home_coach_name: Optional[str] = None
    away_coach_name: Optional[str] = None
    home_goal_count: int = 0
    away_goal_count: int = 0
    home_yellow_cards: int = 0
    away_yellow_cards: int = 0
    home_red_cards: int = 0
    away_red_cards: int = 0
    venue: Optional[str] = None
    referee: Optional[str] = None
    goals: List[Dict] = []
    lineup_home: List[Dict] = []
    lineup_away: List[Dict] = []
    bench_home: List[Dict] = []
    bench_away: List[Dict] = []


class StatsResponse(BaseModel):
    """统计响应"""
    fd_matches: int
    sporttery_matches: int
    last_sync: Optional[str] = None
    sync_status: str


class SyncLog(BaseModel):
    """同步日志"""
    id: int
    source: str
    task_type: str
    status: str
    records_count: int
    error_message: Optional[str] = None
    started_at: str
    finished_at: Optional[str] = None
    retry_count: int
