"""
数据访问层
"""
from aiosqlite import connect
from app.config import settings
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BaseRepository:
    """基础 Repository"""

    def __init__(self):
        self.db_path = settings.DB_PATH

    async def get_connection(self):
        """获取数据库连接"""
        return await connect(self.db_path)


class FDRepository(BaseRepository):
    """Football-Data 数据访问"""

    async def save_match(self, match: Dict) -> bool:
        """保存比赛"""
        try:
            conn = await self.get_connection()
            cursor = await conn.cursor()

            await cursor.execute('''
                INSERT OR REPLACE INTO fd_matches
                (fd_id, league_code, home_team_id, away_team_id,
                 home_team_name, away_team_name, match_date, status,
                 home_score, away_score, home_half_score, away_half_score,
                 referee, attendance, matchday, season, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                match.get('fd_id'),
                match.get('league_code'),
                match.get('home_team_id'),
                match.get('away_team_id'),
                match.get('home_team_name'),
                match.get('away_team_name'),
                match.get('match_date'),
                match.get('status'),
                match.get('home_score'),
                match.get('away_score'),
                match.get('home_half_score'),
                match.get('away_half_score'),
                match.get('referee'),
                match.get('attendance'),
                match.get('matchday'),
                match.get('season'),
                datetime.now().isoformat()
            ))

            await conn.commit()
            await conn.close()
            return True
        except Exception as e:
            logger.error(f"保存比赛失败: {e}")
            return False

    async def get_matches(self, date: Optional[str] = None,
                         league: Optional[str] = None,
                         status: Optional[str] = None,
                         limit: int = 100) -> List[Dict]:
        """获取比赛列表"""
        conn = await self.get_connection()
        conn.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))
        cursor = await conn.cursor()

        query = """
            SELECT m.*, 
                   COALESCE(th.name_cn, m.home_team_name) as home_team_name,
                   COALESCE(ta.name_cn, m.away_team_name) as away_team_name,
                   th.crest as home_team_logo,
                   ta.crest as away_team_logo
            FROM fd_matches m
            LEFT JOIN fd_teams th ON m.home_team_id = th.fd_id
            LEFT JOIN fd_teams ta ON m.away_team_id = ta.fd_id
            WHERE 1=1
        """
        params = []

        if date:
            query += " AND date(match_date) = ?"
            params.append(date)
        if league:
            query += " AND league_code = ?"
            params.append(league)
        if status:
            if status == 'LIVE':
                query += " AND status IN ('LIVE', 'IN_PLAY', 'PAUSED')"
            elif status == 'SCHEDULED':
                query += " AND status IN ('SCHEDULED', 'TIMED')"
            else:
                query += " AND status = ?"
                params.append(status)
        
        # User requirement: Strictly sort by date ASC so the earliest match is at the top.
        query += " ORDER BY match_date ASC LIMIT ?"
        params.append(limit)

        await cursor.execute(query, params)
        rows = await cursor.fetchall()
        await conn.close()

        return rows

    async def get_match_by_id(self, fd_id: int) -> Optional[Dict]:
        """获取单场比赛"""
        conn = await self.get_connection()
        conn.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))
        cursor = await conn.cursor()

        await cursor.execute("SELECT * FROM fd_matches WHERE fd_id = ?", (fd_id,))
        row = await cursor.fetchone()
        await conn.close()

        return row

    async def save_team(self, team: Dict) -> bool:
        """保存球队"""
        try:
            conn = await self.get_connection()
            cursor = await conn.cursor()

            await cursor.execute('''
                INSERT OR REPLACE INTO fd_teams
                (fd_id, name, short_name, tla, crest, venue, founded, club_colors, website, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                team.get('fd_id'),
                team.get('name'),
                team.get('short_name'),
                team.get('tla'),
                team.get('crest'),
                team.get('venue'),
                team.get('founded'),
                team.get('club_colors'),
                team.get('website'),
                datetime.now().isoformat()
            ))

            await conn.commit()
            await conn.close()
            return True
        except Exception as e:
            logger.error(f"保存球队失败: {e}")
            return False

    async def save_league(self, league: Dict) -> bool:
        """保存联赛"""
        try:
            conn = await self.get_connection()
            cursor = await conn.cursor()

            await cursor.execute('''
                INSERT OR REPLACE INTO fd_leagues
                (fd_id, code, name, country, current_season, emblem, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                league.get('fd_id'),
                league.get('code'),
                league.get('name'),
                league.get('country'),
                league.get('current_season'),
                league.get('emblem'),
                datetime.now().isoformat()
            ))

            await conn.commit()
            await conn.close()
            return True
        except Exception as e:
            logger.error(f"保存联赛失败: {e}")
            return False

    async def save_scorer(self, scorer: Dict) -> bool:
        """保存射手榜"""
        try:
            conn = await self.get_connection()
            cursor = await conn.cursor()

            await cursor.execute('''
                INSERT OR REPLACE INTO fd_scorers
                (league_code, season, player_id, player_name, team_id, team_name,
                 position, goals, assists, penalties, played_matches, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                scorer.get('league_code'),
                scorer.get('season'),
                scorer.get('player_id'),
                scorer.get('player_name'),
                scorer.get('team_id'),
                scorer.get('team_name'),
                scorer.get('position'),
                scorer.get('goals'),
                scorer.get('assists'),
                scorer.get('penalties'),
                scorer.get('played_matches'),
                datetime.now().isoformat()
            ))

            await conn.commit()
            await conn.close()
            return True
        except Exception as e:
            logger.error(f"保存射手榜失败: {e}")
            return False

    async def get_scorers(self, league_code: str, season: Optional[int] = None, order_by: str = 'goals') -> List[Dict]:
        """获取射手榜/助攻榜"""
        conn = await self.get_connection()
        conn.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))
        cursor = await conn.cursor()

        # 使用 MAX(id) 去除通过 season=NULL 导致的重复数据
        query = """
            SELECT s.*, 
                   COALESCE(t.name_cn, s.team_name) as team_name
            FROM fd_scorers s
            LEFT JOIN fd_teams t ON s.team_id = t.fd_id
            WHERE s.league_code = ?
            AND s.id IN (
                SELECT MAX(id) 
                FROM fd_scorers 
                WHERE league_code = ? 
                GROUP BY player_id
            )
        """
        params = [league_code, league_code]

        if season:
            query += " AND s.season = ?"
            params.append(season)

        if order_by == 'assists':
            query += " ORDER BY s.assists DESC, s.goals DESC LIMIT 50"
        else:
            query += " ORDER BY s.goals DESC, s.assists DESC LIMIT 50"

        await cursor.execute(query, params)
        rows = await cursor.fetchall()
        await conn.close()

        return rows

    async def save_standing(self, standing: Dict) -> bool:
        """保存积分榜"""
        try:
            conn = await self.get_connection()
            cursor = await conn.cursor()

            await cursor.execute('''
                INSERT OR REPLACE INTO fd_standings
                (league_code, team_id, team_name, season, position,
                 played_games, won, draw, lost, points,
                 goals_for, goals_against, goal_diff, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                standing.get('league_code'),
                standing.get('team_id'),
                standing.get('team_name'),
                standing.get('season'),
                standing.get('position'),
                standing.get('played_games'),
                standing.get('won'),
                standing.get('draw'),
                standing.get('lost'),
                standing.get('points'),
                standing.get('goals_for'),
                standing.get('goals_against'),
                standing.get('goal_diff'),
                datetime.now().isoformat()
            ))

            await conn.commit()
            await conn.close()
            return True
        except Exception as e:
            logger.error(f"保存积分榜失败: {e}")
            return False

    async def get_standings(self, league_code: str, season: Optional[int] = None) -> List[Dict]:
        """获取积分榜"""
        conn = await self.get_connection()
        conn.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))
        cursor = await conn.cursor()

        # 使用 MAX(id) 去除通过 season=NULL 导致的重复数据
        query = """
            SELECT s.*, 
                   COALESCE(t.name_cn, s.team_name) as team_name
            FROM fd_standings s
            LEFT JOIN fd_teams t ON s.team_id = t.fd_id
            WHERE s.league_code = ?
            AND s.id IN (
                SELECT MAX(id) 
                FROM fd_standings 
                WHERE league_code = ? 
                GROUP BY team_id
            )
        """
        params = [league_code, league_code]

        if season:
            query += " AND s.season = ?"
            params.append(season)

        query += " ORDER BY s.position ASC"

        await cursor.execute(query, params)
        rows = await cursor.fetchall()
        await conn.close()

        return rows

    async def get_stats(self) -> Dict:
        """获取统计"""
        conn = await self.get_connection()
        cursor = await conn.cursor()

        await cursor.execute("SELECT COUNT(*) FROM fd_matches")
        fd_matches = (await cursor.fetchone())[0]

        await conn.close()
        return {"fd_matches": fd_matches}

    async def save_match_details(self, details: Dict) -> bool:
        """保存比赛详情"""
        try:
            conn = await self.get_connection()
            cursor = await conn.cursor()

            await cursor.execute('''
                INSERT OR REPLACE INTO fd_match_details
                (match_id, home_formation, away_formation, home_coach_name, away_coach_name,
                 home_goal_count, away_goal_count, home_yellow_cards, away_yellow_cards,
                 home_red_cards, away_red_cards, details_json, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                details.get('match_id'),
                details.get('home_formation'),
                details.get('away_formation'),
                details.get('home_coach_name'),
                details.get('away_coach_name'),
                details.get('home_goal_count', 0),
                details.get('away_goal_count', 0),
                details.get('home_yellow_cards', 0),
                details.get('away_yellow_cards', 0),
                details.get('home_red_cards', 0),
                details.get('away_red_cards', 0),
                details.get('details_json'),
                datetime.now().isoformat()
            ))

            await conn.commit()
            await conn.close()
            return True
        except Exception as e:
            logger.error(f"保存比赛详情失败: {e}")
            return False

    async def save_match_goal(self, goal: Dict) -> bool:
        """保存进球记录"""
        try:
            conn = await self.get_connection()
            cursor = await conn.cursor()

            await cursor.execute('''
                INSERT INTO fd_match_goals
                (match_id, team_id, team_name, player_id, player_name,
                 minute, minute_extra, type, home_away, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                goal.get('match_id'),
                goal.get('team_id'),
                goal.get('team_name'),
                goal.get('player_id'),
                goal.get('player_name'),
                goal.get('minute'),
                goal.get('minute_extra'),
                goal.get('type'),
                goal.get('home_away'),
                datetime.now().isoformat()
            ))

            await conn.commit()
            await conn.close()
            return True
        except Exception as e:
            logger.error(f"保存进球失败: {e}")
            return False

    async def clear_match_goals(self, match_id: int):
        """清除比赛进球记录（用于更新）"""
        conn = await self.get_connection()
        cursor = await conn.cursor()
        await cursor.execute("DELETE FROM fd_match_goals WHERE match_id = ?", (match_id,))
        await conn.commit()
        await conn.close()

    async def save_team_coach(self, coach: Dict) -> bool:
        """保存球队教练"""
        try:
            conn = await self.get_connection()
            cursor = await conn.cursor()

            await cursor.execute('''
                INSERT OR REPLACE INTO fd_team_coaches
                (team_id, coach_id, coach_name, first_name, last_name,
                 date_of_birth, nationality, contract_until, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                coach.get('team_id'),
                coach.get('coach_id'),
                coach.get('coach_name'),
                coach.get('first_name'),
                coach.get('last_name'),
                coach.get('date_of_birth'),
                coach.get('nationality'),
                coach.get('contract_until'),
                datetime.now().isoformat()
            ))

            await conn.commit()
            await conn.close()
            return True
        except Exception as e:
            logger.error(f"保存教练失败: {e}")
            return False

    async def save_team_squad(self, player: Dict) -> bool:
        """保存球队阵容球员"""
        try:
            conn = await self.get_connection()
            cursor = await conn.cursor()

            await cursor.execute('''
                INSERT OR REPLACE INTO fd_team_squads
                (team_id, player_id, player_name, position, shirt_number,
                 nationality, date_of_birth, contract_until, season, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                player.get('team_id'),
                player.get('player_id'),
                player.get('player_name'),
                player.get('position'),
                player.get('shirt_number'),
                player.get('nationality'),
                player.get('date_of_birth'),
                player.get('contract_until'),
                player.get('season'),
                datetime.now().isoformat()
            ))

            await conn.commit()
            await conn.close()
            return True
        except Exception as e:
            logger.error(f"保存阵容失败: {e}")
            return False

    async def get_all_team_ids(self) -> List[int]:
        """获取所有球队ID"""
        conn = await self.get_connection()
        cursor = await conn.cursor()
        await cursor.execute("SELECT fd_id FROM fd_teams")
        rows = await cursor.fetchall()
        await conn.close()
        return [row[0] for row in rows]

    async def get_match_ids_by_status(self, status: str) -> List[int]:
        """获取指定状态的比赛ID"""
        conn = await self.get_connection()
        cursor = await conn.cursor()
        await cursor.execute("SELECT fd_id FROM fd_matches WHERE status = ?", (status,))
        rows = await cursor.fetchall()
        await conn.close()
        return [row[0] for row in rows]
    async def get_match_details(self, match_id: int) -> Optional[Dict]:
        """获取比赛详情（包含进球）"""
        conn = await self.get_connection()
        conn.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))
        cursor = await conn.cursor()

        # 1. 基础详情
        await cursor.execute("SELECT * FROM fd_match_details WHERE match_id = ?", (match_id,))
        detail = await cursor.fetchone()

        if not detail:
            await conn.close()
            return None

        # 2. 进球
        await cursor.execute("""
            SELECT mg.*,
                   COALESCE(t.name_cn, mg.team_name) as team_name
            FROM fd_match_goals mg
            LEFT JOIN fd_teams t ON mg.team_id = t.fd_id
            WHERE match_id = ?
            ORDER BY minute ASC, minute_extra ASC
        """, (match_id,))
        goals = await cursor.fetchall()
        detail['goals'] = goals

        # 3. 基础比赛信息（获取裁判、场地等）
        await cursor.execute("SELECT referee, venue FROM fd_matches WHERE fd_id = ?", (match_id,))
        match_basic = await cursor.fetchone()
        if match_basic:
            detail['referee'] = match_basic.get('referee')
            # 优先使用 match_details 里的（如果以后存了），或者回退到 matches 表
            # 目前 db 中的 venue 实际上在 fd_matches 表里也不总是存在，视爬虫而定
            # fd_match_details 不存 venue。
            pass

        # 4. 解析 JSON 并提取阵容（简易版，只从 JSON 中尝试提取）
        import json
        try:
            full_data = json.loads(detail['details_json'])
            detail['venue'] = full_data.get('venue')
            # 阵容
            detail['lineup_home'] = full_data.get('homeTeam', {}).get('lineup', [])
            detail['lineup_away'] = full_data.get('awayTeam', {}).get('lineup', [])
            detail['bench_home'] = full_data.get('homeTeam', {}).get('bench', [])
            detail['bench_away'] = full_data.get('awayTeam', {}).get('bench', [])
        except:
            detail['lineup_home'] = []
            detail['lineup_away'] = []
            detail['bench_home'] = []
            detail['bench_away'] = []

        await conn.close()
        return detail

class SportteryRepository(BaseRepository):
    """竞彩数据访问"""

    async def save_match(self, match: Dict) -> bool:
        """保存比赛"""
        try:
            conn = await self.get_connection()
            cursor = await conn.cursor()

            await cursor.execute('''
                INSERT OR REPLACE INTO sporttery_matches
                (match_code, group_date, home_team, away_team,
                 league, match_time, status, actual_score, half_score, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                match.get('match_code'),
                match.get('group_date'),
                match.get('home_team'),
                match.get('away_team'),
                match.get('league'),
                match.get('match_time'),
                match.get('status', 'pending'),
                match.get('actual_score'),
                match.get('half_score'),
                datetime.now().isoformat()
            ))

            await conn.commit()
            await conn.close()
            return True
        except Exception as e:
            logger.error(f"保存竞彩比赛失败: {e}")
            return False

    async def get_matches(self, date: Optional[str] = None,
                          status: Optional[str] = None,
                          limit: int = 100) -> List[Dict]:
        """获取比赛列表"""
        conn = await self.get_connection()
        conn.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))
        cursor = await conn.cursor()

        query = "SELECT * FROM sporttery_matches WHERE 1=1"
        params = []

        if date:
            query += " AND group_date = ?"
            params.append(date)
        if status:
            s_lower = status.lower()
            if s_lower == 'live':
                # Sporttery usually doesn't have 'live', use 'pending' as proxy
                query += " AND status = 'pending'"
            else:
                query += " AND status = ?"
                params.append(s_lower)
        
        # User requirement: Strictly sort by time ASC so the earliest match is at the top.
        query += " ORDER BY match_time ASC LIMIT ?"
        params.append(limit)

        await cursor.execute(query, params)
        rows = await cursor.fetchall()
        await conn.close()

        return rows

    async def get_match_by_code(self, match_code: str) -> Optional[Dict]:
        """获取单场比赛"""
        conn = await self.get_connection()
        conn.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))
        cursor = await conn.cursor()

        await cursor.execute("SELECT * FROM sporttery_matches WHERE match_code = ?", (match_code,))
        row = await cursor.fetchone()
        await conn.close()

        return row

    async def get_stats(self) -> Dict:
        """获取统计"""
        conn = await self.get_connection()
        cursor = await conn.cursor()

        await cursor.execute("SELECT COUNT(*) FROM sporttery_matches")
        sporttery_matches = (await cursor.fetchone())[0]

        await conn.close()
        return {"sporttery_matches": sporttery_matches}


class LogRepository(BaseRepository):
    """日志数据访问"""

    async def log_sync(self, source: str, task_type: str, status: str,
                      records_count: int = 0, error_message: str = "",
                      retry_count: int = 0) -> int:
        """记录同步日志"""
        conn = await self.get_connection()
        cursor = await conn.cursor()

        await cursor.execute('''
            INSERT INTO sync_logs
            (source, task_type, status, records_count, error_message, retry_count)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (source, task_type, status, records_count, error_message, retry_count))

        await conn.commit()
        row_id = cursor.lastrowid
        await conn.close()

        return row_id

    async def update_log_finish(self, log_id: int):
        """更新日志完成时间"""
        conn = await self.get_connection()
        cursor = await conn.cursor()

        await cursor.execute('''
            UPDATE sync_logs SET finished_at = ? WHERE id = ?
        ''', (datetime.now().isoformat(), log_id))

        await conn.commit()
        await conn.close()

    async def get_logs(self, source: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """获取日志"""
        conn = await self.get_connection()
        conn.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))
        cursor = await conn.cursor()

        query = "SELECT * FROM sync_logs"
        params = []

        if source:
            query += " WHERE source = ?"
            params.append(source)

        query += " ORDER BY started_at DESC LIMIT ?"
        params.append(limit)

        await cursor.execute(query, params)
        rows = await cursor.fetchall()
        await conn.close()

        return rows

    async def get_last_sync_time(self, source: str) -> Optional[str]:
        """获取最后同步时间"""
        conn = await self.get_connection()
        cursor = await conn.cursor()

        await cursor.execute('''
            SELECT started_at FROM sync_logs
            WHERE source = ? AND status = 'success'
            ORDER BY started_at DESC LIMIT 1
        ''', (source,))

        row = await cursor.fetchone()
        await conn.close()

        return row[0] if row else None
