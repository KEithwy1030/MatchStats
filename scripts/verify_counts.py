import sqlite3
import os

db_path = "data/matchstats.db"

def check_data():
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    leagues = ['PL', 'PD', 'BL1', 'SA', 'FL1', 'CL']

    print(f"{'League':<6} | {'Standings (DB View)':<20} | {'Scorers (DB View)':<20}")
    print("-" * 55)

    for code in leagues:
        # Check Standings (Unique Teams)
        query_st = """
            SELECT count(*) 
            FROM fd_standings s
            WHERE s.league_code = ?
            AND s.id IN (
                SELECT MAX(id) 
                FROM fd_standings 
                WHERE league_code = ? 
                GROUP BY team_id
            )
        """
        cursor.execute(query_st, (code, code))
        st_count = cursor.fetchone()[0]

        # Check Scorers (Unique Players)
        query_sc = """
            SELECT count(*) 
            FROM fd_scorers s
            WHERE s.league_code = ?
            AND s.id IN (
                SELECT MAX(id) 
                FROM fd_scorers 
                WHERE league_code = ? 
                GROUP BY player_id
            )
        """
        cursor.execute(query_sc, (code, code))
        sc_count = cursor.fetchone()[0]

        print(f"{code:<6} | {st_count:<20} | {sc_count:<20}")

    conn.close()

if __name__ == "__main__":
    check_data()
