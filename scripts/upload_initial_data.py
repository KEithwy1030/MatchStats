
import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# 设置输出编码
if sys.stdout:
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def upload_initial():
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ 环境变量未设置")
        return

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # 模拟数据（由于之前的预测文本较长，这里存入最重要的摘要部分或占位符，以便用户立即看到效果）
    # 实际上，用户下次运行 grok_batch_extract.py 就会自动存入完整版
    test_data = [
        {
            "home_team_name": "Arsenal",
            "away_team_name": "Kairat",
            "raw_prediction_text": "【系统初始测试数据】\n预测比分：3-0\n分析：阿森纳主场实力占优，Grok 实时动态显示首发阵容整齐。",
            "match_date": "2026-01-30"
        },
        {
            "home_team_name": "Real Madrid",
            "away_team_name": "Benfica",
            "raw_prediction_text": "【系统初始测试数据】\n预测比分：2-1\n分析：皇马客场作战但经验丰富，贝林厄姆状态火热。",
            "match_date": "2026-01-30"
        }
    ]
    
    try:
        supabase.table("match_predictions").insert(test_data).execute()
        print("✅ 初始测试数据已成功上传！您可以刷新 Vercel 网页查看效果。")
    except Exception as e:
        print(f"❌ 上传失败: {e}")

if __name__ == "__main__":
    upload_initial()
