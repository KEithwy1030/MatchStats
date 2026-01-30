import sqlite3
from pprint import pprint

db_path = r"e:\CursorData\MatchStats\data\matchstats.db"

def list_info():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 列出所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    print("Tables in database:", tables)
    
    # 查找 2026-01-28/29 的所有比赛
    if 'fd_matches' in tables:
        cursor.execute("SELECT match_date, home_team_name, away_team_name, league_code FROM fd_matches WHERE match_date LIKE '2026-01-28%' OR match_date LIKE '2026-01-29%';")
        matches = cursor.fetchall()
        print("\nAll Matches on Jan 28-29:")
        pprint(matches)
    
    conn.close()

if __name__ == "__main__":
    list_info()
