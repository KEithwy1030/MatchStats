
import asyncio
from playwright.async_api import async_playwright
import subprocess
import time
import sys
import socket
import os

# 设置输出编码为 UTF-8
if sys.stdout:
    sys.stdout.reconfigure(encoding='utf-8')

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

async def run_grok_real(port=9222):
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    user_data_dir = r"C:\Users\wuyon\AppData\Local\Google\Chrome\User Data"
    profile_name = "Profile 2"
    
    print(f"🔍 检查端口 {port} 是否占用...")
    if is_port_in_use(port):
        print(f"⚠️ 端口 {port} 已被占用，请确保没有任何 Chrome 实例正在运行，或者尝试其他端口。")
    
    print(f"📡 正在以调试模式启动真实 Chrome ({profile_name})，端口: {port}...")
    
    # 手动启动真实的 Chrome 进程
    cmd = [
        chrome_path,
        f"--remote-debugging-port={port}",
        f"--user-data-dir={user_data_dir}",
        f"--profile-directory={profile_name}",
        "--no-first-run",
        "--no-default-browser-check",
        "--remote-allow-origins=*",
        "https://grok.com/"
    ]
    
    # 启动进程
    try:
        subprocess.Popen(cmd)
    except Exception as e:
        print(f"❌ 启动 Chrome 失败: {e}")
        return

    # 给浏览器启动和建立监听的时间
    print("⏳ 等待浏览器启动...")
    
    async with async_playwright() as p:
        try:
            print(f"🔗 正在通过 CDP 端口 {port} 接管浏览器...")
            
            # 增加重试逻辑，等待端口就绪
            browser = None
            max_retries = 10
            for i in range(max_retries):
                try:
                    browser = await p.chromium.connect_over_cdp(f"http://localhost:{port}", timeout=5000)
                    break
                except Exception as e:
                    if i == max_retries - 1:
                        # 失败前最后看一眼 netstat
                        os.system(f"netstat -ano | findstr :{port}")
                        raise e
                    print(f"🔄 端口暂未就绪，重试中 ({i+1}/{max_retries})...")
                    await asyncio.sleep(2)
            
            # 通常第一个 context 就是刚刚启动的那个
            context = browser.contexts[0]
            
            # 寻找已经加载 grok.com 的页面
            page = None
            for p_obj in context.pages:
                if "grok.com" in p_obj.url:
                    page = p_obj
                    break
            
            if not page:
                page = await context.new_page()
                await page.goto("https://grok.com/")
            
            print(f"📌 成功接管！当前页面标题: {await page.title()}")
            
            # 等待 Grok 加载
            print("⏳ 等待页面稳定...")
            await page.wait_for_load_state("networkidle", timeout=30000)

            # 具体的 Grok 交互逻辑
            prompt = "请分析今晚欧冠焦点战阿森纳对阵主场作战的开拉特的比赛，结合实时动态给出预测和比分建议。"
            
            # grok.com 的输入框通常是 textarea
            input_selector = 'textarea'
            print(f"✍️ 正在定位输入框并发送提示词...")
            
            await page.wait_for_selector(input_selector, timeout=15000)
            await page.fill(input_selector, prompt)
            await page.keyboard.press("Enter")
            
            print("📤 已提交请求，强制等待 30 秒抓取结果...")
            await asyncio.sleep(30)
            
            # 提取内容
            result_text = await page.evaluate('''() => {
                const entries = document.querySelectorAll('[data-testid="messageEntry"]');
                return entries.length > 0 ? entries[entries.length - 1].innerText : document.body.innerText;
            }''')
            
            with open("grok_test_result.txt", "w", encoding="utf-8") as f:
                f.write(result_text)
                
            print(f"✅ 抓取完成！文件已存至: grok_test_result.txt")
            
        except Exception as e:
            print(f"🔥 接管失败: {e}")
            print(f"💡 建议：如果 9222 报错，请关闭所有 Chrome 窗口后再运行，或改用端口 9333。")

if __name__ == "__main__":
    # 按照用户建议，改用 9333 端口以避开潜在冲突
    asyncio.run(run_grok_real(9333))
