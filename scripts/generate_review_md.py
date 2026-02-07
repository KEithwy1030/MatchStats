
import os
import json
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

# Fetch data
try:
    response = supabase.table("match_predictions").select("*").eq("prediction_date", "2026-02-07").execute()
    matches = response.data
    
    # Sort matches by time if available, else by ID
    matches.sort(key=lambda x: x.get('match_time', ''))

    md_content = f"# 2026-02-07 比赛情报审查报告\n\nGenerated at: {os.environ.get('TIME', 'Now')}\n\n"
    
    for match in matches:
        home = match.get('home_team', 'Unknown')
        away = match.get('away_team', 'Unknown')
        league = match.get('league', 'Unknown')
        time = match.get('match_time', 'Unknown')
        intelligence = match.get('prediction_data', 'No data')
        
        md_content += f"## {league} | {home} vs {away}\n"
        md_content += f"**比赛时间**: {time}\n\n"
        md_content += f"### 情报内容\n"
        
        # Intelligence is stored as a string, likely containing newlines. 
        # Make sure it renders well in markdown.
        # If it's a JSON string, try to parse it (though usually it's just text based on previous steps)
        # Based on previous context, 'prediction_data' is the raw text from Grok.
        
        md_content += f"{intelligence}\n\n"
        md_content += "---\n\n"

    filename = "e:\\CursorData\\MatchStats\\match_intelligence_review_2026-02-07.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(md_content)
        
    print(f"Successfully generated markdown report at: {filename}")
    print(f"Total matches: {len(matches)}")

except Exception as e:
    print(f"Error: {e}")
