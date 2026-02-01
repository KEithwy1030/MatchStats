"""
清理本地数据库中的重复积分榜数据
保留每个联赛每个球队最新的一条 TOTAL 记录
"""
import sqlite3
import os

db_path = "data/matchstats.db"

def cleanup():
    if not os.path.exists(db_path):
        print("Database not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("开始清理重复积分榜数据...")
    
    # 1. 创建备份表
    cursor.execute("CREATE TABLE IF NOT EXISTS fd_standings_backup AS SELECT * FROM fd_standings")
    
    # 2. 删除原表记录（只保留每个球队 position 最小的那条，或者 ID 最大的那条）
    # 在这里我们采用删除重复项的策略：保留 ID 最大的那条记录
    cursor.execute("""
    DELETE FROM fd_standings 
    WHERE id NOT IN (
        SELECT MAX(id) 
        FROM fd_standings 
        GROUP BY league_code, team_id
    )
    """)
    
    rows_deleted = cursor.rowcount
    print(f"清理完成! 删除了 {rows_deleted} 条重复记录。")
    
    # 3. 检查剩余数量
    cursor.execute("SELECT count(*) FROM fd_standings")
    count = cursor.fetchone()[0]
    print(f"剩余记录数: {count} (预期应为 132)")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    cleanup()
