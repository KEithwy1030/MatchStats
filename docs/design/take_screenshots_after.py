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
        
        # 1. Desktop 1920x1080
        desktop_page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        await desktop_page.goto(URL, wait_until="networkidle")
        await asyncio.sleep(2)
        await desktop_page.screenshot(path=str(SCREENSHOTS_DIR / "after_desktop.png"), full_page=False)
        print("Desktop screenshot taken.")

        # 2. Desktop Modal
        match_item = desktop_page.locator(".match-row-card").first
        if await match_item.count() > 0:
            await match_item.click()
            await asyncio.sleep(1)
            await desktop_page.screenshot(path=str(SCREENSHOTS_DIR / "after_modal_desktop.png"), full_page=False)
            print("Modal desktop screenshot taken.")
            await desktop_page.locator(".modal-close-btn").click()
            await asyncio.sleep(0.5)

        # 3. Mobile 390x844
        mobile_page = await browser.new_page(
            viewport={"width": 390, "height": 844},
            is_mobile=True,
            has_touch=True,
            device_scale_factor=2
        )
        await mobile_page.goto(URL, wait_until="networkidle")
        await asyncio.sleep(2)
        await mobile_page.screenshot(path=str(SCREENSHOTS_DIR / "after_mobile.png"), full_page=False)
        print("Mobile screenshot taken.")

        # 4. Mobile Modal
        mobile_match = mobile_page.locator(".match-row-card").first
        if await mobile_match.count() > 0:
            await mobile_match.click()
            await asyncio.sleep(1)
            await mobile_page.screenshot(path=str(SCREENSHOTS_DIR / "after_modal_mobile.png"), full_page=False)
            print("Mobile modal screenshot taken.")

        await browser.close()
        print("All validation screenshots completed successfully.")

if __name__ == "__main__":
    asyncio.run(main())
