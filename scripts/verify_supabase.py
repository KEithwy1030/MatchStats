
import os
import requests
import sys
from dotenv import load_dotenv

# 设置输出编码
if sys.stdout:
    sys.stdout.reconfigure(encoding='utf-8')

# 加载环境变量
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def check_connection():
    print(f"Checking connection: {SUPABASE_URL}")
    
    # 尝试访问 Supabase 的基础 API 路径
    url = f"{SUPABASE_URL}/rest/v1/"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print("✅ 连接成功！钥匙和地址都是正确的。")
            return True
        else:
            print(f"❌ 连接失败 (状态码: {response.status_code})")
            print(f"提示: {response.text}")
            return False
    except Exception as e:
        print(f"🔥 发生异常: {e}")
        return False

if __name__ == "__main__":
    check_connection()
