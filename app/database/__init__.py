"""
数据库初始化
"""
from aiosqlite import connect
from app.config import settings, ensure_data_dir
import logging

logger = logging.getLogger(__name__)


async def get_db():
    """获取数据库连接"""
    ensure_data_dir()
    conn = await connect(settings.DB_PATH)
    return conn


async def init_db():
    """初始化数据库表"""
    ensure_data_dir()

    conn = await get_db()
    cursor = await conn.cursor()

    # 启用 WAL 模式
    await cursor.execute("PRAGMA journal_mode=WAL")
    await cursor.execute("PRAGMA busy_timeout=30000")

    # Football-Data 表
    await _create_fd_tables(cursor)

    # 竞彩表
    await _create_sporttery_tables(cursor)

    # 日志表
    await _create_logs_table(cursor)

    await conn.commit()
    await conn.close()

    logger.info(f"数据库初始化完成: {settings.DB_PATH}")


async def _create_fd_tables(cursor):
    """创建 Football-Data 相关表"""

    # 联赛表
    await cursor.execute('''
        CREATE TABLE IF NOT EXISTS fd_leagues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fd_id INTEGER NOT NULL UNIQUE,
            code TEXT NOT NULL,
            name TEXT NOT NULL,
            country TEXT,
            current_season INTEGER,
            emblem TEXT,
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    ''')

    # 球队表（扩展）
    await cursor.execute('''
        CREATE TABLE IF NOT EXISTS fd_teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fd_id INTEGER NOT NULL UNIQUE,
            name TEXT NOT NULL,
            short_name TEXT,
            tla TEXT,
            crest TEXT,
            venue TEXT,
            founded INTEGER,
            club_colors TEXT,
            website TEXT,
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    ''')

    # 比赛表（扩展）
    await cursor.execute('''
        CREATE TABLE IF NOT EXISTS fd_matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fd_id INTEGER NOT NULL UNIQUE,
            league_code TEXT NOT NULL,
            home_team_id INTEGER,
            away_team_id INTEGER,
            home_team_name TEXT,
            away_team_name TEXT,
            match_date TEXT NOT NULL,
            status TEXT,
            home_score INTEGER,
            away_score INTEGER,
            home_half_score INTEGER,
            away_half_score INTEGER,
            referee TEXT,
            attendance INTEGER,
            matchday INTEGER,
            season INTEGER,
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    ''')

    # 积分榜表
    await cursor.execute('''
        CREATE TABLE IF NOT EXISTS fd_standings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            league_code TEXT NOT NULL,
            team_id INTEGER NOT NULL,
            team_name TEXT NOT NULL,
            season INTEGER,
            position INTEGER,
            played_games INTEGER,
            won INTEGER,
            draw INTEGER,
            lost INTEGER,
            points INTEGER,
            goals_for INTEGER,
            goals_against INTEGER,
            goal_diff INTEGER,
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            UNIQUE(league_code, team_id, season)
        )
    ''')

    # 射手榜表
    await cursor.execute('''
        CREATE TABLE IF NOT EXISTS fd_scorers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            league_code TEXT NOT NULL,
            season INTEGER,
            player_id INTEGER,
            player_name TEXT NOT NULL,
            team_id INTEGER,
            team_name TEXT NOT NULL,
            position INTEGER,
            goals INTEGER,
            assists INTEGER,
            penalties INTEGER,
            played_matches INTEGER,
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            UNIQUE(league_code, season, player_id)
        )
    ''')

    # 球员表
    await cursor.execute('''
        CREATE TABLE IF NOT EXISTS fd_players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fd_id INTEGER NOT NULL UNIQUE,
            name TEXT NOT NULL,
            first_name TEXT,
            last_name TEXT,
            date_of_birth TEXT,
            nationality TEXT,
            position TEXT,
            shirt_number INTEGER,
            team_id INTEGER,
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    ''')

    # 比赛详情表（阵容、进球、红黄牌等）
    await cursor.execute('''
        CREATE TABLE IF NOT EXISTS fd_match_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER NOT NULL UNIQUE,
            home_formation TEXT,
            away_formation TEXT,
            home_coach_name TEXT,
            away_coach_name TEXT,
            home_goal_count INTEGER DEFAULT 0,
            away_goal_count INTEGER DEFAULT 0,
            home_yellow_cards INTEGER DEFAULT 0,
            away_yellow_cards INTEGER DEFAULT 0,
            home_red_cards INTEGER DEFAULT 0,
            away_red_cards INTEGER DEFAULT 0,
            details_json TEXT,
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    ''')

    # 进球记录表
    await cursor.execute('''
        CREATE TABLE IF NOT EXISTS fd_match_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER NOT NULL,
            team_id INTEGER,
            team_name TEXT,
            player_id INTEGER,
            player_name TEXT,
            minute INTEGER,
            minute_extra INTEGER,
            type TEXT,
            home_away TEXT,
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    ''')

    # 球队教练表
    await cursor.execute('''
        CREATE TABLE IF NOT EXISTS fd_team_coaches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id INTEGER NOT NULL UNIQUE,
            coach_id INTEGER,
            coach_name TEXT,
            first_name TEXT,
            last_name TEXT,
            date_of_birth TEXT,
            nationality TEXT,
            contract_until TEXT,
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    ''')

    # 球队阵容表
    await cursor.execute('''
        CREATE TABLE IF NOT EXISTS fd_team_squads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id INTEGER NOT NULL,
            player_id INTEGER,
            player_name TEXT,
            position TEXT,
            shirt_number INTEGER,
            nationality TEXT,
            date_of_birth TEXT,
            contract_until TEXT,
            season INTEGER,
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            UNIQUE(team_id, player_id, season)
        )
    ''')

    # 索引
    await cursor.execute('CREATE INDEX IF NOT EXISTS idx_fd_matches_date ON fd_matches(match_date)')
    await cursor.execute('CREATE INDEX IF NOT EXISTS idx_fd_matches_status ON fd_matches(status)')
    await cursor.execute('CREATE INDEX IF NOT EXISTS idx_fd_matches_league ON fd_matches(league_code)')
    await cursor.execute('CREATE INDEX IF NOT EXISTS idx_fd_matches_season ON fd_matches(season)')
    await cursor.execute('CREATE INDEX IF NOT EXISTS idx_fd_standings_league ON fd_standings(league_code)')
    await cursor.execute('CREATE INDEX IF NOT EXISTS idx_fd_scorers_league ON fd_scorers(league_code)')
    await cursor.execute('CREATE INDEX IF NOT EXISTS idx_fd_scorers_season ON fd_scorers(season)')
    await cursor.execute('CREATE INDEX IF NOT EXISTS idx_fd_players_team ON fd_players(team_id)')
    await cursor.execute('CREATE INDEX IF NOT EXISTS idx_match_details_match ON fd_match_details(match_id)')
    await cursor.execute('CREATE INDEX IF NOT EXISTS idx_match_goals_match ON fd_match_goals(match_id)')
    await cursor.execute('CREATE INDEX IF NOT EXISTS idx_team_coaches_team ON fd_team_coaches(team_id)')
    await cursor.execute('CREATE INDEX IF NOT EXISTS idx_team_squads_team ON fd_team_squads(team_id)')


async def _create_sporttery_tables(cursor):
    """创建竞彩相关表"""

    # 竞彩比赛表
    await cursor.execute('''
        CREATE TABLE IF NOT EXISTS sporttery_matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_code TEXT NOT NULL,
            group_date TEXT NOT NULL,
            home_team TEXT NOT NULL,
            away_team TEXT NOT NULL,
            league TEXT NOT NULL,
            match_time TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            actual_score TEXT,
            half_score TEXT,
            scraped_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            UNIQUE(match_code, group_date)
        )
    ''')

    # 索引
    await cursor.execute('CREATE INDEX IF NOT EXISTS idx_sporttery_date ON sporttery_matches(group_date)')
    await cursor.execute('CREATE INDEX IF NOT EXISTS idx_sporttery_status ON sporttery_matches(status)')


async def _create_logs_table(cursor):
    """创建同步日志表"""

    await cursor.execute('''
        CREATE TABLE IF NOT EXISTS sync_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            task_type TEXT NOT NULL,
            status TEXT NOT NULL,
            records_count INTEGER DEFAULT 0,
            error_message TEXT,
            started_at TEXT NOT NULL DEFAULT (datetime('now')),
            finished_at TEXT,
            retry_count INTEGER DEFAULT 0
        )
    ''')
