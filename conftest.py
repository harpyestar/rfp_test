"""
根级 conftest.py
全局 fixture 管理：浏览器、浏览器上下文、页面生命周期
"""

import pytest
import asyncio
from playwright.async_api import async_playwright
from utils.config import config
from utils.logger import get_logger

logger = get_logger("conftest", config.log_level)

# 全局变量
_playwright = None
_browser = None
_event_loop = None


@pytest.fixture(scope="session")
def event_loop():
    """创建会话级事件循环"""
    global _event_loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    _event_loop = loop
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def browser(event_loop):
    """
    浏览器 fixture（会话级）
    启动 Chromium 浏览器，在所有测试结束后关闭
    """
    global _playwright, _browser

    async def launch_browser():
        global _playwright
        logger.info("Initializing Playwright")
        _playwright = await async_playwright().start()
        logger.info("Starting browser")
        browser = await _playwright.chromium.launch(
            headless=config.headless,
            slow_mo=config.slow_mo
        )
        logger.info(f"Browser launched - Headless: {config.headless}, SlowMo: {config.slow_mo}ms")
        return browser

    logger.info("Creating browser fixture")
    _browser = event_loop.run_until_complete(launch_browser())
    yield _browser

    # Cleanup
    async def close_browser():
        global _browser, _playwright
        logger.info("Closing browser")
        await _browser.close()
        logger.info("Stopping Playwright")
        await _playwright.stop()

    event_loop.run_until_complete(close_browser())


@pytest.fixture
def browser_context(browser, event_loop):
    """
    浏览器上下文 fixture（测试级）
    每个测试获得独立的浏览器上下文
    """
    async def create_context():
        logger.info("Creating new browser context")
        return await browser.new_context(viewport={"width": 1920, "height": 1080})

    context = event_loop.run_until_complete(create_context())
    yield context

    # Cleanup
    async def close_context():
        logger.info("Closing browser context")
        await context.close()

    event_loop.run_until_complete(close_context())


@pytest.fixture
def page(browser_context, event_loop):
    """
    页面 fixture（测试级）
    每个测试获得独立的页面
    """
    async def create_page():
        logger.info("Creating new page")
        return await browser_context.new_page()

    page = event_loop.run_until_complete(create_page())
    yield page

    # Cleanup
    async def close_page():
        logger.info("Closing page")
        await page.close()

    event_loop.run_until_complete(close_page())


def pytest_configure(config):
    """pytest 启动时执行"""
    from utils.config import config as app_config
    logger.info("=" * 80)
    logger.info("RFP UI Test Suite Started")
    logger.info(f"Environment: {app_config.test_env}")
    logger.info(f"Base URL: {app_config.base_url}")
    logger.info("=" * 80)


def pytest_sessionfinish(session, exitstatus):
    """pytest 结束时执行"""
    logger.info("=" * 80)
    logger.info("RFP UI Test Suite Finished")
    logger.info(f"Exit Status: {exitstatus}")
    logger.info("=" * 80)
