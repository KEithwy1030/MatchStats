
import sys
import os
import json
import asyncio
import requests
import re
import subprocess
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright
from dotenv import load_dotenv
from supabase import create_client

# ----------------- 静态路径配置 (Windows) -----------------
# 确保即使没其他文件，只要这几个路径对，脚本就能自给自足
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
USER_DATA_DIR = r"E:\CursorData\MCP\playwright-mcp\browser_data\grok-profile-real-chrome"
PROFILE_NAME = "Default"
CDP_PORT = 9333
CDP_URL = f"http://localhost:{CDP_PORT}"
GROK_URL = "https://grok.com"
BATCH_SIZE = 3 

# ----------------- 加载环境变量 -----------------
load_dotenv()
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

class GrokTheUltimate:
    def __init__(self):
        self.supabase = None
        if SUPABASE_URL and SUPABASE_KEY:
            self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    # --- 1. 数据库交互 ---
    def get_matches(self):
        try:
            target_date = datetime.now().strftime('%Y-%m-%d')
            if len(sys.argv) > 1 and sys.argv[1].startswith('202'):
                target_date = sys.argv[1]
            print(f"\n[1/4] 目标日期: {target_date}")
            res = self.supabase.table('sporttery_matches').select('id, league, home_team, away_team, match_time').eq('group_date', target_date).order('match_time').execute()
            return res.data, target_date
        except Exception as e:
            print(f"[x] DB Error: {e}"); return [], None

    def sync_to_db(self, data, date):
        if not self.supabase: return
        for item in data:
            try:
                m_id = item.get("match_id")
                content = item.get("match_intelligence") or item.get("prediction_data")
                if not m_id or not content: continue
                m_info = self.supabase.table("sporttery_matches").select("*").eq("id", m_id).single().execute().data
                if not m_info: continue
                entry = {
                    "match_id": int(m_id),
                    "league": m_info["league"],
                    "home_team": m_info["home_team"],
                    "away_team": m_info["away_team"],
                    "match_time": m_info["match_time"],
                    "prediction_data": content,
                    "prediction_date": date
                }
                self.supabase.table("match_predictions").upsert(entry, on_conflict="match_id").execute()
                print(f"    [DB] {m_info['home_team']} 成功入库")
            except Exception as e: print(f"    [x] DB Sync Error: {e}")

    # --- 2. 浏览器热/冷启动逻辑 (合并自 launch_grok_native) ---
    async def ensure_active_page(self):
        try:
            requests.get(f"{CDP_URL}/json/version", timeout=1)
            print("[Check] 发现运行中的 Chrome (Port 9333)")
            return True
        except:
            print("[Check] 未发现活动浏览器，尝试冷启动...")
            if not os.path.exists(CHROME_PATH):
                print(f"[x] 找不到 Chrome 可执行文件: {CHROME_PATH}"); return False
            cmd = [CHROME_PATH, f"--remote-debugging-port={CDP_PORT}", f"--user-data-dir={USER_DATA_DIR}", f"--profile-directory={PROFILE_NAME}", GROK_URL]
            subprocess.Popen(cmd, shell=False)
            await asyncio.sleep(8)
            return True

    async def wait_for_reply(self, page, timeout=900):
        print(f"    [Wait] 深度挖掘中", end="", flush=True)
        last_text = ""
        start_time = asyncio.get_event_loop().time()
        await asyncio.sleep(10)
        while (asyncio.get_event_loop().time() - start_time) < timeout:
            await page.evaluate("""() => {
                const b = Array.from(document.querySelectorAll('button')).find(x => x.innerText.includes('跳过选择') || x.innerText.includes('Skip selection'));
                if (b) b.click();
            }""")
            await asyncio.sleep(10); print(".", end="", flush=True)
            text = await page.evaluate("""() => {
                const sel = ['.prose', 'article', '.message-row'];
                for (let s of sel) {
                    let els = Array.from(document.querySelectorAll(s));
                    if (els.length > 0) {
                        let t = els[els.length-1].innerText;
                        if (t && t.trim().length > 300) return t;
                    }
                }
                return document.body.innerText;
            }""")
            if text and text == last_text and len(text) > 300:
                print(" [Done]"); return text
            last_text = text
        return None

    # --- 3. 核心流入口 ---
    async def main_engine(self):
        # A. 首先查询当日所有的比赛
        matches, date = self.get_matches()
        if not matches:
            print(f"[!] {date} 暂无比赛计划，脚本退出。")
            return

        # B. 智能审计：查漏补缺
        try:
            # 查询预测表中已经存在的所有 ID
            existing_res = self.supabase.table('match_predictions').select('match_id').eq('prediction_date', date).execute()
            existing_ids = {item['match_id'] for item in existing_res.data}
            
            # 过滤出还没抓取的比赛
            pending_matches = [m for m in matches if m['id'] not in existing_ids]

            if not pending_matches:
                print(f"============================================================")
                print(f"[OK] 审计完成：{date} 的共 {len(matches)} 场比赛情报已全部入库！")
                print(f"[Skip] 脚本将静默退出，不打扰您的正常工作。")
                print(f"============================================================")
                return
            
            print(f"[Audit] 发现更新：今日总场次 {len(matches)}，已入库 {len(existing_ids)}，待处理 {len(pending_matches)}")
            matches = pending_matches # 仅处理剩下的比赛
            
        except Exception as e:
            print(f"[x] 审计阶段出错 (将尝试全量处理): {e}")

        # C. 确定有活要干，再启动浏览器
        if not await self.ensure_active_page(): return

        async with async_playwright() as p:
            try:
                browser = await p.chromium.connect_over_cdp(CDP_URL)
                context = browser.contexts[0]
                page = context.pages[0] if context.pages else await context.new_page()
                if "grok.com" not in page.url: await page.goto(GROK_URL); await asyncio.sleep(3)
            except Exception as e: print(f"[x] CDP 连接失败: {e}"); return

            total = (len(matches) + BATCH_SIZE - 1) // BATCH_SIZE
            print(f"[Run] 进入主引擎：共 {len(matches)} 场，分 {total} 批。")

            for i in range(total):
                batch = matches[i*BATCH_SIZE : (i+1)*BATCH_SIZE]
                print(f"\n[2/4] 正在处理批次 {i+1}/{total}...")
                
                # 终极版提示词逻辑
                prompt = f"""# Role
你是一位拥有 15 年经验的顶级足球博弈精算师与情报专家。

# Objective
请利用 DeepSearch 提取下述比赛的【原始事实素材库】。
**严禁预测结论，严禁包含评价性词汇。必须使用【中文】。**

# Search Dimensions
1. 【战损与替代】：保底有名单，进阶有替补表现。
2. 【数据真相】：保底有比分，进阶有 xG 期望值。
3. 【战术碰撞】：防守/进攻风格是否克制。
4. 【博弈温标】：赔率盘位异常波动捕获。
5. 【动态变量】：天气、旅行损耗、发布会潜台词。
6. 【核心战意】：积分权重、战意量化。
7. 【场外及X因素】：裁判偏好、草皮、转会流言、欠薪等。

# Target Matches
"""
                for m in batch: prompt += f"- [ID:{m['id']}] {m['match_time']} {m['home_team']} VS {m['away_team']}\n"
                prompt += "\n# Output Format\n仅返回 JSON 数组，严禁前导文本：\n[{'match_id': ID, 'match_intelligence': '板块1...\\n板块2...'}]"

                # 输入与执行
                sel = 'textarea[placeholder*="message" i], [contenteditable="true"]'
                await page.wait_for_selector(sel); await page.click(sel)
                await page.evaluate("(t) => { document.execCommand('insertText', false, t); }", prompt)
                await page.keyboard.press("Enter")
                
                reply = await self.wait_for_reply(page)
                if reply:
                    try:
                        m = re.search(r'\[\s*\{.*\}\s*\]', reply, re.DOTALL)
                        s = m.group(0) if m else reply
                        s = re.sub(r'```json\s*|\s*```', '', s)
                        parsed = json.loads(s.strip())
                        if isinstance(parsed, list):
                            print(f"    [3/4] 提取成功，实时入库中...")
                            self.sync_to_db(parsed, date)
                    except Exception as e: print(f"    [x] 解析异常: {e}")

            print(f"\n[4/4] 任务圆满完成！(2026-02-04 终极封装版)")

if __name__ == "__main__":
    asyncio.run(GrokTheUltimate().main_engine())
