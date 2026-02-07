
import sys
import os
import json
import asyncio
import requests
import re
import subprocess
import random
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright
from dotenv import load_dotenv
from supabase import create_client

# ----------------- 静态路径配置 (Windows) -----------------
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
USER_DATA_DIR = r"E:\CursorData\MCP\playwright-mcp\browser_data\grok-profile-real-chrome"
PROFILE_NAME = "Default"
CDP_PORT = 9333
CDP_URL = f"http://localhost:{CDP_PORT}"
GROK_URL = "https://grok.com"
BATCH_SIZE = 2  # 高保真专家模式：每轮只处理2场，且强制开启新会话

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

    # --- 2. 浏览器连接 ---
    async def ensure_active_page(self):
        try:
            requests.get(f"{CDP_URL}/json/version", timeout=1)
            print("[Check] 发现运行中的 Chrome (Port 9333)")
            return True
        except:
            print("[Check] 未发现活动浏览器，请先手动启动 Chrome 调试实例。")
            return False

    # --- 3. 辅助：提取复杂的 JSON ---
    def extract_json_from_text(self, text):
        try:
            return json.loads(text)
        except: pass
        match = re.search(r'```(?:json)?\s*(\[.*\])\s*```', text, re.DOTALL)
        if match:
            try: return json.loads(match.group(1))
            except: pass
        try:
            start = text.find('[')
            end = text.rfind(']')
            if start != -1 and end != -1:
                return json.loads(text[start:end+1])
        except: pass
        return None

    # --- 4. 核心流入口 ---
    async def main_engine(self):
        matches, date = self.get_matches()
        if not matches:
            print(f"[!] {date} 暂无比赛计划，脚本退出。")
            return

        try:
            existing_res = self.supabase.table('match_predictions').select('match_id').eq('prediction_date', date).execute()
            existing_ids = {item['match_id'] for item in existing_res.data}
            pending_matches = [m for m in matches if m['id'] not in existing_ids]

            if not pending_matches:
                print(f"============================================================")
                print(f"[OK] 审计完成：今日 {len(matches)} 场已全部完成情报采集！")
                print(f"============================================================")
                return
            
            print(f"[Audit] 待处理: {len(pending_matches)} / 总场次: {len(matches)}")
            matches = pending_matches
        except Exception as e:
            print(f"[x] 审计阶段出错: {e}")

        if not await self.ensure_active_page(): return

        async with async_playwright() as p:
            try:
                browser = await p.chromium.connect_over_cdp(CDP_URL)
                context = browser.contexts[0]
                page = context.pages[0] if context.pages else await context.new_page()
                
                total_batches = (len(matches) + BATCH_SIZE - 1) // BATCH_SIZE
                print(f"[Run] 进入专家情报模式：每批 2 场，共 {total_batches} 批。")

                for i in range(total_batches):
                    # --- 每一批次强制刷新以保证搜索深度和独立性 ---
                    print(f"\n[Reset] 正在为批次 {i+1} 重置对话环境...")
                    await page.goto(GROK_URL)
                    # 增加等待时间，确保 SPA 加载完成
                    await asyncio.sleep(12) 

                    batch = matches[i*BATCH_SIZE : (i+1)*BATCH_SIZE]
                    print(f"[Processing] 批次 {i+1}/{total_batches}: {[m['home_team'] for m in batch]}")
                    print(f"    [URL] {page.url}")

                    # --- 顶级精算师 Prompt ---
                    prompt = f"""# Role
你是一位拥有 15 年经验的顶级足球博弈精算师与分析专家。
你必须通过深度联网搜索 (Deep Web Search) 为以下比赛提取最硬核的情报素材。

# Objective
提取最实时的原始事实。**严禁任何形式的预测结论，严禁空洞的通用描述。**

# Search & Evidence Requirements (质量红线)
1. 【数据真相】：必须检索并对比两队的 xG (期望进球)、近期控球效率或关键球员表现数据。如果找不到 xG，请引用具体的进失球时效性统计。
2. 【情报支撑】：必须引用来自 X (Twitter) 上的认证博主、随队记者或当地专业媒体的最新动态（如训练课观察、赛前临时变阵、更衣室氛围）。
3. 【盘路异动】：对比主流机构 (Bet365, Pinnacle 等) 的初盘与即时盘，识别是否存在异常的水位跳变或资金流偏好。
4. 【环境变量】：除了天气，要深挖裁判的判罚尺度偏好、甚至客队的旅行后勤保障（是否有延误、体能隐患）。

# Output Format
仅返回标准的 JSON 数组，严禁任何前导或后随文本。
**情报内容 (match_intelligence) 必须使用中文撰写（即使信息源是外文，也请将其核心精髓翻译/整理为中文）：**
[
 {{"match_id": ID, "match_intelligence": "【两队近况】...\\n【数据真相】...\\n【战术碰撞】...\\n【赔率波动】...\\n【心态变量】...\\n【核心战意】...\\n【场外及X因素】..."}}
]

# Target Matches
"""
                    for m in batch: prompt += f"- [ID:{m['id']}] {m['match_time']} {m['home_team']} VS {m['away_team']}\n"

                    # 自动处理 A/B 弹窗
                    try:
                        ab_btn = page.locator("button:has-text('Model A'), button:has-text('Model B')").first
                        if await ab_btn.is_visible(): await ab_btn.click(); await asyncio.sleep(2)
                    except: pass

                    # --- 智能寻找输入框 ---
                    target_input = None
                    selectors = ['textarea:visible', 'div[contenteditable="true"]:visible', '[role="textbox"]:visible']
                    for sel in selectors:
                        try:
                            loc = page.locator(sel).first
                            if await loc.is_visible(timeout=5000):
                                target_input = loc
                                print(f"    [Input Found] Using selector: {sel}")
                                break
                        except: continue
                    
                    if not target_input:
                        print("    [!] 无法定位可见的输入框，尝试强制点击页面中心...")
                        await page.mouse.click(400, 300) # 尝试点击中间
                        target_input = page.locator("textarea, div[contenteditable='true']").first

                    # 发送指令
                    await target_input.click()
                    await asyncio.sleep(1)
                    # 清空并输入
                    await page.evaluate("(t) => { navigator.clipboard.writeText(t); }", prompt)
                    await page.keyboard.press("Control+A")
                    await page.keyboard.press("Backspace")
                    await page.keyboard.press("Control+V")
                    await asyncio.sleep(2)
                    await page.keyboard.press("Enter")
                    
                    print(f"    [Wait] 深度挖掘中", end="", flush=True)
                    reply_text = ""
                    start_wait = datetime.now()
                    while (datetime.now() - start_wait).seconds < 1200: 
                        await asyncio.sleep(10)
                        
                        # 广义提取最新回复 (优先寻找包含 json 特征的 div)
                        current_text = await page.evaluate("""() => {
                            const candidates = Array.from(document.querySelectorAll('.prose, .message-bubble, div[class*="message"], article'));
                            if (candidates.length === 0) return "";
                            // 优先找最后几个包含 match_id 的
                            for (let i = candidates.length - 1; i >= 0; i--) {
                                if (candidates[i].innerText.includes('match_id')) return candidates[i].innerText;
                            }
                            return candidates[candidates.length - 1].innerText;
                        }""")
                        
                        print(f"[{len(current_text)}]", end="", flush=True)
                        
                        # 判定结束：有实质内容且 20 秒内无变化
                        if len(current_text) > 800 and current_text == reply_text:
                            # 验证是否有 sources 标志
                            has_src = await page.evaluate("() => document.body.innerText.includes('sources')")
                            print(f" [Done & Verified]" if has_src else " [Done (Standard)]")
                            break
                        reply_text = current_text
                    
                    # 入库
                    parsed = self.extract_json_from_text(reply_text)
                    if parsed:
                        self.sync_to_db(parsed, date)
                    else:
                        print(f"\n    [x] 解析失败。原始文本片段: {reply_text[:200]}...")

                    # 拟人化延迟：每批次跑完，休息 15~30 秒
                    rest_time = random.uniform(15, 30)
                    print(f"    [Rest] 拟人化休息 {rest_time:.1f}s 以规避风控...")
                    await asyncio.sleep(rest_time)

                print(f"\n[4/4] 专家级情报任务全部圆满完成！")
            except Exception as e: print(f"[x] Critical Failure: {e}")

if __name__ == "__main__":
    asyncio.run(GrokTheUltimate().main_engine())
