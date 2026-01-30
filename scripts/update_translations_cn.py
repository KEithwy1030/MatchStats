import sys
import os
import sqlite3

# Ensure app can be imported
sys.path.append(os.getcwd())
from app.config import settings

# Translation Dictionary (Copied from ogK88)
TEAM_NAME_DICT = {
    # === 英超 (Premier League) ===
    "Arsenal FC": "阿森纳", "Arsenal": "阿森纳",
    "Aston Villa FC": "阿斯顿维拉", "Aston Villa": "阿斯顿维拉",
    "AFC Bournemouth": "伯恩茅斯", "Bournemouth": "伯恩茅斯",
    "Brentford FC": "布伦特福德", "Brentford": "布伦特福德",
    "Brighton & Hove Albion FC": "布莱顿", "Brighton Hove": "布莱顿",
    "Chelsea FC": "切尔西", "Chelsea": "切尔西",
    "Crystal Palace FC": "水晶宫", "Crystal Palace": "水晶宫",
    "Everton FC": "埃弗顿", "Everton": "埃弗顿",
    "Fulham FC": "富勒姆", "Fulham": "富勒姆",
    "Ipswich Town FC": "伊普斯维奇", "Ipswich Town": "伊普斯维奇",
    "Leicester City FC": "莱斯特城", "Leicester City": "莱斯特城",
    "Liverpool FC": "利物浦", "Liverpool": "利物浦",
    "Manchester City FC": "曼城", "Man City": "曼城",
    "Manchester United FC": "曼联", "Man United": "曼联",
    "Newcastle United FC": "纽卡斯尔联", "Newcastle": "纽卡斯尔联",
    "Nottingham Forest FC": "诺丁汉森林", "Nottingham": "诺丁汉森林",
    "Southampton FC": "南安普顿", "Southampton": "南安普顿",
    "Tottenham Hotspur FC": "热刺", "Tottenham": "热刺",
    "West Ham United FC": "西汉姆联", "West Ham": "西汉姆联",
    "Wolverhampton Wanderers FC": "狼队", "Wolves": "狼队",

    # === 西甲 (La Liga) ===
    "Real Madrid CF": "皇家马德里", "Real Madrid": "皇家马德里",
    "FC Barcelona": "巴塞罗那", "Barcelona": "巴塞罗那",
    "Girona FC": "赫罗纳", "Girona": "赫罗纳",
    "Atlético de Madrid": "马德里竞技", "Atleti": "马德里竞技",
    "Athletic Club": "毕尔巴鄂竞技", "Athletic": "毕尔巴鄂竞技",
    "Real Sociedad de Fútbol": "皇家社会", "Real Sociedad": "皇家社会",
    "Real Betis Balompié": "皇家贝蒂斯", "Real Betis": "皇家贝蒂斯",
    "Villarreal CF": "比利亚雷亚尔", "Villarreal": "比利亚雷亚尔",
    "Valencia CF": "瓦伦西亚", "Valencia": "瓦伦西亚",
    "Deportivo Alavés": "阿拉维斯", "Alavés": "阿拉维斯",
    "CA Osasuna": "奥萨苏纳", "Osasuna": "奥萨苏纳",
    "Getafe CF": "赫塔菲", "Getafe": "赫塔菲",
    "RC Celta de Vigo": "塞尔塔", "Celta": "塞尔塔",
    "Sevilla FC": "塞维利亚", "Sevilla": "塞维利亚",
    "RCD Mallorca": "马洛卡", "Mallorca": "马洛卡",
    "UD Las Palmas": "拉斯帕尔马斯", "Las Palmas": "拉斯帕尔马斯",
    "Rayo Vallecano de Madrid": "巴列卡诺", "Rayo Vallecano": "巴列卡诺",
    "Real Valladolid CF": "瓦拉多利德", "Valladolid": "瓦拉多利德",
    "CD Leganés": "莱加内斯", "Leganés": "莱加内斯",
    "RCD Espanyol de Barcelona": "西班牙人", "Espanyol": "西班牙人",

    # === 德甲 (Bundesliga) ===
    "Bayer 04 Leverkusen": "勒沃库森", "Leverkusen": "勒沃库森",
    "FC Bayern München": "拜仁慕尼黑", "Bayern": "拜仁慕尼黑",
    "VfB Stuttgart": "斯图加特", "Stuttgart": "斯图加特",
    "RB Leipzig": "莱比锡红牛", "Leipzig": "莱比锡红牛",
    "Borussia Dortmund": "多特蒙德", "Dortmund": "多特蒙德",
    "Eintracht Frankfurt": "法兰克福", "Frankfurt": "法兰克福",
    "TSG 1899 Hoffenheim": "霍芬海姆", "Hoffenheim": "霍芬海姆",
    "1. FC Heidenheim 1846": "海登海姆", "Heidenheim": "海登海姆",
    "SV Werder Bremen": "不莱梅", "Bremen": "不莱梅",
    "SC Freiburg": "弗赖堡", "Freiburg": "弗赖堡",
    "FC Augsburg": "奥格斯堡", "Augsburg": "奥格斯堡",
    "VfL Wolfsburg": "沃尔夫斯堡", "Wolfsburg": "沃尔夫斯堡",
    "1. FSV Mainz 05": "美因茨", "Mainz": "美因茨",
    "Borussia Mönchengladbach": "门兴", "Gladbach": "门兴",
    "1. FC Union Berlin": "柏林联合", "Union Berlin": "柏林联合",
    "VfL Bochum 1848": "波鸿", "Bochum": "波鸿",
    "FC St. Pauli 1910": "圣保利", "St. Pauli": "圣保利",
    "Holstein Kiel": "基尔",

    # === 意甲 (Serie A) ===
    "FC Internazionale Milano": "国际米兰", "Inter": "国际米兰",
    "AC Milan": "AC米兰", "Milan": "AC米兰",
    "Juventus FC": "尤文图斯", "Juventus": "尤文图斯",
    "Bologna FC 1909": "博洛尼亚", "Bologna": "博洛尼亚",
    "AS Roma": "罗马", "Roma": "罗马",
    "Atalanta BC": "亚特兰大", "Atalanta": "亚特兰大",
    "SS Lazio": "拉齐奥", "Lazio": "拉齐奥",
    "ACF Fiorentina": "佛罗伦萨", "Fiorentina": "佛罗伦萨",
    "Torino FC": "都灵", "Torino": "都灵",
    "SSC Napoli": "那不勒斯", "Napoli": "那不勒斯",
    "Genoa CFC": "热那亚", "Genoa": "热那亚",
    "AC Monza": "蒙扎", "Monza": "蒙扎",
    "Hellas Verona FC": "维罗纳", "Verona": "维罗纳",
    "US Lecce": "莱切", "Lecce": "莱切",
    "Udinese Calcio": "乌迪内斯", "Udinese": "乌迪内斯",
    "Cagliari Calcio": "卡利亚里", "Cagliari": "卡利亚里",
    "Empoli FC": "恩波利", "Empoli": "恩波利",
    "Parma Calcio 1913": "帕尔马", "Parma": "帕尔马",
    "Como 1907": "科莫", "Como": "科莫",
    "Venezia FC": "威尼斯", "Venezia": "威尼斯",

    # === 法甲 (Ligue 1) ===
    "Paris Saint-Germain FC": "巴黎圣日耳曼", "PSG": "巴黎圣日耳曼",
    "AS Monaco FC": "摩纳哥", "Monaco": "摩纳哥",
    "Stade Brestois 29": "布雷斯特", "Brest": "布雷斯特",
    "LOSC Lille": "里尔", "Lille": "里尔",
    "OGC Nice": "尼斯", "Nice": "尼斯",
    "Olympique Lyonnais": "里昂", "Lyon": "里昂",
    "RC Lens": "朗斯", "Lens": "朗斯",
    "Olympique de Marseille": "马赛", "Marseille": "马赛",
    "Stade de Reims": "兰斯", "Reims": "兰斯",
    "Stade Rennais FC 1901": "雷恩", "Rennes": "雷恩",
    "Toulouse FC": "图卢兹", "Toulouse": "图卢兹",
    "Montpellier HSC": "蒙彼利埃", "Montpellier": "蒙彼利埃",
    "RC Strasbourg Alsace": "斯特拉斯堡", "Strasbourg": "斯特拉斯堡",
    "FC Nantes": "南特", "Nantes": "南特",
    "Le Havre AC": "勒阿弗尔", "Le Havre": "勒阿弗尔",
    "AJ Auxerre": "欧塞尔", "Auxerre": "欧塞尔",
    "Angers SCO": "昂热", "Angers": "昂热",
    "AS Saint-Étienne": "圣埃蒂安", "Saint-Étienne": "圣埃蒂安",
    
     # === 英冠 (Championship) ===
    "Sunderland AFC": "桑德兰", "Sunderland": "桑德兰",
    "Leeds United FC": "利兹联", "Leeds United": "利兹联",
    "Burnley FC": "伯恩利", "Burnley": "伯恩利",
    "Sheffield United FC": "谢菲尔德联",
    "West Bromwich Albion FC": "西布朗",
    "Watford FC": "沃特福德",
    "Norwich City FC": "诺维奇",
    "Luton Town FC": "卢顿",
    "Middlesbrough FC": "米德尔斯堡",
    "Portsmouth FC": "朴茨茅斯",
    "Derby County FC": "德比郡",
    "Oxford United FC": "牛津联",
    "Hull City AFC": "赫尔城",
    "Coventry City FC": "考文垂",
    "Blackburn Rovers FC": "布莱克本",
    "Bristol City FC": "布里斯托尔城",
    "Swansea City AFC": "斯旺西",
    "Cardiff City FC": "加的夫城",
    "Millwall FC": "米尔沃尔",
    "Preston North End FC": "普雷斯顿",
    "Queens Park Rangers FC": "女王公园巡游者",
    "Plymouth Argyle FC": "普利茅斯",
    "Sheffield Wednesday FC": "谢周三",
    "Stoke City FC": "斯托克城"
};

def run():
    print(f"Connecting to {settings.DB_PATH}")
    conn = sqlite3.connect(settings.DB_PATH)
    cursor = conn.cursor()
    
    # 1. Add column if not exists
    try:
        cursor.execute("SELECT name_cn FROM fd_teams LIMIT 1")
    except sqlite3.OperationalError:
        print("Adding name_cn column to fd_teams...")
        cursor.execute("ALTER TABLE fd_teams ADD COLUMN name_cn TEXT")
        conn.commit()

    # 2. Update data
    print("Updating translations...")
    updated_count = 0
    for eng_name, cn_name in TEAM_NAME_DICT.items():
        cursor.execute("""
            UPDATE fd_teams 
            SET name_cn = ? 
            WHERE name = ? OR short_name = ?
        """, (cn_name, eng_name, eng_name))
        updated_count += cursor.rowcount
    
    conn.commit()
    print(f"Updated {updated_count} records.")
    
    # Verify
    cursor.execute("SELECT name, name_cn FROM fd_teams WHERE name_cn IS NOT NULL LIMIT 5")
    for row in cursor.fetchall():
        print(f"Sample: {row[0]} -> {row[1]}")
        
    conn.close()

if __name__ == "__main__":
    run()
