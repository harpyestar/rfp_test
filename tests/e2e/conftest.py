"""
E2E 测试 conftest.py
提供跨端测试所需的双 context + page 夹具

方案说明：
同一个 browser 下创建两个独立的 browser_context，cookies / storage 完全隔离，
实现 Operate 和 Hotel 两个角色的独立登录。
"""

import pytest
from pages.common.login_page import LoginPage
from utils.config import config
from utils.logger import get_logger

logger = get_logger("tests.e2e.conftest", config.log_level)


@pytest.fixture
def e2e_pages(browser, event_loop):
    """
    E2E 双端页面夹具

    创建一个 browser，两个独立 context + page：
    - operate: 平台端已登录 page
    - hotel: 酒店端已登录 page

    context 级别隔离，cookies / localStorage 互不干扰。

    Yields:
        dict: {"operate": Page, "hotel": Page}
    """
    operate_ctx = None
    operate_page = None
    hotel_ctx = None
    hotel_page = None

    async def setup():
        nonlocal operate_ctx, operate_page, hotel_ctx, hotel_page

        logger.info("=== 创建 Operate context + page ===")
        operate_ctx = await browser.new_context(
            viewport={"width": 1920, "height": 1080}
        )
        operate_page = await operate_ctx.new_page()
        login_page = LoginPage(operate_page)
        operate_account = config.get_account("operate")
        result = await login_page.login(
            operate_account["mobile"], operate_account["password"]
        )
        if not result["success"]:
            raise Exception(f"Operate 登录失败: {result['message']}")

        logger.info("=== 创建 Hotel context + page ===")
        hotel_ctx = await browser.new_context(
            viewport={"width": 1920, "height": 1080}
        )
        hotel_page = await hotel_ctx.new_page()
        login_page = LoginPage(hotel_page)
        hotel_account = config.get_account("hotel")
        result = await login_page.login(
            hotel_account["mobile"], hotel_account["password"]
        )
        if not result["success"]:
            raise Exception(f"Hotel 登录失败: {result['message']}")

        logger.info("E2E 双端页面创建完成，Operate + Hotel 均已登录")
        return operate_page, hotel_page

    operate_page, hotel_page = event_loop.run_until_complete(setup())
    yield {"operate": operate_page, "hotel": hotel_page}

    # Cleanup
    async def cleanup():
        nonlocal operate_ctx, operate_page, hotel_ctx, hotel_page
        logger.info("清理 E2E 双端页面")
        if operate_page:
            await operate_page.close()
        if operate_ctx:
            await operate_ctx.close()
        if hotel_page:
            await hotel_page.close()
        if hotel_ctx:
            await hotel_ctx.close()

    event_loop.run_until_complete(cleanup())