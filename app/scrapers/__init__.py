"""
数据抓取器
"""
import aiohttp
import asyncio
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from app.config import settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """API 限流器"""

    def __init__(self, max_calls: int = 10, window: int = 60):
        self.max_calls = max_calls
        self.window = window
        self.calls = []

    async def acquire(self):
        """获取调用许可"""
        while True:
            now = asyncio.get_event_loop().time()
            # 清理窗口外的记录
            self.calls = [t for t in self.calls if now - t < self.window]

            if len(self.calls) < self.max_calls:
                self.calls.append(now)
                return

            # 等待
            wait_time = self.window - (now - self.calls[0]) + 0.1
            await asyncio.sleep(wait_time)


class FootballDataScraper:
    """Football-Data.org 数据抓取器"""

    def __init__(self, api_token: str = None):
        self.api_token = api_token or settings.FD_API_TOKEN
        self.base_url = "https://api.football-data.org/v4"
        self.limiter = RateLimiter(settings.FD_RATE_LIMIT, settings.FD_RATE_WINDOW)

    def _headers(self):
        return {"X-Auth-Token": self.api_token}

    async def _get(self, endpoint: str) -> Dict:
        """发送 GET 请求"""
        await self.limiter.acquire()

        url = f"{self.base_url}{endpoint}"
        logger.info(f"请求 Football-Data API: {endpoint}")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self._headers()) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 404:
                        logger.warning(f"资源不存在: {endpoint}")
                        return {}
                    elif response.status == 429:
                        logger.warning("请求超限，等待后重试...")
                        await asyncio.sleep(60)
                        return await self._get(endpoint)
                    else:
                        text = await response.text()
                        logger.error(f"API请求失败: {response.status} - {text}")
                        return {}
        except Exception as e:
            logger.error(f"请求异常: {e}")
            return {}

    async def get_matches(self, competition: str = None,
                         status: str = "SCHEDULED",
                         limit: int = None) -> List[Dict]:
        """获取比赛"""
        if competition:
            endpoint = f"/competitions/{competition}/matches?status={status}"
            if limit:
                endpoint += f"&limit={limit}"
        else:
            endpoint = f"/matches?status={status}"
            if limit:
                endpoint += f"&limit={limit}"

        data = await self._get(endpoint)
        return data.get("matches", [])

    async def get_match(self, match_id: int) -> Optional[Dict]:
        """获取单场比赛详情"""
        endpoint = f"/matches/{match_id}"
        return await self._get(endpoint)

    async def get_competitions(self) -> List[Dict]:
        """获取所有联赛"""
        endpoint = "/competitions"
        data = await self._get(endpoint)
        return data.get("competitions", [])

    async def get_competition(self, competition_id: int) -> Dict:
        """获取单个联赛详情"""
        endpoint = f"/competitions/{competition_id}"
        return await self._get(endpoint)

    async def get_scorers(self, competition: str, limit: int = None) -> tuple[List[Dict], Dict]:
        """获取射手榜"""
        endpoint = f"/competitions/{competition}/scorers"
        if limit:
            endpoint += f"?limit={limit}"
        data = await self._get(endpoint)
        return data.get("scorers", []), data.get("season", {})

    async def get_standings(self, competition: str) -> tuple[List, Dict]:
        """获取积分榜"""
        endpoint = f"/competitions/{competition}/standings"
        data = await self._get(endpoint)
        # API直接返回列表，不是字典 (Some endpoints might, but standard is dict)
        if isinstance(data, list):
            return data, {}
        # 备用：如果是字典，取standings字段
        return data.get("standings", []), data.get("season", {})

    async def get_teams(self, competition: str, limit: int = 100) -> List[Dict]:
        """获取联赛球队"""
        endpoint = f"/competitions/{competition}/teams?limit={limit}"
        data = await self._get(endpoint)
        return data.get("teams", [])

    async def get_team(self, team_id: int) -> Dict:
        """获取球队详情"""
        endpoint = f"/teams/{team_id}"
        return await self._get(endpoint)

    async def get_team_matches(self, team_id: int, limit: int = 10) -> List[Dict]:
        """获取球队比赛"""
        endpoint = f"/teams/{team_id}/matches?limit={limit}"
        data = await self._get(endpoint)
        return data.get("matches", [])


class SportteryScraper:
    """竞彩官网数据抓取器"""

    API_URL = "https://webapi.sporttery.cn/gateway/uniform/football/getMatchListV1.qry?clientCode=3001"
    RESULT_API_URL = "https://webapi.sporttery.cn/gateway/uniform/football/getUniformMatchResultV1.qry?matchPage=0"

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://www.sporttery.cn/',
            'Origin': 'https://www.sporttery.cn'
        }

    async def get_matches(self) -> List[Dict]:
        """获取所有比赛"""
        logger.info("请求竞彩官网 API")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.API_URL, headers=self.headers,
                                      timeout=aiohttp.ClientTimeout(total=15)) as response:
                    if response.status != 200:
                        logger.error(f"竞彩API返回状态: {response.status}")
                        return []

                    data = await response.json()

                    if not data.get('success') and data.get('errorCode') != '0':
                        logger.error(f"竞彩API返回失败: {data}")
                        return []

                    match_groups = data.get('value', {}).get('matchInfoList', [])
                    matches = []

                    for group in match_groups:
                        business_date = group.get('businessDate')

                        for item in group.get('subMatchList', []):
                            match_data = self._parse_match(item, business_date)
                            if match_data:
                                matches.append(match_data)

                    logger.info(f"竞彩API获取到 {len(matches)} 场比赛")
                    return matches

        except asyncio.TimeoutError:
            logger.error("竞彩API请求超时")
            return []
        except Exception as e:
            logger.error(f"竞彩API请求失败: {e}")
            return []

    async def get_match_results(self) -> List[Dict]:
        """使用高级接口获取最近3天的全量比分结果 (单次100场)"""
        logger.info("请求竞彩高级结果 API (3日动态窗口)")
        
        # 动态计算日期范围：今天及前3天
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
        
        # 使用 pageSize=100 确保覆盖周末高峰
        api_url = f"https://webapi.sporttery.cn/gateway/uniform/football/getUniformMatchResultV1.qry?matchBeginDate={start_date}&matchEndDate={end_date}&leagueId=&pageSize=100&pageNo=1&isFix=0&matchPage=1&pcOrWap=1"
        
        results = []
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, headers=self.headers,
                                      timeout=aiohttp.ClientTimeout(total=15)) as response:
                    if response.status != 200:
                        logger.error(f"竞彩高级结果API返回状态: {response.status}")
                        return []

                    data = await response.json()
                    if not data.get('success'):
                        logger.error(f"竞彩高级结果API返回失败: {data}")
                        return []

                    match_list = data.get('value', {}).get('matchResult', [])
                    for item in match_list:
                        results.append({
                            'match_code': item.get('matchNumStr'),
                            'home_team': item.get('homeTeam'),
                            'away_team': item.get('awayTeam'),
                            'group_date': item.get('matchDate'),
                            'actual_score': item.get('sectionsNo999'),
                            'half_score': item.get('sectionsNo1'),
                            'status': 'finished'
                        })
                
                logger.info(f"竞彩高级结果API共获取到 {len(results)} 场比分")
                return results

        except Exception as e:
            logger.error(f"竞彩高级结果API请求失败: {e}")
            return results

    def _parse_match(self, item: Dict, business_date: str) -> Optional[Dict]:
        """解析单场比赛"""
        try:
            match_code = item.get('matchNumStr')
            if not match_code:
                week = item.get('week', '')
                num = item.get('num', '')
                match_code = f"{week}{num}" if week and num else str(item.get('matchId', ''))

            home_score = item.get('homeScore')
            away_score = item.get('awayScore')
            actual_score = None
            status = 'pending'

            if home_score is not None and away_score is not None:
                actual_score = f"{home_score}-{away_score}"
                status = 'finished'

            match_date = item.get('matchDate', '')
            match_time = item.get('matchTime', '')

            return {
                'match_code': match_code,
                'group_date': business_date,
                'home_team': item.get('homeTeamAbbName', '未知主队'),
                'away_team': item.get('awayTeamAbbName', '未知客队'),
                'league': item.get('leagueAbbName', '未知联赛'),
                'match_time': f"{match_date} {match_time}" if match_date and match_time else "",
                'status': status,
                'actual_score': actual_score,
                'half_score': item.get('halfScore', ''),
            }
        except Exception as e:
            logger.error(f"解析比赛失败: {e}")
            return None


async def fetch_with_retry(func, max_retries: int = 3):
    """带重试的抓取"""
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            wait = 2 ** attempt
            logger.warning(f"重试 {attempt + 1}/{max_retries}, 等待 {wait}秒")
            await asyncio.sleep(wait)
