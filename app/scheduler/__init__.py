"""
定时任务调度器
"""
import asyncio
import json
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from typing import List

from app.config import settings
from app.scrapers import FootballDataScraper, SportteryScraper, fetch_with_retry
from app.repositories import FDRepository, SportteryRepository, LogRepository

logger = logging.getLogger(__name__)


class SyncScheduler:
    """数据同步调度器"""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.fd_scraper = FootballDataScraper()
        self.sporttery_scraper = SportteryScraper()
        self.fd_repo = FDRepository()
        self.sporttery_repo = SportteryRepository()
        self.log_repo = LogRepository()

    def start(self):
        """启动调度器"""
        # Football-Data 任务
        # SCHEDULED - 赛程数据（低频，完整赛季赛程）
        self.scheduler.add_job(
            self.sync_fd_scheduled,
            'interval',
            minutes=settings.UPDATE_FD_SCHEDULED,
            id='fd_scheduled',
            name='同步FD赛程'
        )

        # FINISHED - 比赛结果（高频，获取最新比分）
        self.scheduler.add_job(
            self.sync_fd_results,
            'interval',
            minutes=settings.UPDATE_FD_RESULTS,
            id='fd_results',
            name='同步FD比赛结果'
        )

        self.scheduler.add_job(
            self.sync_fd_standings,
            'interval',
            minutes=settings.UPDATE_FD_STANDINGS,
            id='fd_standings',
            name='同步FD积分榜'
        )

        self.scheduler.add_job(
            self.sync_fd_scorers,
            'interval',
            minutes=settings.UPDATE_FD_SCORERS,
            id='fd_scorers',
            name='同步FD射手榜'
        )

        self.scheduler.add_job(
            self.sync_fd_teams,
            'interval',
            minutes=settings.UPDATE_FD_TEAMS,
            id='fd_teams',
            name='同步FD球队数据'
        )

        # 联赛信息同步（低频）
        self.scheduler.add_job(
            self.sync_fd_competitions,
            'interval',
            minutes=1440,  # 1天
            id='fd_competitions',
            name='同步FD联赛信息'
        )

        # 球队详情同步（低频 - 教练、阵容）
        self.scheduler.add_job(
            self.sync_fd_team_details,
            'interval',
            minutes=1440,  # 1天
            id='fd_team_details',
            name='同步FD球队详情'
        )

        # 比赛详情同步（高频 - 进行中比赛）
        self.scheduler.add_job(
            self.sync_fd_live_match_details,
            'interval',
            minutes=30,  # 降低频率到30分钟，因为Free Tier缺少Lineups/Events
            id='fd_live_match_details',
            name='同步FD进行中比赛详情'
        )

        # 实时比分同步（极高频 - 仅更新主表比分和状态）
        self.scheduler.add_job(
            self.sync_fd_live_scores,
            'interval',
            seconds=30,  # 每30秒同步一次实时比分 (Free Tier 允许每分钟10次请求，足够支持)
            id='fd_live_scores',
            name='同步FD实时比分'
        )

        # 竞彩任务
        self.scheduler.add_job(
            self.sync_sporttery_matches,
            'interval',
            minutes=settings.UPDATE_SPORTTERY,
            id='sporttery_matches',
            name='同步竞彩比赛数据'
        )

        self.scheduler.start()
        logger.info("调度器已启动")

        # 打印任务列表
        jobs = self.scheduler.get_jobs()
        logger.info(f"已注册 {len(jobs)} 个定时任务:")
        for job in jobs:
            logger.info(f"  - {job.name} ({job.id})")

    def stop(self):
        """停止调度器"""
        self.scheduler.shutdown()
        logger.info("调度器已停止")

    async def _log_task(self, source: str, task_type: str,
                       func, max_retries: int = 3) -> int:
        """执行任务并记录日志"""
        log_id = await self.log_repo.log_sync(source, task_type, "running")
        records_count = 0
        error_message = ""

        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    await self.log_repo.log_sync(
                        source, task_type, "retrying",
                        retry_count=attempt
                    )
                    await asyncio.sleep(2 ** attempt)

                records_count = await func()
                await self.log_repo.update_log_finish(log_id)
                await self.log_repo.log_sync(
                    source, task_type, "success",
                    records_count=records_count
                )
                return records_count

            except Exception as e:
                error_message = str(e)
                logger.error(f"{source}.{task_type} 失败 (尝试 {attempt + 1}/{max_retries}): {e}")

        # 全部失败
        await self.log_repo.update_log_finish(log_id)
        await self.log_repo.log_sync(
            source, task_type, "failed",
            error_message=error_message, retry_count=max_retries
        )
        return 0

    async def sync_fd_scheduled(self):
        """同步 FD 即将进行的比赛（完整赛季赛程）"""
        async def task():
            logger.info("开始同步 FD 赛程数据...")
            total = 0

            for league in settings.monitored_leagues_list:
                # 获取 SCHEDULED 和 TIMED 状态的比赛
                for status in ["SCHEDULED", "TIMED"]:
                    matches = await self.fd_scraper.get_matches(
                        competition=league,
                        status=status
                    )

                    for match in matches:
                        season = match.get('season', {})
                        await self.fd_repo.save_match({
                            'fd_id': match.get('id'),
                            'league_code': league,
                            'home_team_id': match.get('homeTeam', {}).get('id'),
                            'away_team_id': match.get('awayTeam', {}).get('id'),
                            'home_team_name': match.get('homeTeam', {}).get('name'),
                            'away_team_name': match.get('awayTeam', {}).get('name'),
                            'match_date': match.get('utcDate'),
                            'status': match.get('status'),
                            'home_score': None,
                            'away_score': None,
                            'home_half_score': None,
                            'away_half_score': None,
                            'referee': None,
                            'attendance': None,
                            'matchday': match.get('matchday'),
                            'season': season.get('id') if isinstance(season, dict) else season
                        })
                        total += 1

                # 避免API限流
                await asyncio.sleep(1)

            logger.info(f"FD 赛程同步完成: {total} 场")
            return total

        return await self._log_task("football_data", "scheduled", task)

    async def sync_fd_standings(self):
        """同步 FD 积分榜"""
        async def task():
            logger.info("开始同步 FD 积分榜...")
            total = 0

            for league in settings.monitored_leagues_list:
                standings_data = await self.fd_scraper.get_standings(league)

                # standings_data 可能是列表或字典
                tables = []
                if isinstance(standings_data, list):
                    tables = standings_data
                elif isinstance(standings_data, dict):
                    tables = standings_data.get('standings', [])

                for table in tables:
                    # table 可能是列表或字典
                    team_list = []
                    if isinstance(table, dict):
                        team_list = table.get('table', [])
                    elif isinstance(table, list):
                        team_list = table

                    for team in team_list:
                        team_data = team.get('team') if isinstance(team, dict) else team
                        if not isinstance(team_data, dict):
                            continue

                        await self.fd_repo.save_standing({
                            'league_code': league,
                            'team_id': team_data.get('id'),
                            'team_name': team_data.get('name'),
                            'position': team.get('position'),
                            'played_games': team.get('playedGames'),
                            'won': team.get('won'),
                            'draw': team.get('draw'),
                            'lost': team.get('lost'),
                            'points': team.get('points'),
                            'goals_for': team.get('goalsFor'),
                            'goals_against': team.get('goalsAgainst'),
                            'goal_diff': team.get('goalDifference')
                        })
                        total += 1

                await asyncio.sleep(1)

            logger.info(f"FD 积分榜同步完成: {total} 条")
            return total

        return await self._log_task("football_data", "standings", task)

    async def sync_fd_results(self):
        """同步 FD 已结束的比赛结果（包含详情）"""
        async def task():
            logger.info("开始同步 FD 比赛结果...")
            total = 0

            for league in settings.monitored_leagues_list:
                # 获取最近的已结束比赛（limit=100 足够覆盖最近几天）
                matches = await self.fd_scraper.get_matches(
                    competition=league,
                    status="FINISHED",
                    limit=100
                )

                for match in matches:
                    score = match.get('score', {})
                    full_time = score.get('fullTime', {})
                    half_time = score.get('halfTime', {})
                    season = match.get('season', {})

                    await self.fd_repo.save_match({
                        'fd_id': match.get('id'),
                        'league_code': league,
                        'home_team_id': match.get('homeTeam', {}).get('id'),
                        'away_team_id': match.get('awayTeam', {}).get('id'),
                        'home_team_name': match.get('homeTeam', {}).get('name'),
                        'away_team_name': match.get('awayTeam', {}).get('name'),
                        'match_date': match.get('utcDate'),
                        'status': match.get('status'),
                        'home_score': full_time.get('home'),
                        'away_score': full_time.get('away'),
                        'home_half_score': half_time.get('home'),
                        'away_half_score': half_time.get('away'),
                        'referee': match.get('referee', {}).get('name') if match.get('referee') else None,
                        'attendance': match.get('attendance'),
                        'matchday': match.get('matchday'),
                        'season': season.get('id') if isinstance(season, dict) else season
                    })
                    total += 1

                await asyncio.sleep(1)

            logger.info(f"FD 比赛结果同步完成: {total} 场")
            return total

        return await self._log_task("football_data", "results", task)

    async def sync_fd_teams(self):
        """同步 FD 球队数据（完整详情）"""
        async def task():
            logger.info("开始同步 FD 球队数据...")
            total = 0

            for league in settings.monitored_leagues_list:
                teams = await self.fd_scraper.get_teams(competition=league)

                for team in teams:
                    team_id = team.get('id')
                    team_name = team.get('name')

                    # 保存基础信息
                    await self.fd_repo.save_team({
                        'fd_id': team_id,
                        'name': team_name,
                        'short_name': team.get('shortName'),
                        'tla': team.get('tla'),
                        'crest': team.get('crest'),
                        'venue': team.get('venue'),
                        'founded': team.get('founded'),
                        'club_colors': team.get('clubColors'),
                        'website': team.get('website')
                    })
                    total += 1

                await asyncio.sleep(1)

            logger.info(f"FD 球队同步完成: {total} 支")
            return total

        return await self._log_task("football_data", "teams", task)

    async def sync_fd_scorers(self):
        """同步 FD 射手榜"""
        async def task():
            logger.info("开始同步 FD 射手榜...")
            total = 0

            for league in settings.monitored_leagues_list:
                scorers = await self.fd_scraper.get_scorers(league, limit=100)

                for pos_idx, scorer in enumerate(scorers):
                    player = scorer.get('player', {})
                    team = scorer.get('team', {})
                    await self.fd_repo.save_scorer({
                        'league_code': league,
                        'season': scorer.get('season', {}).get('id') if isinstance(scorer.get('season'), dict) else scorer.get('season'), # Fix season access too if needed, but scraper output shows it might be root or nested. API usually has season at root of response, not scorer. Wait, scraper.get_scorers returns list of scorers.
                        # Actually looking at debug output context, we didn't see season in the scorer keys. It is usually a parent key. 
                        # Let's check debug output again.
                        # keys: ['player', 'team', 'playedMatches', 'goals', 'assists', 'penalties']
                        # Season information usually comes from the 'season' key in the wrapper response, not the individual scorer item.
                        # But get_scorers in scraper returns data.get("scorers", []). The season info is lost from the list items.
                        # However, the scheduler passes 'league' (competition code).
                        # We might needed season to save it.
                        # FDRepository.save_scorer expects 'season'.
                        # If the scraper doesn't pass it, we might be saving NULL or old season.
                        
                        # Let's verify scraper first. scraper.get_scorers returns just the list. 
                        # I should probably update scraper to return the season too or just pass None and let repo handle it (Repo uses MAX(id) so maybe okay).
                        # But wait, lines 352 uses scorer.get('season'). If it's not in keys, it's None.
                        
                        # In the original code (lines 352), it was scorer.get('season').
                        # New plan: Use what we have. API keys are goals, assists, penalties, playedMatches.
                        
                        'league_code': league,
                        'season': None, # Scorer item doesn't have season usually.
                        'player_id': player.get('id'),
                        'player_name': player.get('name'),
                        'team_id': team.get('id'),
                        'team_name': team.get('name'),
                        'position': pos_idx + 1,
                        'goals': scorer.get('goals', 0),
                        'assists': scorer.get('assists', 0),
                        'penalties': scorer.get('penalties', 0),
                        'played_matches': scorer.get('playedMatches', 0)
                    })
                    total += 1

                await asyncio.sleep(1)

            logger.info(f"FD 射手榜同步完成: {total} 条")
            return total

        return await self._log_task("football_data", "scorers", task)

    async def sync_sporttery_matches(self):
        """同步竞彩比赛数据"""
        async def task():
            logger.info("开始同步竞彩比赛数据...")

            matches = await self.sporttery_scraper.get_matches()
            total = 0

            for match in matches:
                await self.sporttery_repo.save_match(match)
                total += 1

            logger.info(f"竞彩比赛同步完成: {total} 场")
            return total

        return await self._log_task("sporttery", "matches", task)

    async def sync_fd_competitions(self):
        """同步 FD 联赛列表和详情"""
        async def task():
            logger.info("开始同步 FD 联赛信息...")
            total = 0

            # 获取所有联赛
            competitions = await self.fd_scraper.get_competitions()

            for comp in competitions:
                # 获取每个联赛的详情
                detail = await self.fd_scraper.get_competition(comp.get('code'))

                await self.fd_repo.save_league({
                    'fd_id': detail.get('id'),
                    'code': detail.get('code'),
                    'name': detail.get('name'),
                    'country': detail.get('area', {}).get('name') if detail.get('area') else None,
                    'current_season': detail.get('season', {}).get('id') if detail.get('season') else None,
                    'emblem': detail.get('emblem')
                })
                total += 1
                await asyncio.sleep(6)  # 遵守10次/分钟限制

            logger.info(f"FD 联赛信息同步完成: {total} 个")
            return total

        return await self._log_task("football_data", "competitions", task)

    async def sync_fd_team_details(self):
        """同步每支球队的详细信息（教练、阵容）"""
        async def task():
            logger.info("开始同步 FD 球队详情...")
            total_teams = 0
            total_squad = 0

            # 获取所有球队ID
            team_ids = await self.fd_repo.get_all_team_ids()
            logger.info(f"需要同步 {len(team_ids)} 支球队的详情")

            for team_id in team_ids:
                try:
                    detail = await self.fd_scraper.get_team(team_id)

                    # 保存教练信息
                    coach = detail.get('coach')
                    if coach:
                        await self.fd_repo.save_team_coach({
                            'team_id': team_id,
                            'coach_id': coach.get('id'),
                            'coach_name': coach.get('name'),
                            'first_name': coach.get('firstName'),
                            'last_name': coach.get('lastName'),
                            'date_of_birth': coach.get('dateOfBirth'),
                            'nationality': coach.get('nationality'),
                            'contract_until': coach.get('contract', {}).get('until') if coach.get('contract') else None
                        })

                    # 保存阵容
                    season = detail.get('squad', [{}])[0].get('contract', {}).get('until', '').split('-')[0] if detail.get('squad') else datetime.now().year
                    squad = detail.get('squad', [])

                    for player in squad:
                        contract = player.get('contract', {})
                        await self.fd_repo.save_team_squad({
                            'team_id': team_id,
                            'player_id': player.get('id'),
                            'player_name': player.get('name'),
                            'position': player.get('position'),
                            'shirt_number': player.get('shirtNumber'),
                            'nationality': player.get('nationality'),
                            'date_of_birth': player.get('dateOfBirth'),
                            'contract_until': contract.get('until') if contract else None,
                            'season': int(season) if season else datetime.now().year
                        })
                        total_squad += 1

                    total_teams += 1
                    await asyncio.sleep(6)  # 遵守10次/分钟限制

                    if total_teams % 10 == 0:
                        logger.info(f"已同步 {total_teams}/{len(team_ids)} 支球队")

                except Exception as e:
                    logger.error(f"同步球队 {team_id} 详情失败: {e}")

            logger.info(f"FD 球队详情同步完成: {total_teams} 支球队, {total_squad} 名球员")
            return total_teams

        return await self._log_task("football_data", "team_details", task)

    async def sync_fd_live_match_details(self):
        """同步进行中和最近结束比赛的详情（阵容、进球、红黄牌）"""
        async def task():
            logger.info("开始同步 FD 比赛详情...")
            total = 0

            # 获取进行中 (LIVE) 和最近结束 (FINISHED) 的比赛
            live_ids = await self.fd_repo.get_match_ids_by_status('IN_PLAY')
            paused_ids = await self.fd_repo.get_match_ids_by_status('PAUSED')
            finished_ids = await self.fd_repo.get_match_ids_by_status('FINISHED')

            # 优先同步进行中的比赛
            match_ids = live_ids + paused_ids

            # 如果没有进行中的比赛，同步最近10场已结束的
            if not match_ids:
                match_ids = finished_ids[:10]

            logger.info(f"需要同步 {len(match_ids)} 场比赛的详情")

            for match_id in match_ids:
                try:
                    detail = await self.fd_scraper.get_match(match_id)

                    # 保存比赛详情
                    home_coach = detail.get('homeTeam', {}).get('coach', {})
                    away_coach = detail.get('awayTeam', {}).get('coach', {})

                    match_info = {
                        'match_id': match_id,
                        'home_formation': None,
                        'away_formation': None,
                        'home_coach_name': home_coach.get('name') if home_coach else None,
                        'away_coach_name': away_coach.get('name') if away_coach else None,
                        'home_goal_count': 0,
                        'away_goal_count': 0,
                        'home_yellow_cards': 0,
                        'away_yellow_cards': 0,
                        'home_red_cards': 0,
                        'away_red_cards': 0,
                        'details_json': json.dumps(detail) if detail else None
                    }

                    # 统计数据
                    home_team_id = detail.get('homeTeam', {}).get('id')
                    away_team_id = detail.get('awayTeam', {}).get('id')

                    # 清除旧进球记录
                    await self.fd_repo.clear_match_goals(match_id)

                    # 处理进球
                    for goal in detail.get('goals', []):
                        team_id = goal.get('team', {}).get('id')
                        team_name = goal.get('team', {}).get('name')
                        player_id = goal.get('scorer', {}).get('id') if goal.get('scorer') else None
                        player_name = goal.get('scorer', {}).get('name') if goal.get('scorer') else 'Unknown'

                        # 确定是主队还是客队进球
                        home_away = 'home' if team_id == home_team_id else 'away'

                        await self.fd_repo.save_match_goal({
                            'match_id': match_id,
                            'team_id': team_id,
                            'team_name': team_name,
                            'player_id': player_id,
                            'player_name': player_name,
                            'minute': goal.get('minute', [0])[0] if isinstance(goal.get('minute'), list) else goal.get('minute', 0),
                            'minute_extra': goal.get('minute', [0, 0])[1] if isinstance(goal.get('minute'), list) and len(goal.get('minute', [])) > 1 else None,
                            'type': goal.get('type', 'goal'),
                            'home_away': home_away
                        })

                        # 统计进球数
                        if home_away == 'home':
                            match_info['home_goal_count'] += 1
                        else:
                            match_info['away_goal_count'] += 1

                    await self.fd_repo.save_match_details(match_info)
                    total += 1
                    await asyncio.sleep(6)  # 遵守10次/分钟限制

                except Exception as e:
                    logger.error(f"同步比赛 {match_id} 详情失败: {e}")

            logger.info(f"FD 比赛详情同步完成: {total} 场")
            return total

        return await self._log_task("football_data", "match_details", task)

    async def sync_fd_live_scores(self):
        """同步 FD 实时比赛比分和状态（仅同步主表）"""
        async def task():
            logger.info("开始同步 FD 实时比分...")
            total = 0

            # 抓取所有进行中的比赛
            matches = await self.fd_scraper.get_matches(status="LIVE")
            # 如果 LIVE 没数据，尝试 IN_PLAY (API 文档中有时互换)
            if not matches:
                matches = await self.fd_scraper.get_matches(status="IN_PLAY")

            for match in matches:
                league_code = match.get('competition', {}).get('code')
                if league_code not in settings.monitored_leagues_list:
                    continue

                score = match.get('score', {})
                full_time = score.get('fullTime', {})
                half_time = score.get('halfTime', {})
                season = match.get('season', {})

                await self.fd_repo.save_match({
                    'fd_id': match.get('id'),
                    'league_code': league_code,
                    'home_team_id': match.get('homeTeam', {}).get('id'),
                    'away_team_id': match.get('awayTeam', {}).get('id'),
                    'home_team_name': match.get('homeTeam', {}).get('name'),
                    'away_team_name': match.get('awayTeam', {}).get('name'),
                    'match_date': match.get('utcDate'),
                    'status': match.get('status'),
                    'home_score': full_time.get('home'),
                    'away_score': full_time.get('away'),
                    'home_half_score': half_time.get('home'),
                    'away_half_score': half_time.get('away'),
                    'referee': match.get('referee', {}).get('name') if match.get('referee') else None,
                    'attendance': match.get('attendance'),
                    'matchday': match.get('matchday'),
                    'season': season.get('id') if isinstance(season, dict) else season
                })
                total += 1

            logger.info(f"FD 实时比分同步完成: {total} 场")
            return total

        return await self._log_task("football_data", "live_scores", task)


# 全局调度器实例
scheduler = SyncScheduler()
