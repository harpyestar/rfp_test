"""
登录测试模块
测试所有三个角色的登录功能
"""

import allure
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
        验证用户能够使用有效的手机号和密码成功登录

        Args:
            login_page: LoginPage fixture
            account_info: 账号信息（parametrized）
            account_type: 账号类型（parametrized）
        """
        logger.info(f"Starting login test for account type: {account_type}")

        with allure.step("【步骤 1】进入登录页面"):
            await login_page.navigate_to_login()

        with allure.step(f"【步骤 2】输入手机号: {account_info['mobile']}"):
            await login_page.fill_mobile(account_info["mobile"])

        with allure.step("【步骤 3】输入密码"):
            await login_page.fill_password(account_info["password"])

        with allure.step("【步骤 4】点击登录按钮"):
            await login_page.click_login_button()

        with allure.step("【步骤 5】等待页面跳转至 /home"):
            current_url = await login_page.wait_for_login_redirect()
            assert "/home" in current_url, f"Expected /home in URL, got {current_url}"

        with allure.step("【步骤 6】验证页面标题不为空"):
            page_title = await login_page.get_page_title()
            assert page_title, "Page title is empty"

        logger.info(f"✓ Test passed for {account_type} ({account_info['role_name']})")

