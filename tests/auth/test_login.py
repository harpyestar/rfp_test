"""
登录测试模块
测试所有三个角色的登录功能
"""

import pytest
from pages.common.login_page import LoginPage
from utils.logger import get_logger
from utils.config import config

logger = get_logger("tests.auth.test_login", config.log_level)


@pytest.mark.auth
@pytest.mark.smoke
class TestLogin:
    """登录功能测试类"""

    async def test_login_success(self, login_page: LoginPage, account_info: dict, account_type: str):
        """
        测试登录成功
        验证用户能够使用有效的邮箱和密码成功登录

        Args:
            login_page: LoginPage fixture
            account_info: 账号信息（parametrized）
            account_type: 账号类型（parametrized）
        """
        logger.info(f"Starting login test for account type: {account_type}")
        result = await login_page.login(mobile=account_info["mobile"], password=account_info["password"])
        assert result["success"] is True, f"Login failed: {result['message']}"
        assert "/home" in result["url"], f"Expected /home in URL, got {result['url']}"
        page_title = await login_page.get_page_title()
        assert page_title, "Page title is empty"
        logger.info(f"✓ Test passed for {account_type} ({account_info['role_name']})")

    async def test_login_url_navigation(self, login_page: LoginPage, account_info: dict, account_type: str):
        """
        测试登录后的 URL 跳转
        验证成功登录后，页面 URL 从登录页跳转到首页 (/home)

        Args:
            login_page: LoginPage fixture
            account_info: 账号信息（parametrized）
            account_type: 账号类型（parametrized）
        """
        logger.info(f"Testing URL navigation for {account_type}")
        await login_page.navigate_to_login()
        login_url = await login_page.get_current_url()
        result = await login_page.login(mobile=account_info["mobile"], password=account_info["password"])
        assert result["success"] is True
        current_url = result["url"]
        assert "/home" in current_url, f"Expected /home in URL, got {current_url}"
        assert current_url != login_url, "URL should change after login"
        logger.info(f"✓ URL navigation test passed for {account_type}")

    async def test_login_page_title(self, login_page: LoginPage, account_info: dict, account_type: str):
        """
        测试登录后的页面标题
        验证登录成功后，页面标题正常显示（不为空且不含 'error'）

        Args:
            login_page: LoginPage fixture
            account_info: 账号信息（parametrized）
            account_type: 账号类型（parametrized）
        """
        logger.info(f"Testing page title for {account_type}")
        result = await login_page.login(mobile=account_info["mobile"], password=account_info["password"])
        assert result["success"] is True
        page_title = await login_page.get_page_title()
        assert page_title, "Page title should not be empty"
        assert "error" not in page_title.lower(), f"Title contains error: {page_title}"
        logger.info(f"✓ Page title test passed for {account_type}")
