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
    SEARCH_BUTTON_SELECTOR = ".ml-15 > div"
    GROUP_DISCOUNT_BUTTON_TEXT = "集团折扣"
    EXPIRED_TOAST_TEXT = "项目签约时间已经结束"

    def __init__(self, page: Page):
        super().__init__(page)

    async def navigate_to_home(self) -> None:
        home_url = config.base_url.rstrip("/") + self.HOME_PATH
        self.logger.info(f"Navigating to hotel group home page: {home_url}")
        await self.page.goto(
            home_url,
            wait_until="domcontentloaded",
            timeout=timeout_config.get_navigation_timeout(),
        )
        await self.wait_helper.wait_for_load_state(
            self.page,
            state="domcontentloaded",
            timeout=timeout_config.get_page_load_timeout(),
        )

    async def open_contract_project_menu(self) -> None:
        menu_item = self.page.get_by_text(self.CONTRACT_PROJECT_MENU_TEXT, exact=True).first
        await menu_item.wait_for(timeout=timeout_config.get_element_timeout())
        await menu_item.click()

        submenu_item = self.page.get_by_text(self.CONTRACT_PROJECT_MENU_TEXT, exact=True).nth(1)
        await submenu_item.wait_for(timeout=timeout_config.get_element_timeout())
        await submenu_item.click()

    async def select_project_quotation_overview_tab(self) -> None:
        tab = self.page.get_by_text(self.PROJECT_QUOTATION_OVERVIEW_TAB_TEXT, exact=True)
        await tab.wait_for(timeout=timeout_config.get_element_timeout())
        await tab.click()

        project_input = (
            self.page.locator(self.PROJECT_INPUT_CONTAINER_SELECTOR)
            .filter(has_text=self.PROJECT_INPUT_TITLE_TEXT)
            .locator(self.PROJECT_INPUT_SELECTOR)
        )
        await project_input.wait_for(timeout=timeout_config.get_element_timeout())

    async def search_project(self, project_name: str) -> None:
        project_input = (
            self.page.locator(self.PROJECT_INPUT_CONTAINER_SELECTOR)
            .filter(has_text=self.PROJECT_INPUT_TITLE_TEXT)
            .locator(self.PROJECT_INPUT_SELECTOR)
        )
        await project_input.wait_for(timeout=timeout_config.get_element_timeout())
        await project_input.fill(project_name)

        search_button = self.page.locator(self.SEARCH_BUTTON_SELECTOR).first
        await search_button.wait_for(timeout=timeout_config.get_element_timeout())
        await search_button.click()

        await self.page.get_by_text(project_name, exact=True).first.wait_for(
            timeout=timeout_config.get_element_timeout()
        )

    async def click_first_group_discount_button(self) -> None:
        group_discount_button = self.page.get_by_text(self.GROUP_DISCOUNT_BUTTON_TEXT, exact=True).first
        await group_discount_button.wait_for(timeout=timeout_config.get_element_timeout())
        await group_discount_button.click()

    async def wait_for_discount_detail_page(self) -> None:
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
        except Exception:
            self.logger.info("Group discount button still present after navigation, continuing")

    async def has_expired_toast(self) -> bool:
        toast = self.page.get_by_text(self.EXPIRED_TOAST_TEXT, exact=True)
        try:
            await toast.wait_for(timeout=1000)
            return await toast.is_visible()
        except Exception:
            return False
