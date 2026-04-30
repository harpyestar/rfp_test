"""
测试级 conftest.py
参数化测试、账号管理、登录状态
"""

import pytest
from playwright.async_api import Page
from pages.common.login_page import LoginPage
from utils.config import config
from utils.logger import get_logger

logger = get_logger("tests.conftest", config.log_level)


def pytest_generate_tests(metafunc):
    """
    pytest 参数化钩子
    如果测试函数需要 account_type 参数，自动参数化为三个角色
    """
    if "account_type" in metafunc.fixturenames:
        account_types = ["operate", "hotel", "hotelgroup"]
        metafunc.parametrize("account_type", account_types)


@pytest.fixture
def login_page(page):
    """
    登录页 fixture
    返回 LoginPage 对象，用于测试登录功能
    """
    logger.info("Creating LoginPage object")
    return LoginPage(page)


@pytest.fixture
def account_info(account_type: str) -> dict:
    """
    账号信息 fixture
    根据 account_type 参数获取对应角色的账号信息

    Args:
        account_type: 账号类型 (operate, hotel, hotelgroup)

    Returns:
        dict: 账号信息 {mobile, password, role_name}

    Raises:
        KeyError: 账号类型不存在
    """
    logger.info(f"Loading account info for: {account_type}")
    try:
        account = config.get_account(account_type)
        logger.info(f"Account loaded - Type: {account_type}, Mobile: {account['mobile']}")
        return account
    except KeyError as e:
        logger.error(f"Account not found: {account_type}")
        raise
