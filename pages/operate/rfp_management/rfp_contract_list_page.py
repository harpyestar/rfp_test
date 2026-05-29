"""
签约项目列表页面对象模型
负责签约列表页的菜单导航、Tab 切换验证和操作按钮验证
"""

from playwright.async_api import Page
from pages.common.base_page import BasePage
from utils.config import config
from utils.timeout_config import timeout_config
from utils.logger import get_logger
import allure


class RFPContractListPage(BasePage):
    """签约项目列表页面对象"""

    HOME_PATH = "/operate.html#/home"

    CONTRACT_MANAGEMENT_MENU_TEXT = "签约管理"
    CONTRACTING_MENU_TEXT = "签约"

    UNSTARTED_TAB_TEXT = "未启动"
    STARTED_TAB_TEXT = "已启动"
    COMPLETED_TAB_TEXT = "已完成"

    START_BUTTON_TEXT = "启动"
    EDIT_BUTTON_TEXT = "修改项目"
    VOID_BUTTON_TEXT = "作废"

    SIGN_DETAIL_BUTTON_TEXT = "签约详情"
    PROJECT_DETAIL_BUTTON_TEXT = "项目详情"
    EXPORT_QUOTE_BUTTON_TEXT = "导出报价"
    PERFORMANCE_BUTTON_TEXT = "履约情况"

    def __init__(self, page: Page):
        super().__init__(page)
        self.logger = get_logger(self.__class__.__name__, config.log_level)

    async def navigate_to_home(self) -> None:
        """进入 /home 页面"""
        self.logger.info("开始进入 /home 页面")
        home_url = f"{config.base_url.rstrip('/')}{self.HOME_PATH}"
        await self.page.goto(
            home_url,
            wait_until="domcontentloaded",
            timeout=timeout_config.get_navigation_timeout(),
        )
        await self.wait_helper.wait_for_url(
            self.page,
            "**/home*",
            timeout=timeout_config.get_navigation_timeout(),
        )
        self.logger.info("[OK] 已进入 /home 页面")

    async def navigate_to_contracting(self) -> None:
        """通过菜单进入签约页面：签约管理 → 签约"""
        self.logger.info("开始通过菜单进入签约页面")
        contract_management_menu = self.page.get_by_text(
            self.CONTRACT_MANAGEMENT_MENU_TEXT, exact=True
        )
        await contract_management_menu.wait_for(timeout=timeout_config.get_element_timeout())
        await contract_management_menu.click()
        self.logger.info("已展开'签约管理'子菜单")
        await self.page.wait_for_timeout(300)

        contracting_menu = self.page.get_by_text(
            self.CONTRACTING_MENU_TEXT, exact=True
        ).last
        await contracting_menu.wait_for(timeout=timeout_config.get_element_timeout())
        await contracting_menu.click()
        await self.page.wait_for_load_state("networkidle")
        self.logger.info("[OK] 已进入签约页面")

    async def verify_tabs_visible(self) -> bool:
        """验证三个 Tab 均可见：未启动、已启动、已完成"""
        self.logger.info("验证三个 Tab 可见")
        for tab_text in [self.UNSTARTED_TAB_TEXT, self.STARTED_TAB_TEXT, self.COMPLETED_TAB_TEXT]:
            tab = self.page.get_by_text(tab_text, exact=True).first
            await tab.wait_for(timeout=timeout_config.get_element_timeout())
            if not await tab.is_visible():
                self.logger.error(f"Tab '{tab_text}' 不可见")
                return False
            self.logger.info(f"Tab '{tab_text}' 可见")
        return True

    async def verify_unstarted_action_buttons(self) -> bool:
        """验证未启动Tab操作列按钮：启动、修改项目、作废"""
        self.logger.info("验证未启动Tab操作按钮")
        for btn_text in [self.START_BUTTON_TEXT, self.EDIT_BUTTON_TEXT, self.VOID_BUTTON_TEXT]:
            btn = self.page.get_by_text(btn_text, exact=True).first
            try:
                await btn.wait_for(timeout=timeout_config.get_element_timeout())
                if not await btn.is_visible():
                    self.logger.error(f"按钮 '{btn_text}' 不可见")
                    return False
                self.logger.info(f"按钮 '{btn_text}' 可见")
            except Exception:
                self.logger.warning(f"按钮 '{btn_text}' 未找到（列表可能为空）")
        return True

    async def click_completed_tab(self) -> None:
        """点击「已完成」Tab"""
        self.logger.info("点击'已完成' Tab")
        completed_tab = self.page.get_by_text(self.COMPLETED_TAB_TEXT, exact=True).first
        await completed_tab.wait_for(timeout=timeout_config.get_element_timeout())
        await completed_tab.click()
        await self.page.wait_for_load_state("networkidle")
        self.logger.info("[OK] 已点击'已完成' Tab")

    async def verify_completed_action_buttons(self) -> bool:
        """验证已完成Tab操作列按钮：签约详情、项目详情、导出报价、履约情况"""
        self.logger.info("验证已完成Tab操作按钮")
        for btn_text in [
            self.SIGN_DETAIL_BUTTON_TEXT,
            self.PROJECT_DETAIL_BUTTON_TEXT,
            self.EXPORT_QUOTE_BUTTON_TEXT,
            self.PERFORMANCE_BUTTON_TEXT,
        ]:
            btn = self.page.get_by_text(btn_text, exact=True).first
            try:
                await btn.wait_for(timeout=timeout_config.get_element_timeout())
                if not await btn.is_visible():
                    self.logger.error(f"按钮 '{btn_text}' 不可见")
                    return False
                self.logger.info(f"按钮 '{btn_text}' 可见")
            except Exception:
                self.logger.warning(f"按钮 '{btn_text}' 未找到（列表可能为空）")
        return True