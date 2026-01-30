
import asyncio
from playwright.async_api import async_playwright
import sys
import os

# 设置输出编码为 UTF-8
if sys.stdout:
    sys.stdout.reconfigure(encoding='utf-8')

async def grok_takeover_prediction(home_team, away_team):
    print("🔗 正在通过 CDP 端口 9222 接管您的真实浏览器...")
    print("💡 请确保您已使用命令行启动了 Chrome 且路径为 E:\\CursorData\\chrome_Bot")

    async with async_playwright() as p:
        browser = None
        max_retries = 3
        
        # 重试连接机制
        for attempt in range(max_retries):
            try:
                print(f"🔄 尝试连接... (第 {attempt + 1}/{max_retries} 次)")
                # 增加超时时间到 30 秒
                browser = await p.chromium.connect_over_cdp(
                    "http://localhost:9222",
                    timeout=30000  # 30秒超时
                )
                print("✅ CDP 连接成功！")
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"⚠️ 连接失败: {str(e)[:100]}，3秒后重试...")
                    await asyncio.sleep(3)
                else:
                    raise Exception(f"连接失败，已重试 {max_retries} 次。错误: {e}")
        
        if not browser:
            print("❌ 无法建立连接")
            return
        
        try:
            # 使用现有上下文
            context = browser.contexts[0]
            
            # 寻找已经加载 grok.com 的页面，没有就开一个
            page = None
            for p_obj in context.pages:
                if "grok.com" in p_obj.url:
                    page = p_obj
                    break
            
            if not page:
                page = await context.new_page()
                await page.goto("https://grok.com/", wait_until="networkidle")
            else:
                # 确保页面已完全加载
                try:
                    await page.wait_for_load_state("networkidle", timeout=10000)
                except:
                    pass

            await asyncio.sleep(2)  # 额外等待确保页面稳定
            print(f"✅ 接管成功！当前页面: {await page.title()}")

            # 具体的交互逻辑
            prompt = f"请作为足球预测专家，深度分析欧冠比赛：{home_team} vs {away_team}。结合 X 上的实时伤病、首发动态，给出最终比分预测及详细原因分析。请用中文回答。"
            
            print(f"✍️ 正在定位输入框...")
            # 尝试多种选择器策略
            input_element = None
            selectors = [
                'textarea[placeholder*="Grok"]',
                'textarea',
                'div[contenteditable="true"]',
                'input[type="text"]'
            ]
            
            for selector in selectors:
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                    input_element = selector
                    print(f"✅ 找到输入框: {selector}")
                    break
                except:
                    continue
            
            if not input_element:
                print("❌ 未找到输入框，尝试直接点击页面中心并输入...")
                await page.click('body')
                await page.keyboard.type(prompt)
                await page.keyboard.press("Enter")
            else:
                print(f"📝 正在输入提示词...")
                await page.fill(input_element, prompt)
                await page.keyboard.press("Enter")
            
            print("📤 已提交请求，等待 Grok 开始回复...")
            await asyncio.sleep(5)
            
            # 智能轮询机制：检测内容是否还在增长
            previous_length = 0
            stable_count = 0
            max_polls = 10  # 最多轮询10次（5分钟）
            has_content_started = False  # 标记：是否已经开始有实质内容
            
            for poll_round in range(max_polls):
                # 提取当前可见的 Grok 回复内容（使用更精确的 message-bubble）
                current_content = await page.evaluate('''() => {
                    const bubbles = document.querySelectorAll('.message-bubble');
                    if (bubbles.length > 0) {
                        return bubbles[bubbles.length - 1].innerText;
                    }
                    return "";
                }''')
                
                current_length = len(current_content)
                
                print(f"⏳ 第 {poll_round + 1} 轮检测 | 当前内容长度: {current_length} 字符", end="")
                
                # 判断是否已经开始有实质内容（超过100字符说明不仅仅是"思考中"）
                if current_length > 100 and not has_content_started:
                    has_content_started = True
                    print(f" | 🟢 Grok 已开始输出内容！")
                    previous_length = current_length
                    stable_count = 0
                    await asyncio.sleep(30)
                    continue
                
                # 内容是否还在增长
                if current_length > previous_length:
                    print(f" | 🟢 内容增长中... (+{current_length - previous_length})")
                    previous_length = current_length
                    stable_count = 0  # 重置稳定计数器
                else:
                    # 只有在"已经开始有内容"之后，才认为"未变化"是真正的稳定
                    if has_content_started:
                        stable_count += 1
                        print(f" | 🟡 内容未变化 ({stable_count}/2)")
                        
                        # 连续两轮都没变化，说明已经稳定
                        if stable_count >= 2:
                            print("✅ 内容已稳定，Grok 回复完成！")
                            break
                    else:
                        print(f" | ⏸️ Grok 还在思考中...")
                
                # 等待30秒再下一轮检测
                await asyncio.sleep(30)
            
            # 滚动到页面底部，确保所有内容都加载
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)
            
            # 最终提取
            print("🔍 提取最终分析结果...")
            result_text = await page.evaluate('''() => {
                // 方式1: 使用 message-bubble class（最精确）
                const bubbles = document.querySelectorAll('.message-bubble');
                if (bubbles.length > 0) {
                    // 最后一个 bubble 通常是 Grok 的回复
                    const lastBubble = bubbles[bubbles.length - 1];
                    return lastBubble.innerText;
                }
                
                // 方式2: 查找包含"思考了"的容器（Grok特征）
                const allDivs = document.querySelectorAll('div');
                for (let i = allDivs.length - 1; i >= 0; i--) {
                    const text = allDivs[i].innerText;
                    if (text && text.includes('思考了') && text.length > 500) {
                        return text;
                    }
                }
                
                // 方式3: 查找 messageEntry 但需要是最后一个且内容足够长
                const messageEntries = document.querySelectorAll('[data-testid="messageEntry"]');
                if (messageEntries.length > 1) {
                    const lastMessage = messageEntries[messageEntries.length - 1];
                    const text = lastMessage.innerText;
                    if (text.length > 500) {
                        return text;
                    }
                }
                
                // 兜底：返回页面主要内容（但可能包含UI元素）
                return document.body.innerText;
            }''')

            # 保存结果到当前项目目录
            filename = f"prediction_grok_{home_team}_vs_{away_team}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(result_text)
            
            print(f"🎉 大功告成！预测文章已保存至: {filename}")
            print(f"📊 最终内容长度: {len(result_text)} 字符")
            
            # 重要：不要执行 browser.close()，否则会关掉您的手动浏览器
            # 仅断开 CDP 连接即可
            
        except Exception as e:
            print(f"🔥 接管失败: {e}")
            print("💡 检查点：")
            print("1. 浏览器是否已彻底关闭后用了正确的 CMD 命令重启？")
            print("2. 访问 http://localhost:9222/json/version 是否有 JSON 响应？")

if __name__ == "__main__":
    # 测试一下阿森纳对阵卡拉特
    asyncio.run(grok_takeover_prediction("阿森纳", "卡拉特"))
