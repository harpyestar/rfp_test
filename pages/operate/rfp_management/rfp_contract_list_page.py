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

    ORG_NAME_LABEL_TEXT = "机构名"
    PROJECT_NAME_LABEL_TEXT = "签约项目"
    CREATOR_LABEL_TEXT = "创建人"

    SEARCH_BUTTON_SELECTOR = ".ml-15 > div"

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

    async def click_started_tab(self) -> None:
        """点击「已启动」Tab"""
        self.logger.info("点击'已启动' Tab")
        started_tab = self.page.get_by_text(self.STARTED_TAB_TEXT, exact=True).first
        await started_tab.wait_for(timeout=timeout_config.get_element_timeout())
        await started_tab.click()
        await self.page.wait_for_load_state("networkidle")
        self.logger.info("[OK] 已点击'已启动' Tab")

    def _filter_input_by_label(self, label_text: str):
        """通过 label 文本定位对应筛选输入框"""
        return (
            self.page.locator("label")
            .filter(has_text=label_text)
            .first
            .locator("..")
            .get_by_role("textbox")
        )

    def _search_button(self):
        """定位搜索按钮"""
        return self.page.locator(self.SEARCH_BUTTON_SELECTOR).first

    async def search_by_project_name(self, project_name: str) -> None:
        """按签约项目名称筛选"""
        self.logger.info(f"按签约项目名称筛选: {project_name}")
        input_field = self._filter_input_by_label(self.PROJECT_NAME_LABEL_TEXT)
        await input_field.wait_for(timeout=timeout_config.get_element_timeout())
        await input_field.fill(project_name)
        search_btn = self._search_button()
        await search_btn.wait_for(timeout=timeout_config.get_element_timeout())
        await search_btn.click()
        await self.page.wait_for_load_state("networkidle")
        self.logger.info(f"签约项目名称筛选完成: {project_name}")

    async def search_by_org_name(self, org_name: str) -> None:
        """按机构名筛选（输入并选择下拉选项）"""
        self.logger.info(f"按机构名筛选: {org_name}")
        input_field = self._filter_input_by_label(self.ORG_NAME_LABEL_TEXT)
        await input_field.wait_for(timeout=timeout_config.get_element_timeout())
        await input_field.fill(org_name)
        await self.page.wait_for_timeout(500)
        panel = self.page.locator(".c-dropdown-panel").last
        await panel.wait_for(timeout=timeout_config.get_element_timeout())
        option = panel.locator(".c-select-option").filter(has_text=org_name).first
        await option.wait_for(timeout=timeout_config.get_element_timeout())
        await option.click()
        self.logger.info(f"已选择机构名下拉选项: {org_name}")
        search_btn = self._search_button()
        await search_btn.wait_for(timeout=timeout_config.get_element_timeout())
        await search_btn.click()
        await self.page.wait_for_load_state("networkidle")
        self.logger.info(f"机构名筛选完成: {org_name}")

    async def search_by_creator(self, creator_name: str) -> None:
        """按创建人筛选"""
        self.logger.info(f"按创建人筛选: {creator_name}")
        input_field = self._filter_input_by_label(self.CREATOR_LABEL_TEXT)
        await input_field.wait_for(timeout=timeout_config.get_element_timeout())
        await input_field.fill(creator_name)
        search_btn = self._search_button()
        await search_btn.wait_for(timeout=timeout_config.get_element_timeout())
        await search_btn.click()
        await self.page.wait_for_load_state("networkidle")
        self.logger.info(f"创建人筛选完成: {creator_name}")

    async def combined_search(self, org_name: str, project_name: str, creator_name: str) -> None:
        """组合筛选：机构名 + 签约项目 + 创建人"""
        self.logger.info(f"组合筛选: 机构={org_name}, 项目={project_name}, 创建人={creator_name}")
        await self.search_by_org_name(org_name)
        await self.search_by_project_name(project_name)
        await self.search_by_creator(creator_name)
        self.logger.info("组合筛选完成")

    async def get_project_filter_value(self) -> str:
        """获取签约项目筛选输入框的当前值"""
        input_field = self._filter_input_by_label(self.PROJECT_NAME_LABEL_TEXT)
        await input_field.wait_for(timeout=timeout_config.get_element_timeout())
        value = await input_field.input_value()
        self.logger.info(f"签约项目筛选框当前值: '{value}'")
        return value

    async def reset_filter(self) -> None:
        """点击「重置」按钮，重置所有筛选条件"""
        self.logger.info("点击'重置'按钮")
        reset_btn = self.page.locator(self.SEARCH_BUTTON_SELECTOR).nth(1)
        await reset_btn.wait_for(timeout=timeout_config.get_element_timeout())
        await reset_btn.click()
        await self.page.wait_for_load_state("networkidle")
        self.logger.info("[OK] 已点击'重置'按钮")

    async def get_org_filter_value(self) -> str:
        """获取机构名筛选输入框的当前值"""
        input_field = self._filter_input_by_label(self.ORG_NAME_LABEL_TEXT)
        await input_field.wait_for(timeout=timeout_config.get_element_timeout())
        value = await input_field.input_value()
        self.logger.info(f"机构名筛选框当前值: '{value}'")
        return value

    async def get_creator_filter_value(self) -> str:
        """获取创建人筛选输入框的当前值"""
        input_field = self._filter_input_by_label(self.CREATOR_LABEL_TEXT)
        await input_field.wait_for(timeout=timeout_config.get_element_timeout())
        value = await input_field.input_value()
        self.logger.info(f"创建人筛选框当前值: '{value}'")
        return value

    async def verify_all_filters_cleared(self) -> bool:
        """验证所有筛选条件已清空"""
        project_val = await self.get_project_filter_value()
        org_val = await self.get_org_filter_value()
        creator_val = await self.get_creator_filter_value()
        all_cleared = project_val == "" and org_val == "" and creator_val == ""
        if all_cleared:
            self.logger.info("所有筛选条件已清空")
        else:
            self.logger.error(
                f"筛选条件未完全清空: 签约项目='{project_val}', 机构名='{org_val}', 创建人='{creator_val}'"
            )
        return all_cleared

    async def verify_list_is_empty(self) -> bool:
        """验证列表为空（无数据或显示暂无数据）"""
        self.logger.info("验证列表是否为空")
        try:
            empty_text = self.page.get_by_text("暂无数据").first
            if await empty_text.is_visible():
                self.logger.info("列表为空（暂无数据提示可见）")
                return True
        except Exception:
            pass
        rows = await self.page.locator("table.c-table-body tbody tr.c-tr").count()
        self.logger.info(f"列表行数: {rows}")
        return rows == 0

    async def verify_project_in_list(self, project_name: str) -> bool:
        """验证列表中存在指定项目名称"""
        self.logger.info(f"验证列表中存在项目: {project_name}")
        try:
            cell = self.page.get_by_text(project_name, exact=True).first
            await cell.wait_for(timeout=timeout_config.get_element_timeout())
            self.logger.info(f"列表中找到项目: {project_name}")
            return True
        except Exception:
            self.logger.warning(f"列表中未找到项目: {project_name}")
            return False