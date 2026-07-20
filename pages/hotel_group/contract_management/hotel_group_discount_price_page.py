"""
酒店集团端集团折扣报价页面对象
"""

from playwright.async_api import Page
from pages.common.base_page import BasePage
from utils.config import config
from utils.timeout_config import timeout_config


class HotelGroupDiscountPricePage(BasePage):
    """酒店集团端集团折扣报价页面对象"""

    HOME_PATH = "/hotelGroup.html#/home"
    CONTRACT_PROJECT_MENU_TEXT = "签约项目"
    PROJECT_QUOTATION_OVERVIEW_TAB_TEXT = "项目报价总览"
    PROJECT_INPUT_CONTAINER_SELECTOR = "label.c-input"
    PROJECT_INPUT_TITLE_TEXT = "项目"
    PROJECT_INPUT_SELECTOR = 'input[placeholder="请输入..."][type="text"]'
    SEARCH_BUTTON_SELECTOR = ".c-icon-search"
    GROUP_DISCOUNT_BUTTON_TEXT = "集团折扣"
    EXPIRED_TOAST_TEXT = "项目签约时间已经结束"

    def __init__(self, page: Page):
        super().__init__(page)

    async def navigate_to_home(self) -> None:
        home_url = config.base_url.rstrip("/") + self.HOME_PATH
        self.logger.info(f"正在导航到酒店集团首页: {home_url}")
        await self.goto(home_url, timeout=timeout_config.get_navigation_timeout())
        await self.wait_helper.wait_for_load_state(
            self.page,
            state="domcontentloaded",
            timeout=timeout_config.get_page_load_timeout(),
        )
        self.logger.info("酒店集团首页加载完成")

    async def open_contract_project_menu(self) -> None:
        self.logger.info("正在展开侧边栏'签约项目'菜单")
        menu_item = self.page.get_by_text(self.CONTRACT_PROJECT_MENU_TEXT, exact=True).first
        await menu_item.wait_for(timeout=timeout_config.get_element_timeout())
        await menu_item.click()

        self.logger.info("正在点击子菜单'签约项目'进入签约项目页面")
        submenu_item = self.page.get_by_text(self.CONTRACT_PROJECT_MENU_TEXT, exact=True).nth(1)
        await submenu_item.wait_for(timeout=timeout_config.get_element_timeout())
        await submenu_item.click()
        self.logger.info("已进入签约项目页面")

    async def select_project_quotation_overview_tab(self) -> None:
        self.logger.info(f"正在切换到'{self.PROJECT_QUOTATION_OVERVIEW_TAB_TEXT}'标签页")
        tab = self.page.get_by_text(self.PROJECT_QUOTATION_OVERVIEW_TAB_TEXT, exact=True)
        await tab.wait_for(timeout=timeout_config.get_element_timeout())
        await tab.click()

        self.logger.info("等待项目搜索输入框加载")
        project_input = (
            self.page.locator(self.PROJECT_INPUT_CONTAINER_SELECTOR)
            .filter(has_text=self.PROJECT_INPUT_TITLE_TEXT)
            .locator(self.PROJECT_INPUT_SELECTOR)
        )
        await project_input.wait_for(timeout=timeout_config.get_element_timeout())
        self.logger.info("'项目报价总览'标签页切换完成")

    async def search_project(self, project_name: str) -> None:
        self.logger.info(f"正在输入项目名称进行搜索: {project_name}")
        project_input = (
            self.page.locator(self.PROJECT_INPUT_CONTAINER_SELECTOR)
            .filter(has_text=self.PROJECT_INPUT_TITLE_TEXT)
            .locator(self.PROJECT_INPUT_SELECTOR)
        )
        await project_input.wait_for(timeout=timeout_config.get_element_timeout())
        await project_input.fill(project_name)

        self.logger.info("正在点击搜索按钮")
        search_button = self.page.locator(self.SEARCH_BUTTON_SELECTOR).first
        await search_button.wait_for(timeout=timeout_config.get_element_timeout())
        await search_button.click()

        self.logger.info(f"搜索完成，已找到项目: {project_name}")

    async def click_first_group_discount_button(self) -> None:
        self.logger.info(f"正在点击首个'{self.GROUP_DISCOUNT_BUTTON_TEXT}'按钮")
        group_discount_button = (
            self.page.locator("a.c-button-link")
            .filter(has_text=self.GROUP_DISCOUNT_BUTTON_TEXT)
            .last
        )
        await group_discount_button.wait_for(timeout=timeout_config.get_element_timeout())
        await group_discount_button.click()
        self.logger.info("已点击集团折扣按钮，正在跳转至详情页")

    async def wait_for_discount_detail_page(self) -> None:
        self.logger.info("等待集团折扣详情页加载")
        await self.wait_helper.wait_for_load_state(
            self.page,
            state="domcontentloaded",
            timeout=timeout_config.get_page_load_timeout(),
        )
        try:
            await self.page.get_by_text(self.GROUP_DISCOUNT_BUTTON_TEXT, exact=True).first.wait_for(
                state="detached",
                timeout=timeout_config.get_navigation_timeout(),
            )
            self.logger.info("集团折扣详情页加载完成")
        except Exception:
            self.logger.info("集团折扣按钮未消失，可能仍停留在列表页，继续执行")

    async def has_expired_toast(self) -> bool:
        self.logger.debug(f"正在检查是否出现'{self.EXPIRED_TOAST_TEXT}'提示")
        toast = self.page.get_by_text(self.EXPIRED_TOAST_TEXT, exact=True)
        try:
            await toast.wait_for(timeout=1000)
            visible = await toast.is_visible()
            if visible:
                self.logger.warning(f"检测到'{self.EXPIRED_TOAST_TEXT}'提示")
            return visible
        except Exception:
            self.logger.debug(f"未检测到'{self.EXPIRED_TOAST_TEXT}'提示")
            return False
