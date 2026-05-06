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

