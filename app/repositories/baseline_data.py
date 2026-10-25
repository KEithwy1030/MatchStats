"""
MatchStats Baseline Data
用于当 Supabase 云数据库离线、未初始化或冷启动时的高可用降级数据支撑。
确保 to B 落地页和演示看板永远具备可用、完整、美观的欧洲主流联赛数据展示。
"""

import os
import json
from typing import List, Dict

BASELINE_SPORTTERY_MATCHES: List[Dict] = []
try:
    _json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "sporttery_baseline.json")
    if os.path.exists(_json_path):
        with open(_json_path, "r", encoding="utf-8") as f:
            BASELINE_SPORTTERY_MATCHES = json.load(f)
except Exception:
    pass

BASELINE_LEAGUES = [
    {"code": "PL", "name": "英超 Premier League", "country": "英格兰", "current_season": 2026},
    {"code": "PD", "name": "西甲 La Liga", "country": "西班牙", "current_season": 2026},
    {"code": "BL1", "name": "德甲 Bundesliga", "country": "德国", "current_season": 2026},
    {"code": "SA", "name": "意甲 Serie A", "country": "意大利", "current_season": 2026},
    {"code": "FL1", "name": "法甲 Ligue 1", "country": "法国", "current_season": 2026},
    {"code": "CL", "name": "欧冠 UEFA Champions League", "country": "欧洲", "current_season": 2026},
]

# 英超积分榜基线
BASELINE_STANDINGS: Dict[str, List[Dict]] = {
    "PL": [
        {"position": 1, "team_id": 65, "team_name": "Manchester City FC", "team_name_cn": "曼城", "played_games": 9, "won": 7, "draw": 2, "lost": 0, "points": 23, "goals_for": 20, "goals_against": 9, "goal_diff": 11, "league_code": "PL", "season": 2026},
        {"position": 2, "team_id": 64, "team_name": "Liverpool FC", "team_name_cn": "利物浦", "played_games": 9, "won": 7, "draw": 1, "lost": 1, "points": 22, "goals_for": 17, "goals_against": 5, "goal_diff": 12, "league_code": "PL", "season": 2026},
        {"position": 3, "team_id": 57, "team_name": "Arsenal FC", "team_name_cn": "阿森纳", "played_games": 9, "won": 5, "draw": 3, "lost": 1, "points": 18, "goals_for": 17, "goals_against": 10, "goal_diff": 7, "league_code": "PL", "season": 2026},
        {"position": 4, "team_id": 58, "team_name": "Aston Villa FC", "team_name_cn": "阿斯顿维拉", "played_games": 9, "won": 5, "draw": 3, "lost": 1, "points": 18, "goals_for": 16, "goals_against": 11, "goal_diff": 5, "league_code": "PL", "season": 2026},
        {"position": 5, "team_id": 61, "team_name": "Chelsea FC", "team_name_cn": "切尔西", "played_games": 9, "won": 5, "draw": 2, "lost": 2, "points": 17, "goals_for": 19, "goals_against": 11, "goal_diff": 8, "league_code": "PL", "season": 2026},
        {"position": 6, "team_id": 73, "team_name": "Tottenham Hotspur FC", "team_name_cn": "热刺", "played_games": 9, "won": 4, "draw": 1, "lost": 4, "points": 13, "goals_for": 18, "goals_against": 10, "goal_diff": 8, "league_code": "PL", "season": 2026},
        {"position": 7, "team_id": 397, "team_name": "Brighton & Hove Albion FC", "team_name_cn": "布莱顿", "played_games": 9, "won": 4, "draw": 4, "lost": 1, "points": 16, "goals_for": 16, "goals_against": 12, "goal_diff": 4, "league_code": "PL", "season": 2026},
        {"position": 8, "team_id": 67, "team_name": "Newcastle United FC", "team_name_cn": "纽卡斯尔联", "played_games": 9, "won": 3, "draw": 3, "lost": 3, "points": 12, "goals_for": 9, "goals_against": 10, "goal_diff": -1, "league_code": "PL", "season": 2026},
        {"position": 9, "team_id": 66, "team_name": "Manchester United FC", "team_name_cn": "曼联", "played_games": 9, "won": 3, "draw": 2, "lost": 4, "points": 11, "goals_for": 8, "goals_against": 11, "goal_diff": -3, "league_code": "PL", "season": 2026},
        {"position": 10, "team_id": 402, "team_name": "Brentford FC", "team_name_cn": "布伦特福德", "played_games": 9, "won": 4, "draw": 1, "lost": 4, "points": 13, "goals_for": 18, "goals_against": 18, "goal_diff": 0, "league_code": "PL", "season": 2026},
    ],
    "PD": [
        {"position": 1, "team_id": 81, "team_name": "FC Barcelona", "team_name_cn": "巴塞罗那", "played_games": 11, "won": 10, "draw": 0, "lost": 1, "points": 30, "goals_for": 37, "goals_against": 10, "goal_diff": 27, "league_code": "PD", "season": 2026},
        {"position": 2, "team_id": 86, "team_name": "Real Madrid CF", "team_name_cn": "皇家马德里", "played_games": 11, "won": 7, "draw": 3, "lost": 1, "points": 24, "goals_for": 21, "goals_against": 11, "goal_diff": 10, "league_code": "PD", "season": 2026},
        {"position": 3, "team_id": 78, "team_name": "Atlético de Madrid", "team_name_cn": "马德里竞技", "played_games": 11, "won": 5, "draw": 5, "lost": 1, "points": 20, "goals_for": 16, "goals_against": 7, "goal_diff": 9, "league_code": "PD", "season": 2026},
        {"position": 4, "team_id": 94, "team_name": "Villarreal CF", "team_name_cn": "比利亚雷亚尔", "played_games": 11, "won": 6, "draw": 3, "lost": 2, "points": 21, "goals_for": 20, "goals_against": 19, "goal_diff": 1, "league_code": "PD", "season": 2026},
        {"position": 5, "team_id": 77, "team_name": "Athletic Club", "team_name_cn": "毕尔巴鄂竞技", "played_games": 11, "won": 5, "draw": 3, "lost": 3, "points": 18, "goals_for": 17, "goals_against": 11, "goal_diff": 6, "league_code": "PD", "season": 2026},
    ],
    "BL1": [
        {"position": 1, "team_id": 5, "team_name": "FC Bayern München", "team_name_cn": "拜仁慕尼黑", "played_games": 8, "won": 6, "draw": 2, "lost": 0, "points": 20, "goals_for": 29, "goals_against": 7, "goal_diff": 22, "league_code": "BL1", "season": 2026},
        {"position": 2, "team_id": 721, "team_name": "RB Leipzig", "team_name_cn": "莱比锡红牛", "played_games": 8, "won": 6, "draw": 2, "lost": 0, "points": 20, "goals_for": 14, "goals_against": 3, "goal_diff": 11, "league_code": "BL1", "season": 2026},
        {"position": 3, "team_id": 3, "team_name": "Bayer 04 Leverkusen", "team_name_cn": "勒沃库森", "played_games": 8, "won": 4, "draw": 3, "lost": 1, "points": 15, "goals_for": 20, "goals_against": 15, "goal_diff": 5, "league_code": "BL1", "season": 2026},
        {"position": 4, "team_id": 4, "team_name": "Borussia Dortmund", "team_name_cn": "多特蒙德", "played_games": 8, "won": 4, "draw": 1, "lost": 3, "points": 13, "goals_for": 15, "goals_against": 14, "goal_diff": 1, "league_code": "BL1", "season": 2026},
    ],
    "SA": [
        {"position": 1, "team_id": 113, "team_name": "SSC Napoli", "team_name_cn": "那不勒斯", "played_games": 9, "won": 7, "draw": 1, "lost": 1, "points": 22, "goals_for": 16, "goals_against": 5, "goal_diff": 11, "league_code": "SA", "season": 2026},
        {"position": 2, "team_id": 108, "team_name": "FC Internazionale Milano", "team_name_cn": "国际米兰", "played_games": 9, "won": 5, "draw": 3, "lost": 1, "points": 18, "goals_for": 21, "goals_against": 13, "goal_diff": 8, "league_code": "SA", "season": 2026},
        {"position": 3, "team_id": 109, "team_name": "Juventus FC", "team_name_cn": "尤文图斯", "played_games": 9, "won": 4, "draw": 5, "lost": 0, "points": 17, "goals_for": 15, "goals_against": 5, "goal_diff": 10, "league_code": "SA", "season": 2026},
        {"position": 4, "team_id": 102, "team_name": "Atalanta BC", "team_name_cn": "亚特兰大", "played_games": 9, "won": 5, "draw": 1, "lost": 3, "points": 16, "goals_for": 24, "goals_against": 14, "goal_diff": 10, "league_code": "SA", "season": 2026},
    ],
    "FL1": [
        {"position": 1, "team_id": 524, "team_name": "Paris Saint-Germain FC", "team_name_cn": "巴黎圣日耳曼", "played_games": 9, "won": 7, "draw": 2, "lost": 0, "points": 23, "goals_for": 28, "goals_against": 8, "goal_diff": 20, "league_code": "FL1", "season": 2026},
        {"position": 2, "team_id": 548, "team_name": "AS Monaco FC", "team_name_cn": "摩纳哥", "played_games": 9, "won": 6, "draw": 2, "lost": 1, "points": 20, "goals_for": 15, "goals_against": 6, "goal_diff": 9, "league_code": "FL1", "season": 2026},
        {"position": 3, "team_id": 516, "team_name": "Olympique de Marseille", "team_name_cn": "马赛", "played_games": 9, "won": 5, "draw": 2, "lost": 2, "points": 17, "goals_for": 21, "goals_against": 11, "goal_diff": 10, "league_code": "FL1", "season": 2026},
    ]
}

# 射手榜基线
BASELINE_SCORERS: Dict[str, List[Dict]] = {
    "PL": [
        {"player_id": 38101, "player_name": "Erling Haaland", "team_id": 65, "team_name": "Manchester City FC", "team_name_cn": "曼城", "goals": 11, "assists": 0, "penalties": 1, "played_matches": 9, "league_code": "PL", "season": 2026},
        {"player_id": 100727, "player_name": "Cole Palmer", "team_id": 61, "team_name": "Chelsea FC", "team_name_cn": "切尔西", "goals": 7, "assists": 5, "penalties": 1, "played_matches": 9, "league_code": "PL", "season": 2026},
        {"player_id": 3754, "player_name": "Mohamed Salah", "team_id": 64, "team_name": "Liverpool FC", "team_name_cn": "利物浦", "goals": 6, "assists": 5, "penalties": 1, "played_matches": 9, "league_code": "PL", "season": 2026},
        {"player_id": 13358, "player_name": "Bryan Mbeumo", "team_id": 402, "team_name": "Brentford FC", "team_name_cn": "布伦特福德", "goals": 8, "assists": 1, "penalties": 1, "played_matches": 9, "league_code": "PL", "season": 2026},
        {"player_id": 7892, "player_name": "Ollie Watkins", "team_id": 58, "team_name": "Aston Villa FC", "team_name_cn": "阿斯顿维拉", "goals": 5, "assists": 2, "penalties": 0, "played_matches": 9, "league_code": "PL", "season": 2026},
        {"player_id": 7889, "player_name": "Bukayo Saka", "team_id": 57, "team_name": "Arsenal FC", "team_name_cn": "阿森纳", "goals": 3, "assists": 7, "penalties": 0, "played_matches": 8, "league_code": "PL", "season": 2026},
    ],
    "PD": [
        {"player_id": 371, "player_name": "Robert Lewandowski", "team_id": 81, "team_name": "FC Barcelona", "team_name_cn": "巴塞罗那", "goals": 14, "assists": 2, "penalties": 2, "played_matches": 11, "league_code": "PD", "season": 2026},
        {"player_id": 84157, "player_name": "Ayoze Pérez", "team_id": 94, "team_name": "Villarreal CF", "team_name_cn": "比利亚雷亚尔", "goals": 7, "assists": 1, "penalties": 0, "played_matches": 9, "league_code": "PD", "season": 2026},
        {"player_id": 33154, "player_name": "Kylian Mbappé", "team_id": 86, "team_name": "Real Madrid CF", "team_name_cn": "皇家马德里", "goals": 6, "assists": 1, "penalties": 3, "played_matches": 10, "league_code": "PD", "season": 2026},
        {"player_id": 758, "player_name": "Raphinha", "team_id": 81, "team_name": "FC Barcelona", "team_name_cn": "巴塞罗那", "goals": 6, "assists": 6, "penalties": 0, "played_matches": 11, "league_code": "PD", "season": 2026},
    ],
    "BL1": [
        {"player_id": 8004, "player_name": "Harry Kane", "team_id": 5, "team_name": "FC Bayern München", "team_name_cn": "拜仁慕尼黑", "goals": 9, "assists": 5, "penalties": 3, "played_matches": 8, "league_code": "BL1", "season": 2026},
        {"player_id": 32889, "player_name": "Omar Marmoush", "team_id": 19, "team_name": "Eintracht Frankfurt", "team_name_cn": "法兰克福", "goals": 9, "assists": 4, "penalties": 1, "played_matches": 8, "league_code": "BL1", "season": 2026},
    ],
    "SA": [
        {"player_id": 8325, "player_name": "Mateo Retegui", "team_id": 102, "team_name": "Atalanta BC", "team_name_cn": "亚特兰大", "goals": 10, "assists": 2, "penalties": 2, "played_matches": 9, "league_code": "SA", "season": 2026},
        {"player_id": 2060, "player_name": "Marcus Thuram", "team_id": 108, "team_name": "FC Internazionale Milano", "team_name_cn": "国际米兰", "goals": 7, "assists": 1, "penalties": 0, "played_matches": 9, "league_code": "SA", "season": 2026},
    ],
    "FL1": [
        {"player_id": 11528, "player_name": "Bradley Barcola", "team_id": 524, "team_name": "Paris Saint-Germain FC", "team_name_cn": "巴黎圣日耳曼", "goals": 8, "assists": 1, "penalties": 0, "played_matches": 9, "league_code": "FL1", "season": 2026},
        {"player_id": 9214, "player_name": "Mason Greenwood", "team_id": 516, "team_name": "Olympique de Marseille", "team_name_cn": "马赛", "goals": 6, "assists": 1, "penalties": 1, "played_matches": 9, "league_code": "FL1", "season": 2026},
    ]
}

# 比赛日程基线
BASELINE_MATCHES: List[Dict] = [
    # 英超
    {"fd_id": 500101, "league_code": "PL", "home_team_id": 57, "away_team_id": 64, "home_team_name": "Arsenal FC", "away_team_name": "Liverpool FC", "home_team_name_cn": "阿森纳", "away_team_name_cn": "利物浦", "match_date": "2026-10-25T16:30:00Z", "status": "FINISHED", "home_score": 2, "away_score": 2, "referee": "Anthony Taylor"},
    {"fd_id": 500102, "league_code": "PL", "home_team_id": 61, "away_team_id": 67, "home_team_name": "Chelsea FC", "away_team_name": "Newcastle United FC", "home_team_name_cn": "切尔西", "away_team_name_cn": "纽卡斯尔联", "match_date": "2026-10-25T14:00:00Z", "status": "FINISHED", "home_score": 2, "away_score": 1, "referee": "Simon Hooper"},
    {"fd_id": 500103, "league_code": "PL", "home_team_id": 65, "away_team_id": 394, "home_team_name": "Manchester City FC", "away_team_name": "Southampton FC", "home_team_name_cn": "曼城", "away_team_name_cn": "南安普顿", "match_date": "2026-10-24T14:00:00Z", "status": "FINISHED", "home_score": 1, "away_score": 0, "referee": "Tony Harrington"},
    {"fd_id": 500104, "league_code": "PL", "home_team_id": 58, "away_team_id": 402, "home_team_name": "Aston Villa FC", "away_team_name": "Bournemouth", "home_team_name_cn": "阿斯顿维拉", "away_team_name_cn": "伯恩茅斯", "match_date": "2026-10-24T14:00:00Z", "status": "FINISHED", "home_score": 1, "away_score": 1, "referee": "Andy Madley"},
    {"fd_id": 500105, "league_code": "PL", "home_team_id": 66, "away_team_id": 61, "home_team_name": "Manchester United FC", "away_team_name": "Chelsea FC", "home_team_name_cn": "曼联", "away_team_name_cn": "切尔西", "match_date": "2026-11-01T16:30:00Z", "status": "SCHEDULED", "home_score": None, "away_score": None, "referee": "Michael Oliver"},
    {"fd_id": 500106, "league_code": "PL", "home_team_id": 73, "away_team_id": 58, "home_team_name": "Tottenham Hotspur FC", "away_team_name": "Aston Villa FC", "home_team_name_cn": "热刺", "away_team_name_cn": "阿斯顿维拉", "match_date": "2026-11-01T14:00:00Z", "status": "SCHEDULED", "home_score": None, "away_score": None, "referee": "Craig Pawson"},
    {"fd_id": 500107, "league_code": "PL", "home_team_id": 67, "away_team_id": 57, "home_team_name": "Newcastle United FC", "away_team_name": "Arsenal FC", "home_team_name_cn": "纽卡斯尔联", "away_team_name_cn": "阿森纳", "match_date": "2026-10-31T12:30:00Z", "status": "SCHEDULED", "home_score": None, "away_score": None, "referee": "John Brooks"},
    {"fd_id": 500108, "league_code": "PL", "home_team_id": 64, "away_team_id": 397, "home_team_name": "Liverpool FC", "away_team_name": "Brighton & Hove Albion FC", "home_team_name_cn": "利物浦", "away_team_name_cn": "布莱顿", "match_date": "2026-10-31T15:00:00Z", "status": "SCHEDULED", "home_score": None, "away_score": None, "referee": "Paul Tierney"},
    # 西甲
    {"fd_id": 500201, "league_code": "PD", "home_team_id": 86, "away_team_id": 81, "home_team_name": "Real Madrid CF", "away_team_name": "FC Barcelona", "home_team_name_cn": "皇家马德里", "away_team_name_cn": "巴塞罗那", "match_date": "2026-10-25T19:00:00Z", "status": "FINISHED", "home_score": 0, "away_score": 4, "referee": "Sánchez Martínez"},
    {"fd_id": 500202, "league_code": "PD", "home_team_id": 78, "away_team_id": 77, "home_team_name": "Atlético de Madrid", "away_team_name": "Athletic Club", "home_team_name_cn": "马德里竞技", "away_team_name_cn": "毕尔巴鄂竞技", "match_date": "2026-10-25T15:15:00Z", "status": "FINISHED", "home_score": 1, "away_score": 0, "referee": "Cuadra Fernández"},
    {"fd_id": 500203, "league_code": "PD", "home_team_id": 81, "away_team_id": 92, "home_team_name": "FC Barcelona", "away_team_name": "RCD Espanyol", "home_team_name_cn": "巴塞罗那", "away_team_name_cn": "西班牙人", "match_date": "2026-11-01T15:15:00Z", "status": "SCHEDULED", "home_score": None, "away_score": None, "referee": "Gil Manzano"},
    # 德甲
    {"fd_id": 500301, "league_code": "BL1", "home_team_id": 5, "away_team_id": 3, "home_team_name": "FC Bayern München", "away_team_name": "Bayer 04 Leverkusen", "home_team_name_cn": "拜仁慕尼黑", "away_team_name_cn": "勒沃库森", "match_date": "2026-10-25T17:30:00Z", "status": "FINISHED", "home_score": 1, "away_score": 1, "referee": "Felix Zwayer"},
    {"fd_id": 500302, "league_code": "BL1", "home_team_id": 4, "away_team_id": 721, "home_team_name": "Borussia Dortmund", "away_team_name": "RB Leipzig", "home_team_name_cn": "多特蒙德", "away_team_name_cn": "莱比锡红牛", "match_date": "2026-11-01T17:30:00Z", "status": "SCHEDULED", "home_score": None, "away_score": None, "referee": "Daniel Siebert"},
    # 意甲
    {"fd_id": 500401, "league_code": "SA", "home_team_id": 108, "away_team_id": 109, "home_team_name": "FC Internazionale Milano", "away_team_name": "Juventus FC", "home_team_name_cn": "国际米兰", "away_team_name_cn": "尤文图斯", "match_date": "2026-10-25T17:00:00Z", "status": "FINISHED", "home_score": 4, "away_score": 4, "referee": "Marco Guida"},
    {"fd_id": 500402, "league_code": "SA", "home_team_id": 98, "away_team_id": 113, "home_team_name": "AC Milan", "away_team_name": "SSC Napoli", "home_team_name_cn": "AC米兰", "away_team_name_cn": "那不勒斯", "match_date": "2026-10-29T19:45:00Z", "status": "SCHEDULED", "home_score": None, "away_score": None, "referee": "Daniele Chiffi"},
    # 法甲
    {"fd_id": 500501, "league_code": "FL1", "home_team_id": 516, "away_team_id": 524, "home_team_name": "Olympique de Marseille", "away_team_name": "Paris Saint-Germain FC", "home_team_name_cn": "马赛", "away_team_name_cn": "巴黎圣日耳曼", "match_date": "2026-10-25T19:45:00Z", "status": "FINISHED", "home_score": 0, "away_score": 3, "referee": "François Letexier"},
]
