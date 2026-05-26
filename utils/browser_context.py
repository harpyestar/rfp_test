"""
浏览器上下文创建工具
统一管理反检测配置，所有 conftest 通过此函数创建 context
"""

from playwright.async_api import Browser


async def create_browser_context(browser: Browser, **kwargs):
    defaults = {
        "viewport": {"width": 1920, "height": 1080},
        "user_agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "locale": "zh-CN",
    }
    defaults.update(kwargs)
    return await browser.new_context(**defaults)