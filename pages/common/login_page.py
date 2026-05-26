"""
登录页面对象模型
处理登录相关的交互操作
所有超时值从 timeout_config 中读取，确保与 .env 配置一致
"""

import asyncio
import random
from playwright.async_api import Page
from pages.common.base_page import BasePage
from utils.config import config
from utils.timeout_config import timeout_config
from typing import Dict, Any


class LoginPage(BasePage):
    """登录页 Page Object"""

    MOBILE_INPUT = 'input[placeholder="请输入手机号"]'
    PASSWORD_INPUT = 'input[type="password"]'
    LOGIN_BUTTON = 'button:has-text("登录")'  # Button has text "Login", not type="submit"
    LOGIN_FORM = 'form'

    def __init__(self, page: Page):
        super().__init__(page)

    async def navigate_to_login(self, max_retries: int = 3) -> None:
        login_url = config.base_url.rstrip('/') + '/login.html#/login'
        self.logger.info(f"Login URL: {login_url}")

        # 随机初始延迟(0~3s)，多 worker 并发时错开登录时机
        init_jitter = random.uniform(0, 3)
        await asyncio.sleep(init_jitter)

        last_error = None
        for attempt in range(1, max_retries + 1):
            try:
                await self.page.goto(login_url, wait_until="networkidle", timeout=timeout_config.get_navigation_timeout())
                self.logger.info("Server responded, waiting for form elements...")
                await self.wait_helper.wait_for_selector(
                    self.page,
                    'form, input[type="text"], input[type="password"]',
                    timeout=timeout_config.get_element_timeout()
                )
                self.logger.info("Login form elements rendered successfully")
                return
            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    delay = 5 * attempt + random.uniform(0, 3)
                    self.logger.warning(f"导航登录页失败(第{attempt}次): {e}, {delay:.1f}秒后重试...")
                    await asyncio.sleep(delay)

        self.logger.error(f"导航登录页失败(已重试{max_retries}次): {last_error}")
        raise last_error

    async def login(self, mobile: str, password: str) -> Dict[str, Any]:
        try:
            self.logger.info(f"Logging in with mobile: {mobile}")

            await self.navigate_to_login()

            self.logger.debug("Filling mobile field")
            await self.fill(self.MOBILE_INPUT, mobile)

            self.logger.debug("Filling password field")
            await self.fill(self.PASSWORD_INPUT, password)

            self.logger.info("Clicking login button")
            await self.click(self.LOGIN_BUTTON)

            self.logger.debug("Waiting for login to complete")
            # 等待 URL 变更到 "**/home*"
            await self.wait_helper.wait_for_url(
                self.page,
                "**/home*",
                timeout=timeout_config.get_navigation_timeout()
            )

            current_url = await self.get_current_url()
            self.logger.info(f"Login successful. Current URL: {current_url}")

            return {
                "success": True,
                "url": current_url,
                "message": "Login successful"
            }

        except Exception as e:
            error_message = f"Login failed: {str(e)}"
            self.logger.error(error_message)
            current_url = await self.get_current_url()

            return {
                "success": False,
                "url": current_url,
                "message": error_message
            }

    async def is_login_page(self) -> bool:
        is_visible = await self.is_visible(self.LOGIN_FORM)
        self.logger.debug(f"Is login page: {is_visible}")
        return is_visible

