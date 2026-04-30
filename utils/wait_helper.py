"""
等待策略工具模块
提供 Playwright 等待操作的便捷封装
所有超时值从 timeout_config 中读取，确保与 .env 配置一致
"""

from typing import Optional, Callable
from playwright.async_api import Page, expect
import asyncio
from utils.timeout_config import timeout_config


class WaitHelper:
    """等待工具类"""

    @staticmethod
    async def wait_for_url(
        page: Page,
        url_pattern: str,
        timeout: Optional[int] = None
    ) -> None:
        """
        等待 URL 包含指定模式

        Args:
            page: Playwright Page 对象
            url_pattern: URL 模式（支持通配符 * ）
            timeout: 超时时间（毫秒），如不指定则使用 TIMEOUT_NAVIGATION
        """
        if timeout is None:
            timeout = timeout_config.get_navigation_timeout()
        try:
            await page.wait_for_url(url_pattern, timeout=timeout)
        except Exception as e:
            raise TimeoutError(f"URL '{url_pattern}' not found within {timeout}ms: {str(e)}")

    @staticmethod
    async def wait_for_selector(
        page: Page,
        selector: str,
        timeout: Optional[int] = None
    ) -> None:
        """
        等待元素出现

        Args:
            page: Playwright Page 对象
            selector: CSS 选择器
            timeout: 超时时间（毫秒），如不指定则使用 TIMEOUT_ELEMENT
        """
        if timeout is None:
            timeout = timeout_config.get_element_timeout()
        try:
            await page.wait_for_selector(selector, timeout=timeout)
        except Exception as e:
            raise TimeoutError(f"Selector '{selector}' not found within {timeout}ms: {str(e)}")

    @staticmethod
    async def wait_for_load_state(
        page: Page,
        state: str = "networkidle",
        timeout: Optional[int] = None
    ) -> None:
        """
        等待页面加载完成

        Args:
            page: Playwright Page 对象
            state: 加载状态 (load, domcontentloaded, networkidle)
            timeout: 超时时间（毫秒），如不指定则使用 TIMEOUT_PAGE_LOAD
        """
        if timeout is None:
            timeout = timeout_config.get_page_load_timeout()
        try:
            await page.wait_for_load_state(state, timeout=timeout)
        except Exception as e:
            raise TimeoutError(f"Page load state '{state}' not reached within {timeout}ms: {str(e)}")

    @staticmethod
    async def wait_for_text(
        page: Page,
        text: str,
        timeout: Optional[int] = None
    ) -> None:
        """
        等待页面包含指定文本

        Args:
            page: Playwright Page 对象
            text: 要查找的文本
            timeout: 超时时间（毫秒），如不指定则使用 TIMEOUT_ELEMENT
        """
        if timeout is None:
            timeout = timeout_config.get_element_timeout()
        try:
            await page.locator(f":has-text('{text}')").first.wait_for(timeout=timeout)
        except Exception as e:
            raise TimeoutError(f"Text '{text}' not found within {timeout}ms: {str(e)}")

    @staticmethod
    async def sleep(seconds: int) -> None:
        """
        异步睡眠（用于特殊等待场景）

        Args:
            seconds: 睡眠秒数
        """
        await asyncio.sleep(seconds)

