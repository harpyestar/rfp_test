"""
Page Object Model 基类
封装所有页面通用的交互操作
所有超时值从 timeout_config 中读取，确保与 .env 配置一致
"""

from playwright.async_api import Page, expect
from utils.logger import get_logger
from utils.wait_helper import WaitHelper
from utils.timeout_config import timeout_config
from utils.config import config
from typing import Optional, Any


class BasePage:
    """Page Object Model 基类"""

    def __init__(self, page: Page):
        self.page = page
        self.logger = get_logger(self.__class__.__name__, config.log_level)
        self.wait_helper = WaitHelper()

    async def goto(self, url: str) -> None:
        self.logger.info(f"Navigating to {url}")
        # 使用 domcontentloaded 替代 networkidle，减少卡顿风险
        await self.page.goto(url, wait_until="domcontentloaded")
        # 仅在必要时等待网络空闲（可选，用于后续交互）
        try:
            await self.wait_helper.wait_for_load_state(
                self.page,
                state="domcontentloaded",
                timeout=timeout_config.get_element_timeout()
            )
        except Exception as e:
            self.logger.warning(f"DomContentLoaded wait raised: {str(e)}, continuing...")

    async def find_element(self, selector: str) -> Any:
        self.logger.debug(f"Finding element: {selector}")
        await self.wait_helper.wait_for_selector(
            self.page,
            selector,
            timeout=timeout_config.get_element_timeout()
        )
        return self.page.locator(selector)

    async def fill(self, selector: str, value: str) -> None:
        self.logger.info(f"Filling {selector} with {value}")
        locator = await self.find_element(selector)
        await locator.fill(value)

    async def click(self, selector: str) -> None:
        self.logger.info(f"Clicking {selector}")
        locator = await self.find_element(selector)
        await locator.click()

    async def get_text(self, selector: str) -> str:
        self.logger.debug(f"Getting text from {selector}")
        locator = await self.find_element(selector)
        return await locator.text_content() or ""

    async def get_attribute(self, selector: str, attribute: str) -> Optional[str]:
        self.logger.debug(f"Getting attribute '{attribute}' from {selector}")
        locator = await self.find_element(selector)
        return await locator.get_attribute(attribute)

    async def is_visible(self, selector: str) -> bool:
        try:
            locator = self.page.locator(selector)
            is_visible = await locator.is_visible()
            self.logger.debug(f"Element {selector} visible: {is_visible}")
            return is_visible
        except Exception as e:
            self.logger.warning(f"Element {selector} not found: {str(e)}")
            return False

    async def get_current_url(self) -> str:
        url = self.page.url
        self.logger.debug(f"Current URL: {url}")
        return url

    async def get_page_title(self) -> str:
        title = await self.page.title()
        self.logger.debug(f"Page title: {title}")
        return title

    async def screenshot(self, path: str) -> None:
        self.logger.info(f"Taking screenshot: {path}")
        await self.page.screenshot(path=path, full_page=True)

