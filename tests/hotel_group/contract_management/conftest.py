"""
HotelGroup 角色合同管理测试 fixtures
"""

import pytest
from pages.common.login_page import LoginPage
from utils.config import config
from utils.logger import get_logger

logger = get_logger("tests.hotel_group.contract_management.conftest", config.log_level)


@pytest.fixture(scope="module")
def page_module(browser, event_loop):
    """Module 级 page fixture，复用酒店集团端登录状态"""
    global _module_page, _module_context

    logger.info("Creating module-level page for hotel group login state reuse")

    async def create_module_page():
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()
        logger.info("Module-level page created for hotel group tests")
        return page, context

    _module_page, _module_context = event_loop.run_until_complete(create_module_page())

    yield _module_page

    async def close_module_page():
        logger.info("Closing hotel group module-level page and context")
        await _module_page.close()
        await _module_context.close()

    event_loop.run_until_complete(close_module_page())


@pytest.fixture(scope="module")
def hotel_group_user(page_module, event_loop):
    """HotelGroup 角色登录 fixture"""
    logger.info("Setting up hotel group user fixture")

    try:
        account = config.get_account("hotelgroup")
        logger.info(f"Loading hotel group account: {account['mobile']}")

        async def perform_login():
            login_page = LoginPage(page_module)
            return await login_page.login(account["mobile"], account["password"])

        result = event_loop.run_until_complete(perform_login())

        if result["success"]:
            logger.info("Hotel group user login successful")
            yield page_module
        else:
            error_msg = f"Hotel group user login failed: {result['message']}"
            logger.error(error_msg)
            raise Exception(error_msg)

    except Exception as e:
        error_msg = f"Failed to set up hotel group user fixture: {str(e)}"
        logger.error(error_msg)
        raise

    finally:
        logger.info("Hotel group user fixture cleanup completed")


@pytest.fixture(autouse=True)
def reset_to_hotel_group_home(page_module, event_loop):
    """每个用例执行前重置到酒店集团首页"""
    logger.info("Resetting page to hotel group home")

    async def navigate_home():
        home_url = config.base_url.rstrip("/") + "/hotelGroup.html#/home"
        logger.info(f"Navigating to hotel group home page: {home_url}")
        await page_module.goto(home_url, wait_until="domcontentloaded")
        logger.info("Page reset to hotel group home - ready for test execution")

    event_loop.run_until_complete(navigate_home())

    yield

    logger.info("Test completed - page state will be reset for next test")
