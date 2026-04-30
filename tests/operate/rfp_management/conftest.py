"""
Operate 角色测试的 conftest.py
定义 operate 相关的 fixtures
支持参数化测试中的登录状态复用（Module 级）
"""

import pytest
from pages.common.login_page import LoginPage
from utils.config import config
from utils.logger import get_logger

logger = get_logger("tests.operate.rfp_management.conftest", config.log_level)


@pytest.fixture(scope="module")
def page_module(browser, event_loop):
    """
    Module 级 page fixture - 整个模块共享同一个 page

    用于参数化测试中复用登录状态：
    - 所有参数化用例共用一个 page
    - 登录仅执行一次
    - 后续用例都复用同一登录状态，避免重复登录

    作用域: module
    返回:
        page: Playwright Page 对象（模块级共享）
    """
    global _module_page, _module_context

    logger.info("Creating module-level page for login state reuse")

    async def create_module_page():
        context = await browser.new_context()
        page = await context.new_page()
        logger.info("Module-level page created - ready for shared login state")
        return page, context

    _module_page, _module_context = event_loop.run_until_complete(create_module_page())

    yield _module_page

    # Cleanup
    async def close_module_page():
        logger.info("Closing module-level page and context")
        await _module_page.close()
        await _module_context.close()

    event_loop.run_until_complete(close_module_page())


@pytest.fixture(scope="module")
def operate_user(page_module, event_loop):
    """
    Operate 角色用户登录 fixture（Module 级）

    特点：
    - 作用域: module（同一模块内只登录一次）
    - 所有参数化用例共享登录状态
    - 参数化的多条用例复用同一登录会话

    Args:
        page_module: Module 级 page 对象
        event_loop: 事件循环

    Returns:
        page_module: 已登录的 Page 对象
    """
    logger.info("Setting up operate user fixture [SCOPE: module] - performing login ONCE for all parametrized tests")

    try:
        # 获取 operate 账号信息
        account = config.get_account("operate")
        logger.info(f"Loading operate account: {account['mobile']}")

        # 创建 LoginPage 对象并执行登录
        async def perform_login():
            login_page = LoginPage(page_module)
            result = await login_page.login(account["mobile"], account["password"])
            return result

        result = event_loop.run_until_complete(perform_login())

        if result["success"]:
            logger.info(f"Operate user login successful (ONE-TIME for all tests in module)")
            logger.info(f"   URL: {result['url']}")
            logger.info(f"   Tip:All parametrized test cases will reuse this login state")
            # 登录成功后，返回已登录状态的 page
            yield page_module
        else:
            error_msg = f"Operate user login failed: {result['message']}"
            logger.error(error_msg)
            raise Exception(error_msg)

    except Exception as e:
        error_msg = f"Failed to set up operate user fixture: {str(e)}"
        logger.error(error_msg)
        raise

    finally:
        logger.info("Operate user fixture cleanup - page ready for next test")


@pytest.fixture(autouse=True)
def reset_to_home_page(page_module, event_loop):
    """
    自动重置页面到 /home - 确保每个测试用例都从已知状态开始

    作用：
    - 在每个测试方法执行前自动执行
    - 导航到 /home 页面，重置页面状态
    - 确保参数化的多个用例都能从同一起点开始
    - 避免前一个用例的页面状态影响后续用例

    使用场景：
    - 第一个用例执行完后，页面可能停留在某个地方
    - 第二个用例开始时，先导航回 /home
    - 这样所有用例都有一个一致的初始状态
    """
    logger.info("Resetting page to /home - ensuring consistent test state")

    async def navigate_home():
        # 处理 base_url 末尾的斜杠，避免 URL 重复
        base_url = config.base_url.rstrip('/')
        home_url = f"{base_url}/home"
        logger.info(f"Navigating to home page: {home_url}")
        await page_module.goto(home_url, wait_until="networkidle")
        logger.info("Page reset to /home - ready for test execution")

    event_loop.run_until_complete(navigate_home())

    yield  # 测试执行

    logger.info("Test completed - page state will be reset for next test")
