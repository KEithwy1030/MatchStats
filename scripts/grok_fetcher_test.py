
import asyncio
from playwright.async_api import async_playwright
import time
import os
import sys

# 设置输出编码为 UTF-8 防止乱码
if sys.stdout:
    sys.stdout.reconfigure(encoding='utf-8')

async def run_grok_test(prompt):
    # 核心配置：您的 Chrome 个人资料路径
    user_data_dir = r"C:\Users\wuyon\AppData\Local\Google\Chrome\User Data"
    profile_name = "Profile 2"
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    
    print(f"🚀 正在启动浏览器并加载配置: {profile_name}...")
    print(f"📂 配置文件路径: {user_data_dir}")

    async with async_playwright() as p:
        try:
            # 使用 launch_persistent_context 接管已有配置
            # 显式指定 executable_path 指向您的主流 Chrome
            context = await p.chromium.launch_persistent_context(
                user_data_dir,
                executable_path=chrome_path,
                headless=False,
                args=[f"--profile-directory={profile_name}", "--no-sandbox", "--disable-setuid-sandbox"],
                # 保持窗口大小一致，避免布局错乱
                viewport={"width": 1280, "height": 800}
            )

            page = await context.new_page()
            
            # 1. 访问 Grok
            print("🌐 正在访问 Grok (X.com)...")
            await page.goto("https://x.com/i/grok", wait_until="networkidle")

            # 2. 等待并输入提示词
            print(f"✍️ 正在寻找输入框...")
            # Grok 的输入通常使用 textarea 或者是 data-testid="grok_input_box"
            input_selector = 'textarea[data-testid="grok_input_box"], textarea'
            
            try:
                await page.wait_for_selector(input_selector, timeout=20000)
                print(f"⌨️ 正在输入提示词...")
                await page.fill(input_selector, prompt)
                
                # 模拟回车发送
                await page.keyboard.press("Enter")
                print("📤 请求已发送，等待 30 秒...")
            except Exception as e:
                print(f"❌ 查找输入框失败: {e}")
                # 截图排查
                await page.screenshot(path="grok_error_debug.png")
                print("📸 已保存调试截图 grok_error_debug.png")
                await context.close()
                return

            # 3. 等待生成内容
            await asyncio.sleep(30)

            # 4. 暴力提取页面所有文本
            print("🔍 尝试提取结果...")
            # 优先寻找回复容器文本，如果找不到则全量提取并由后续逻辑过滤
            result_text = await page.evaluate('''() => {
                // 尝试寻找最新的 Grok 回复块
                const entries = document.querySelectorAll('[data-testid="messageEntry"]');
                if (entries.length > 0) {
                    return entries[entries.length - 1].innerText;
                }
                return document.body.innerText;
            }''')

            # 5. 保存结果到 txt
            filename = f"grok_output_{int(time.time())}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(result_text)
            
            print(f"✅ 提取成功！内容已保存至: {filename}")
            print("\n--- 内容预览 ---")
            print(result_text[:300] + "...")

            # 脚本结束，暂时不关闭 context，让浏览器停留在那里方便手工确认
            # 如果需要完全闭闭，请取消下面注释
            # await context.close()

        except Exception as e:
            print(f"🔥 运行异常: {e}")

if __name__ == "__main__":
    test_prompt = "请帮我分析一下今晚欧冠阿森纳对阵开拉特的比赛，给出预测分析和比分预测建议。请尽可能详细，结合 X 上的实时信息。"
    asyncio.run(run_grok_test(test_prompt))
