import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

SCREENSHOTS_DIR = Path(r"E:\CursorData\3.MatchStats\docs\design\screenshots")
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
URL = "http://127.0.0.1:8790/matchstats/"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path=CHROME_PATH,
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        
        # Desktop
        desktop_page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        await desktop_page.goto(URL, wait_until="networkidle")
        await asyncio.sleep(2)
        await desktop_page.screenshot(path=str(SCREENSHOTS_DIR / "before_desktop.png"), full_page=False)
        print("Desktop screenshot taken.")

        # Modal
        match_item = desktop_page.locator(".match-item").first
        if await match_item.count() > 0:
            await match_item.click()
            await asyncio.sleep(1)
            await desktop_page.screenshot(path=str(SCREENSHOTS_DIR / "before_modal_desktop.png"), full_page=False)
            print("Modal screenshot taken.")
            await desktop_page.locator(".modal-close").click()
            await asyncio.sleep(0.5)

        # Mobile
        mobile_page = await browser.new_page(
            viewport={"width": 390, "height": 844},
            is_mobile=True,
            has_touch=True,
            device_scale_factor=2
        )
        await mobile_page.goto(URL, wait_until="networkidle")
        await asyncio.sleep(2)
        await mobile_page.screenshot(path=str(SCREENSHOTS_DIR / "before_mobile.png"), full_page=False)
        print("Mobile screenshot taken.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
