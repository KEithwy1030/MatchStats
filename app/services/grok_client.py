"""
Grok Client Service

Handles CDP connection to Grok and prediction extraction.
"""

import asyncio
from typing import Optional
from playwright.async_api import async_playwright


class GrokClient:
    """Client for Grok predictions via CDP"""

    def __init__(self, cdp_url: str = "http://localhost:9222"):
        self.cdp_url = cdp_url
        self.grok_url = "https://grok.com"
        self.wait_seconds = 60  # Wait time for Grok to search and analyze

    async def predict_match(self, match_info: dict) -> Optional[str]:
        """
        Get prediction for a single match

        Args:
            match_info: Dict with keys: match_id, league, home_team, away_team, match_time

        Returns:
            Prediction text or None if failed
        """
        try:
            # Connect to Chrome via CDP
            p = await async_playwright().start()
            browser = await p.chromium.connect_over_cdp(self.cdp_url)

            context = browser.contexts[0]
            page = context.pages[0] if context.pages else await context.new_page()

            # Navigate to Grok
            await page.goto(self.grok_url, wait_until='networkidle', timeout=30000)
            await asyncio.sleep(2)

            # Build prompt
            prompt = self._build_prompt(match_info)

            # Send to Grok
            input_element = await self._find_input_element(page)
            if not input_element:
                print(f"    [x] Cannot find input box for match {match_info['match_id']}")
                await p.stop()
                return None

            await input_element.click()
            await asyncio.sleep(0.5)
            await input_element.fill('')
            await input_element.type(prompt, delay=20)
            await page.keyboard.press('Enter')

            print(f"    [OK] Request sent, waiting {self.wait_seconds}s...")

            # Wait for response
            await asyncio.sleep(self.wait_seconds)

            # Extract response
            response_text = await self._extract_response(page)

            if response_text and len(response_text) > 50:
                print(f"    [OK] Got response ({len(response_text)} chars)")
                await p.stop()
                return response_text
            else:
                print(f"    [x] Response too short or empty")
                await p.stop()
                return None

        except Exception as e:
            print(f"    [x] Error: {e}")
            return None

    def _build_prompt(self, match_info: dict) -> str:
        """Build prediction prompt for a match"""
        return f"""请联网搜索这场比赛的详细赛前数据并进行分析：

联赛：{match_info['league']}
主队：{match_info['home_team']}
客队：{match_info['away_team']}
比赛时间：{match_info['match_time']}

请搜索并提供以下信息：
1. 两队近期状态（最近5场比赛）
2. 伤停情况
3. 历史交锋记录
4. 数据分析（进球/失球统计等）
5. 综合分析和预测

请以清晰易读的文本格式返回所有信息，保持原有的段落和格式。
不要使用 JSON 或代码块，直接返回纯文本分析即可。
"""

    async def _find_input_element(self, page):
        """Find Grok input element"""
        selectors = [
            'textarea[placeholder*="message" i]',
            'textarea',
            '[contenteditable="true"]',
        ]

        for selector in selectors:
            try:
                element = await page.wait_for_selector(selector, timeout=3000)
                if element:
                    return element
            except:
                continue
        return None

    async def _extract_response(self, page) -> Optional[str]:
        """Extract Grok's response text"""
        selectors = [
            '[data-message-author="assistant"]',
            '[class*="assistant-message"]',
            'div[class*="message"]',
        ]

        for selector in selectors:
            try:
                elements = await page.query_selector_all(selector)
                if elements and len(elements) > 0:
                    latest = elements[-1]
                    text = await latest.inner_text()
                    if len(text) > 50:
                        return text
            except:
                continue
        return None
