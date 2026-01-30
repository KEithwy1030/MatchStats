
import asyncio
from playwright.async_api import async_playwright
import time
import sys
import os

# 设置输出编码
if sys.stdout:
    sys.stdout.reconfigure(encoding='utf-8')

async def extract_grok_predictions(matches):
    """接管浏览器并批量抓取比赛预测"""
    print("🔗 正在尝试连接您手动启动的真实浏览器 (Port 9222)...")
    
    async with async_playwright() as p:
        try:
            # 连接浏览器
            browser = await p.chromium.connect_over_cdp("http://localhost:9222", timeout=30000)
            context = browser.contexts[0]
            
            # 查找或打开 Grok 页面
            page = None
            for p_obj in context.pages:
                if "grok.com" in p_obj.url:
                    page = p_obj
                    break
            
            if not page:
                print("🌐 正在打开 Grok 首页...")
                page = await context.new_page()
                await page.goto("https://grok.com/")
            else:
                print(f"✅ 已接管现有 Grok 页面: {await page.title()}")

            all_results = {}

            for match in matches:
                home, away = match
                print(f"\n🚀 正在查询: {home} vs {away}...")
                
                # 构造 Prompt
                prompt = f"请作为足球预测专家，深度分析欧冠比赛：{home} vs {away}。结合 X 上的实时伤病、首发动态，给出最终比分预测及详细原因分析。请用中文回答。"
                
                # 定位输入框
                try:
                    # 使用 contenteditable 或 textarea
                    input_selector = 'div[contenteditable="true"]'
                    await page.wait_for_selector(input_selector, timeout=10000)
                    await page.fill(input_selector, prompt)
                    await page.keyboard.press("Enter")
                    print("📤 请求已提交，等待 Grok 生成内容...")
                except Exception as e:
                    print(f"❌ 定位输入框失败: {e}")
                    continue

                # 智能轮询逻辑
                await asyncio.sleep(5)
                previous_length = 0
                stable_count = 0
                has_content_started = False
                
                # 最多轮询 10 次 (约 5 分钟)
                for poll_round in range(10):
                    current_content = await page.evaluate('''() => {
                        const bubbles = document.querySelectorAll('.message-bubble');
                        if (bubbles.length > 0) {
                            return bubbles[bubbles.length - 1].innerText;
                        }
                        return "";
                    }''')
                    
                    current_length = len(current_content)
                    print(f"⏳ 轮询中... 当前内容长度: {current_length}")

                    if current_length > 100 and not has_content_started:
                        has_content_started = True
                        print("🟢 Grok 已开始输出内容...")
                        previous_length = current_length
                        stable_count = 0
                        await asyncio.sleep(20)
                        continue

                    if current_length > previous_length:
                        previous_length = current_length
                        stable_count = 0
                    else:
                        if has_content_started:
                            stable_count += 1
                            if stable_count >= 2:
                                print("✅ 内容已稳定。")
                                break
                        else:
                            print("⏸️ 还在思考中...")
                    
                    await asyncio.sleep(20)

                # 提取最终结果
                final_text = await page.evaluate('''() => {
                    const bubbles = document.querySelectorAll('.message-bubble');
                    if (bubbles.length > 0) {
                        return bubbles[bubbles.length - 1].innerText;
                    }
                    return "未找到内容";
                }''')

                all_results[f"{home} vs {away}"] = final_text
                print(f"📄 {home} vs {away} 提取成功 (长度: {len(final_text)})")
                
                # 稍微等待，避免操作过快
                await asyncio.sleep(5)

            # 输出所有结果
            print("\n" + "="*80)
            print("🏁 所有比赛预测提取完成！")
            print("="*80)
            
            for match_name, content in all_results.items():
                print(f"\n【{match_name} 分析预览】")
                print("-" * 40)
                print(content[:300] + "...") # 仅显示预览
                print("-" * 40)

        except Exception as e:
            print(f"❌ 运行过程中发生错误: {e}")

if __name__ == "__main__":
    # 测试案例：今晚的 3 场欧冠比赛
    test_matches = [
        ("Arsenal FC", "FK Kairat"),
        ("Sport Lisboa e Benfica", "Real Madrid CF"),
        ("FC Barcelona", "FC København")
    ]
    asyncio.run(extract_grok_predictions(test_matches))
