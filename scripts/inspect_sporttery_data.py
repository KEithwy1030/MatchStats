
import os
import json
from supabase import create_client
from dotenv import load_dotenv
from collections import Counter

def inspect():
    load_dotenv()
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    supabase = create_client(url, key)

    # 1. 总数统计
    res = supabase.table('sporttery_matches').select('*', count='exact').execute()
    total = res.count
    matches = res.data

    print(f"==========================================")
    print(f"📊 Supabase 竞彩赛程数据概览")
    print(f"==========================================")
    print(f"总计场次: {total}")

    if not matches:
        print("数据库中暂无竞彩比赛数据。")
        return

    # 2. 按日期分布
    dates = Counter([m.get('group_date') for m in matches])
    print("\n📅 数据日期分布 (group_date):")
    for date, count in sorted(dates.items(), reverse=True)[:7]:
        print(f"  - {date}: {count} 场")

    # 3. 按状态分布
    statuses = Counter([m.get('status') for m in matches])
    print("\n⚙️ 比赛状态分布:")
    for status, count in statuses.items():
        print(f"  - {status}: {count} 场")

    # 4. 最近的 5 场比赛示例
    print("\n🔍 最近场次示例:")
    sorted_matches = sorted(matches, key=lambda x: x.get('match_time', ''), reverse=True)
    for m in sorted_matches[:5]:
        print(f"  - [{m.get('match_time')}] {m.get('league')} | {m.get('home_team')} {m.get('actual_score') or 'VS'} {m.get('away_team')} ({m.get('status')})")

    # 5. 检查与 Grok 预测的关联 (关联 match_predictions 表)
    pred_res = supabase.table('match_predictions').select('match_id').execute()
    pred_ids = {p['match_id'] for p in pred_res.data}
    
    today = "2026-02-07"
    today_matches = [m for m in matches if m.get('group_date') == today]
    today_covered = [m for m in today_matches if m['id'] in pred_ids]
    
    print(f"\n✅ 今日 ({today}) 覆盖率:")
    print(f"  - 竞彩总场次: {len(today_matches)}")
    print(f"  - Grok 已覆盖: {len(today_covered)}")
    print(f"  - 覆盖率: {len(today_covered)/len(today_matches)*100:.1f}%" if today_matches else "  - 无场次数据")

if __name__ == "__main__":
    inspect()
