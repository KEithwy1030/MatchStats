
import os
from supabase import create_client
from dotenv import load_dotenv

def test_connection():
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    print(f"🔗 正在尝试连接 Supabase...")
    try:
        supabase = create_client(url, key)
        # 尝试读取一场比赛
        res = supabase.table("fd_matches").select("id").limit(1).execute()
        print(f"✅ 权限验证成功！已成功读取到云端数据。")
        print(f"📊 云端数据探测：当前已有数据条目。")
        return True
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False

if __name__ == "__main__":
    test_connection()
