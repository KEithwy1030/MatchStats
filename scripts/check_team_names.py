
import requests
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.sporttery.cn/'
}
try:
    # 赛程 API
    r_list = requests.get('https://webapi.sporttery.cn/gateway/uniform/football/getMatchListV1.qry', headers=headers)
    data_list = r_list.json()
    m_list = data_list['value']['matchInfoList'][0]['subMatchList'][0]
    print("--- 赛程 API (Match List) ---")
    print(f"matchNumStr: {m_list.get('matchNumStr')}")
    print(f"homeTeamAbbName: {m_list.get('homeTeamAbbName')}")
    print(f"awayTeamAbbName: {m_list.get('awayTeamAbbName')}")

    # 赛果 API
    r_res = requests.get('https://webapi.sporttery.cn/gateway/uniform/football/getUniformMatchResultV1.qry?matchPage=1&pageSize=5', headers=headers)
    data_res = r_res.json()
    m_res = data_res['value']['matchResult'][0]
    print("\n--- 赛果 API (Match Result) ---")
    print(f"matchNumStr: {m_res.get('matchNumStr')}")
    print(f"homeTeam: {m_res.get('homeTeam')}")
    print(f"awayTeam: {m_res.get('awayTeam')}")
except Exception as e:
    print(f"Error: {e}")
    if 'r_list' in locals():
        print(f"Response: {r_list.text[:200]}")
