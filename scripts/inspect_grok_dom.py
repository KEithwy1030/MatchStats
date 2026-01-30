
import asyncio
from playwright.async_api import async_playwright
import sys

if sys.stdout:
    sys.stdout.reconfigure(encoding='utf-8')

async def inspect_grok_dom():
    """DOM 侦查工具：找出 Grok 回复内容的真实位置"""
    
    async with async_playwright() as p:
        print("🔗 连接浏览器...")
        browser = await p.chromium.connect_over_cdp("http://localhost:9222", timeout=30000)
        
        context = browser.contexts[0]
        page = None
        
        for p_obj in context.pages:
            if "grok.com" in p_obj.url:
                page = p_obj
                break
        
        if not page:
            print("❌ 未找到 Grok 页面")
            return
        
        print("✅ 已找到 Grok 页面")
        print("\n🔍 正在分析 DOM 结构...\n")
        
        # 尝试多种选择器并输出结果
        selectors_to_test = [
            ('messageEntry', '[data-testid="messageEntry"]'),
            ('article 标签', 'article'),
            ('包含message的div', 'div[class*="message"]'),
            ('包含response的div', 'div[class*="response"]'),
            ('包含answer的div', 'div[class*="answer"]'),
            ('main标签下所有div', 'main div'),
            ('role=article', '[role="article"]'),
        ]
        
        for name, selector in selectors_to_test:
            try:
                elements = await page.query_selector_all(selector)
                count = len(elements)
                
                if count > 0:
                    print(f"📌 {name} ({selector})")
                    print(f"   找到 {count} 个元素")
                    
                    # 提取最后一个元素的文本预览
                    if count > 0:
                        last_text = await elements[-1].inner_text()
                        preview = last_text[:100].replace('\n', ' ')
                        print(f"   最后一个元素内容预览: {preview}...")
                        print(f"   完整长度: {len(last_text)} 字符")
                    print()
            except Exception as e:
                print(f"❌ {name}: 错误 - {e}\n")
        
        # 特别提取：获取所有可见的长文本块
        print("=" * 60)
        print("🎯 智能检测：所有包含超过500字符的文本容器")
        print("=" * 60)
        
        long_texts = await page.evaluate('''() => {
            const results = [];
            const allElements = document.querySelectorAll('div, article, section, main');
            
            allElements.forEach((el, index) => {
                const text = el.innerText;
                if (text && text.length > 500) {
                    // 避免嵌套重复
                    let isChild = false;
                    for (let parent = el.parentElement; parent; parent = parent.parentElement) {
                        if (parent.innerText === text) {
                            isChild = true;
                            break;
                        }
                    }
                    
                    if (!isChild) {
                        results.push({
                            tag: el.tagName,
                            className: el.className,
                            textLength: text.length,
                            preview: text.substring(0, 150)
                        });
                    }
                }
            });
            
            return results;
        }''')
        
        for idx, item in enumerate(long_texts[:5], 1):  # 只显示前5个
            print(f"\n容器 #{idx}:")
            print(f"  标签: {item['tag']}")
            print(f"  Class: {item['className']}")
            print(f"  长度: {item['textLength']} 字符")
            print(f"  内容预览: {item['preview']}...")

if __name__ == "__main__":
    asyncio.run(inspect_grok_dom())
