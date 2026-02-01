"""
数据访问层 (Supabase 云数据库版)
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
from app.config import settings
from app.database import supabase

logger = logging.getLogger(__name__)

class BaseRepository:
    """基础 Repository"""
    def __init__(self):
        self._client = supabase
    
    @property
    def client(self):
        if self._client is None:
            from app.database import supabase as latest_supabase
            self._client = latest_supabase
            if self._client is None:
                raise RuntimeError("Supabase client is not initialized. Please check your SUPABASE_KEY and SUPABASE_URL.")
        return self._client

class FDRepository(BaseRepository):
    """Football-Data 数据访问"""

    async def save_match(self, match: Dict) -> bool:
        """保存比赛"""
        try:
            # 准备数据
            data = {
                'fd_id': match.get('fd_id'),
                'league_code': match.get('league_code'),
                'home_team_id': match.get('home_team_id'),
                'away_team_id': match.get('away_team_id'),
                'home_team_name': match.get('home_team_name'),
                'away_team_name': match.get('away_team_name'),
                'match_date': match.get('match_date'),
                'status': match.get('status'),
                'home_score': match.get('home_score'),
                'away_score': match.get('away_score'),
                'home_half_score': match.get('home_half_score'),
                'away_half_score': match.get('away_half_score'),
                'referee': match.get('referee'),
                'attendance': match.get('attendance'),
                'matchday': match.get('matchday'),
                'season': match.get('season'),
                'updated_at': datetime.now().isoformat()
            }
            # 使用 upsert，基于 unique index (fd_id)
            self.client.table('fd_matches').upsert(data, on_conflict="fd_id").execute()
            return True
        except Exception as e:
            logger.error(f"Supabase 保存比赛失败: {e}")
            return False

    async def get_matches(self, date: Optional[str] = None,
                         league: Optional[str] = None,
                         status: Optional[str] = None,
                         limit: int = 100) -> List[Dict]:
        """获取比赛列表 (附带中文名)"""
        try:
            query = self.client.table('fd_matches').select("*")
            
            if date:
                query = query.gte('match_date', f"{date}T00:00:00").lte('match_date', f"{date}T23:59:59")
            if league:
                query = query.eq('league_code', league)
            if status:
                if status == 'LIVE':
                    query = query.in_('status', ['LIVE', 'IN_PLAY', 'PAUSED'])
                elif status == 'SCHEDULED':
                    query = query.in_('status', ['SCHEDULED', 'TIMED'])
                else:
                    query = query.eq('status', status)
            
            response = query.order('match_date', desc=False).limit(limit).execute()
            matches = response.data
            
            # 获取所有相关球队ID
            team_ids = set()
            for m in matches:
                team_ids.add(m['home_team_id'])
                team_ids.add(m['away_team_id'])
            
            if team_ids:
                teams_res = self.client.table('fd_teams').select("fd_id, name_cn, crest").in_('fd_id', list(team_ids)).execute()
                team_map = {t['fd_id']: t for t in teams_res.data}
                
                for m in matches:
                    h_team = team_map.get(m['home_team_id'], {})
                    a_team = team_map.get(m['away_team_id'], {})
                    
                    m['home_team_name_cn'] = h_team.get('name_cn') or m['home_team_name']
                    m['away_team_name_cn'] = a_team.get('name_cn') or m['away_team_name']
                    m['home_team_logo'] = h_team.get('crest')
                    m['away_team_logo'] = a_team.get('crest')
            
            return matches
        except Exception as e:
            logger.error(f"Supabase 获取比赛失败: {e}")
            return []

    async def get_match_by_id(self, fd_id: int) -> Optional[Dict]:
        """获取单场比赛"""
        response = self.client.table('fd_matches').select("*").eq('fd_id', fd_id).maybe_single().execute()
        return response.data

    async def get_leagues(self) -> List[Dict]:
        """获取联赛列表"""
        response = self.client.table('fd_leagues').select("*").order('code').execute()
        return response.data

    async def get_teams(self, league_code: Optional[str] = None) -> List[Dict]:
        """获取球队列表"""
        if league_code:
            # 这是一个复杂的查询，因为需要关联 matches
            # 在 Supabase 中通常通过 RPC 或者先查出 team_ids
            match_res = self.client.table('fd_matches').select("home_team_id, away_team_id").eq('league_code', league_code).execute()
            team_ids = set()
            for m in match_res.data:
                team_ids.add(m['home_team_id'])
                team_ids.add(m['away_team_id'])
            
            if not team_ids: return []
            
            response = self.client.table('fd_teams').select("*").in_('fd_id', list(team_ids)).order('name').execute()
            return response.data
        else:
            response = self.client.table('fd_teams').select("*").order('name').execute()
            return response.data

    async def save_team(self, team: Dict) -> bool:
        """保存球队"""
        try:
            data = {
                'fd_id': team.get('fd_id'),
                'name': team.get('name'),
                'short_name': team.get('short_name'),
                'tla': team.get('tla'),
                'crest': team.get('crest'),
                'venue': team.get('venue'),
                'founded': team.get('founded'),
                'club_colors': team.get('club_colors'),
                'website': team.get('website'),
                'updated_at': datetime.now().isoformat()
            }
            self.client.table('fd_teams').upsert(data, on_conflict="fd_id").execute()
            return True
        except Exception as e:
            logger.error(f"Supabase 保存球队失败: {e}")
            return False

    async def save_league(self, league: Dict) -> bool:
        """保存联赛"""
        try:
            data = {
                'fd_id': league.get('fd_id'),
                'code': league.get('code'),
                'name': league.get('name'),
                'country': league.get('country'),
                'current_season': league.get('current_season'),
                'emblem': league.get('emblem'),
                'updated_at': datetime.now().isoformat()
            }
            self.client.table('fd_leagues').upsert(data, on_conflict="fd_id").execute()
            return True
        except Exception as e:
            logger.error(f"Supabase 保存联赛失败: {e}")
            return False

    async def save_scorer(self, scorer: Dict) -> bool:
        """保存射手榜"""
        try:
            data = {
                'league_code': scorer.get('league_code'),
                'season': scorer.get('season'),
                'player_id': scorer.get('player_id'),
                'player_name': scorer.get('player_name'),
                'team_id': scorer.get('team_id'),
                'team_name': scorer.get('team_name'),
                'position': scorer.get('position'),
                'goals': scorer.get('goals') or 0,
                'assists': scorer.get('assists') or 0,
                'penalties': scorer.get('penalties') or 0,
                'played_matches': scorer.get('played_matches') or 0,
                'updated_at': datetime.now().isoformat()
            }
            # 注意：scorers 表通常没有唯一约束 fd_id，所以手动处理重复
            self.client.table('fd_scorers').upsert(data, on_conflict="league_code,player_id").execute()
            return True
        except Exception as e:
            logger.error(f"Supabase 保存射手失败: {e}")
            return False

    async def get_scorers(self, league_code: str, season: Optional[int] = None, order_by: str = 'goals') -> List[Dict]:
        """获取射手榜 (附带球队中文名)"""
        try:
            query = self.client.table('fd_scorers').select("*").eq('league_code', league_code)
            if season:
                query = query.eq('season', season)
            
            if order_by == 'assists':
                query = query.order('assists', desc=True).order('goals', desc=True)
            else:
                query = query.order('goals', desc=True).order('assists', desc=True)
                
            response = query.limit(50).execute()
            scorers = response.data
            
            # 关联球队中文名
            team_ids = list(set([s['team_id'] for s in scorers]))
            if team_ids:
                teams_res = self.client.table('fd_teams').select("fd_id, name_cn").in_('fd_id', team_ids).execute()
                team_map = {t['fd_id']: t['name_cn'] for t in teams_res.data if t.get('name_cn')}
                
                for s in scorers:
                    if s['team_id'] in team_map:
                        s['team_name_cn'] = team_map[s['team_id']]
                    else:
                        s['team_name_cn'] = s['team_name']
            
            return scorers
        except Exception as e:
            logger.error(f"获取射手榜失败: {e}")
            return []

    async def save_standing(self, standing: Dict) -> bool:
        """保存积分榜"""
        try:
            data = {
                'league_code': standing.get('league_code'),
                'team_id': standing.get('team_id'),
                'team_name': standing.get('team_name'),
                'season': standing.get('season'),
                'position': standing.get('position'),
                'played_games': standing.get('played_games'),
                'won': standing.get('won'),
                'draw': standing.get('draw'),
                'lost': standing.get('lost'),
                'points': standing.get('points'),
                'goals_for': standing.get('goals_for'),
                'goals_against': standing.get('goals_against'),
                'goal_diff': standing.get('goal_diff'),
                'updated_at': datetime.now().isoformat()
            }
            self.client.table('fd_standings').upsert(data, on_conflict="league_code,team_id").execute()
            return True
        except Exception as e:
            logger.error(f"Supabase 保存积分榜失败: {e}")
            return False

    async def get_standings(self, league_code: str, season: Optional[int] = None) -> List[Dict]:
        """获取积分榜 (附带中文名)"""
        try:
            # 使用 Supabase 的外键关联查询，fk_teams 是对应的外键关系
            # 注意：在 Supabase 中需要确保 fd_standings(team_id) 关联了 fd_teams(fd_id)
            # 如果没有建立物理外键，我们在这里做个简单的手动合并
            response = self.client.table('fd_standings').select("*").eq('league_code', league_code).order('position', desc=False).execute()
            standings = response.data
            
            # 获取所有球队的中文名映射
            team_ids = [s['team_id'] for s in standings]
            if team_ids:
                teams_res = self.client.table('fd_teams').select("fd_id, name_cn").in_('fd_id', team_ids).execute()
                team_map = {t['fd_id']: t['name_cn'] for t in teams_res.data if t.get('name_cn')}
                
                for s in standings:
                    if s['team_id'] in team_map:
                        s['team_name_cn'] = team_map[s['team_id']]
                    else:
                        s['team_name_cn'] = s['team_name'] # 回退到英文名
            
            return standings
        except Exception as e:
            logger.error(f"获取积分榜失败: {e}")
            return []

    async def get_stats(self) -> Dict:
        """获取统计"""
        matches_count = self.client.table('fd_matches').select('id', count='exact').limit(1).execute().count
        return {"fd_matches": matches_count or 0}

    async def save_match_details(self, details: Dict) -> bool:
        """保存比赛详情"""
        try:
            data = {
                'match_id': details.get('match_id'),
                'home_formation': details.get('home_formation'),
                'away_formation': details.get('away_formation'),
                'home_coach_name': details.get('home_coach_name'),
                'away_coach_name': details.get('away_coach_name'),
                'home_goal_count': details.get('home_goal_count', 0),
                'away_goal_count': details.get('away_goal_count', 0),
                'home_yellow_cards': details.get('home_yellow_cards', 0),
                'away_yellow_cards': details.get('away_yellow_cards', 0),
                'home_red_cards': details.get('home_red_cards', 0),
                'away_red_cards': details.get('away_red_cards', 0),
                'details_json': details.get('details_json'),
                'updated_at': datetime.now().isoformat()
            }
            self.client.table('fd_match_details').upsert(data, on_conflict="match_id").execute()
            return True
        except Exception as e:
            logger.error(f"Supabase 保存比赛详情失败: {e}")
            return False

    async def save_match_goal(self, goal: Dict) -> bool:
        """保存进球记录"""
        try:
            data = {
                'match_id': goal.get('match_id'),
                'team_id': goal.get('team_id'),
                'team_name': goal.get('team_name'),
                'player_id': goal.get('player_id'),
                'player_name': goal.get('player_name'),
                'minute': goal.get('minute'),
                'minute_extra': goal.get('minute_extra'),
                'type': goal.get('type'),
                'home_away': goal.get('home_away'),
                'updated_at': datetime.now().isoformat()
            }
            self.client.table('fd_match_goals').insert(data).execute()
            return True
        except Exception as e:
            logger.error(f"Supabase 保存进球失败: {e}")
            return False

    async def clear_match_goals(self, match_id: int):
        """清除比赛进球记录"""
        self.client.table('fd_match_goals').delete().eq('match_id', match_id).execute()

    async def save_team_coach(self, coach: Dict) -> bool:
        """保存球队教练"""
        try:
            data = {
                'team_id': coach.get('team_id'),
                'coach_id': coach.get('coach_id'),
                'coach_name': coach.get('coach_name'),
                'first_name': coach.get('first_name'),
                'last_name': coach.get('last_name'),
                'date_of_birth': coach.get('date_of_birth'),
                'nationality': coach.get('nationality'),
                'contract_until': coach.get('contract_until'),
                'updated_at': datetime.now().isoformat()
            }
            self.client.table('fd_team_coaches').upsert(data, on_conflict="team_id").execute()
            return True
        except Exception as e:
            logger.error(f"Supabase 保存教练失败: {e}")
            return False

    async def save_team_squad(self, player: Dict) -> bool:
        """保存球队阵容球员"""
        try:
            data = {
                'team_id': player.get('team_id'),
                'player_id': player.get('player_id'),
                'player_name': player.get('player_name'),
                'position': player.get('position'),
                'shirt_number': player.get('shirt_number'),
                'nationality': player.get('nationality'),
                'date_of_birth': player.get('date_of_birth'),
                'contract_until': player.get('contract_until'),
                'season': player.get('season'),
                'updated_at': datetime.now().isoformat()
            }
            # 组合主键 (team_id, player_id) 在迁移时已有处理
            self.client.table('fd_team_squads').upsert(data).execute()
            return True
        except Exception as e:
            logger.error(f"Supabase 保存阵容失败: {e}")
            return False

    async def get_match_details(self, match_id: int) -> Optional[Dict]:
        """获取比赛详情"""
        try:
            # 1. 基础详情
            detail_res = self.client.table('fd_match_details').select("*").eq('match_id', match_id).maybe_single().execute()
            detail = detail_res.data
            if not detail: return None

            # 2. 进球
            goals_res = self.client.table('fd_match_goals').select("*").eq('match_id', match_id).order('minute').order('minute_extra').execute()
            detail['goals'] = goals_res.data

            # 3. 基础比赛信息
            match_res = self.client.table('fd_matches').select("referee").eq('fd_id', match_id).maybe_single().execute()
            if match_res.data:
                detail['referee'] = match_res.data.get('referee')

            # 4. 解析 JSON
            import json
            try:
                full_data = json.loads(detail['details_json'])
                detail['venue'] = full_data.get('venue')
                detail['lineup_home'] = full_data.get('homeTeam', {}).get('lineup', [])
                detail['lineup_away'] = full_data.get('awayTeam', {}).get('lineup', [])
            except:
                pass
            
            return detail
        except Exception as e:
            logger.error(f"Supabase 获取详情失败: {e}")
            return None

    async def get_all_team_ids(self) -> List[int]:
        """获取所有球队ID"""
        response = self.client.table('fd_teams').select("fd_id").execute()
        return [row['fd_id'] for row in response.data]

    async def get_match_ids_by_status(self, status: str) -> List[int]:
        """获取指定状态的比赛ID"""
        response = self.client.table('fd_matches').select("fd_id").eq('status', status).execute()
        return [row['fd_id'] for row in response.data]

class SportteryRepository(BaseRepository):
    """竞彩数据访问 (Supabase版)"""

    async def save_match(self, match: Dict) -> bool:
        """保存比赛"""
        try:
            data = {
                'match_code': match.get('match_code'),
                'group_date': match.get('group_date'),
                'home_team': match.get('home_team'),
                'away_team': match.get('away_team'),
                'league': match.get('league'),
                'match_time': match.get('match_time'),
                'status': match.get('status', 'pending'),
                'actual_score': match.get('actual_score'),
                'half_score': match.get('half_score'),
                'updated_at': datetime.now().isoformat()
            }
            self.client.table('sporttery_matches').upsert(data, on_conflict="match_code").execute()
            return True
        except Exception as e:
            logger.error(f"Supabase 保存竞彩数据失败: {e}")
            return False

    async def get_matches(self, date: Optional[str] = None,
                          status: Optional[str] = None,
                          limit: int = 100) -> List[Dict]:
        """获取比赛列表"""
        query = self.client.table('sporttery_matches').select("*")
        if date:
            query = query.eq('group_date', date)
        if status:
            query = query.eq('status', status.lower())
        
        response = query.order('match_time', desc=False).limit(limit).execute()
        return response.data

    async def get_stats(self) -> Dict:
        """获取统计"""
        count = self.client.table('sporttery_matches').select('id', count='exact').limit(1).execute().count
        return {"sporttery_matches": count or 0}

class LogRepository(BaseRepository):
    """日志数据访问 (Supabase版)"""

    async def log_sync(self, source: str, task_type: str, status: str,
                       records_count: int = 0, error_message: str = "",
                       retry_count: int = 0) -> int:
        """记录同步日志"""
        try:
            data = {
                'source': source,
                'task_type': task_type,
                'status': status,
                'records_count': records_count,
                'error_message': error_message,
                'retry_count': retry_count,
                'started_at': datetime.now().isoformat()
            }
            response = self.client.table('sync_logs').insert(data).execute()
            if response.data:
                return response.data[0]['id']
            return 0
        except Exception as e:
            logger.error(f"Supabase 记录日志失败: {e}")
            return 0

    async def update_log_finish(self, log_id: int):
        """更新日志完成时间"""
        if not log_id: return
        self.client.table('sync_logs').update({'finished_at': datetime.now().isoformat()}).eq('id', log_id).execute()

    async def get_logs(self, source: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """获取日志"""
        query = self.client.table('sync_logs').select("*")
        if source:
            query = query.eq('source', source)
        response = query.order('started_at', desc=True).limit(limit).execute()
        return response.data

    async def get_last_sync_time(self, source: str) -> Optional[str]:
        """获取最后同步时间"""
        response = self.client.table('sync_logs').select('started_at').eq('source', source).eq('status', 'success').order('started_at', desc=True).limit(1).execute()
        if response.data:
            return response.data[0]['started_at']
        return None
