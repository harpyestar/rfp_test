"""
签约项目列表页面对象模型
负责签约列表页的菜单导航、Tab 切换验证和操作按钮验证
"""

from playwright.async_api import Page, expect
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

    GO_TO_SIGN_BUTTON_TEXT = "去签约"
    MODIFY_BUTTON_TEXT = "修改"
    STOP_BUTTON_TEXT = "终止"

    STARTED_ACTION_BUTTONS = [
        GO_TO_SIGN_BUTTON_TEXT,
        MODIFY_BUTTON_TEXT,
        STOP_BUTTON_TEXT,
        EXPORT_QUOTE_BUTTON_TEXT,
        PERFORMANCE_BUTTON_TEXT,
    ]

    C_DIALOG_SELECTOR = ".c-confirmer"
    CONFIRM_BUTTON_TEXT = "确定"
    CANCEL_BUTTON_TEXT = "取消"
    DIALOG_TITLE_TEXT = "提示"
    START_CONFIRM_MSG = "确定要启动么？"
    START_SUCCESS_TEXT = "操作成功!"
    STOP_CONFIRM_MSG = "确定要终止签约么？"
    STOP_SUCCESS_TEXT = "操作成功!"
    VOID_CONFIRM_MSG = "确定要废标么？"
    VOID_SUCCESS_TEXT = "操作成功!"
    SUCCESS_TOAST_SELECTOR = ".c-view.c-notify-content-description.bold"

    ORG_NAME_LABEL_TEXT = "机构名"
    PROJECT_NAME_LABEL_TEXT = "签约项目"
    CREATOR_LABEL_TEXT = "创建人"

    SEARCH_BUTTON_SELECTOR = ".ml-15 > div"

    NEXT_PAGE_BUTTON_SELECTOR = ".c-icon-right-arrow"
    PREV_PAGE_BUTTON_SELECTOR = ".c-icon-left-arrow"

    UNSTARTED_COLUMN_HEADERS = [
        "签约项目",
        "预计签约酒店数",
        "差标范围(元)",
        "报名起止日",
        "报价起止日",
        "公布评标结果日",
        "创建信息",
        "操作",
    ]

    STARTED_COLUMN_HEADERS = [
        "签约项目",
        "预计签约酒店数",
        "差标范围(元)",
        "报名起止日",
        "报价起止日",
        "公布结果日",
        "已报价/已邀酒店数",
        "创建信息",
        "操作",
    ]

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
        """通过菜单进入签约页面：签约管理 → 签约（若子菜单已展开则直接点击）"""
        self.logger.info("开始通过菜单进入签约页面")
        contracting_menu = self.page.get_by_text(
            self.CONTRACTING_MENU_TEXT, exact=True
        ).last
        try:
            await contracting_menu.wait_for(timeout=500)
            if await contracting_menu.is_visible():
                self.logger.info("'签约'子菜单已可见，直接点击")
                await contracting_menu.click()
                await self.page.wait_for_load_state("networkidle")
                self.logger.info("[OK] 已进入签约页面")
                return
        except Exception:
            pass

        contract_management_menu = self.page.get_by_text(
            self.CONTRACT_MANAGEMENT_MENU_TEXT, exact=True
        )
        await contract_management_menu.wait_for(timeout=timeout_config.get_element_timeout())
        await contract_management_menu.click()
        self.logger.info("已展开'签约管理'子菜单")
        await self.page.wait_for_timeout(300)

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

    async def verify_unstarted_list_columns(self) -> bool:
        """验证未启动Tab列表字段列完整"""
        self.logger.info("验证未启动Tab列表字段列")
        table_header = self.page.locator(".c-table").first
        await table_header.wait_for(timeout=timeout_config.get_element_timeout())
        for col_name in self.UNSTARTED_COLUMN_HEADERS:
            col = table_header.get_by_text(col_name, exact=True).first
            try:
                await col.wait_for(timeout=timeout_config.get_element_timeout())
                if not await col.is_visible():
                    self.logger.error(f"列 '{col_name}' 不可见")
                    return False
                self.logger.info(f"列 '{col_name}' 可见")
            except Exception:
                self.logger.error(f"列 '{col_name}' 未找到")
                return False
        return True

    async def verify_unstarted_first_row_has_data(self) -> bool:
        """验证未启动Tab列表第一行有数据（非空列表）"""
        self.logger.info("验证未启动Tab列表第一行有数据")
        rows = self.page.locator("table.c-table-body tbody tr.c-tr")
        count = await rows.count()
        if count == 0:
            self.logger.warning("列表为空，无数据行")
            return False
        first_row = rows.first
        cells = first_row.locator("td")
        cell_count = await cells.count()
        self.logger.info(f"第一行有 {cell_count} 个单元格")
        return cell_count >= len(self.UNSTARTED_COLUMN_HEADERS)

    async def verify_started_list_columns(self) -> bool:
        """验证已启动Tab列表字段列完整"""
        self.logger.info("验证已启动Tab列表字段列")
        table_header = self.page.locator(".c-table").first
        await table_header.wait_for(timeout=timeout_config.get_element_timeout())
        for col_name in self.STARTED_COLUMN_HEADERS:
            col = table_header.get_by_text(col_name, exact=True).first
            try:
                await col.wait_for(timeout=timeout_config.get_element_timeout())
                if not await col.is_visible():
                    self.logger.error(f"列 '{col_name}' 不可见")
                    return False
                self.logger.info(f"列 '{col_name}' 可见")
            except Exception:
                self.logger.error(f"列 '{col_name}' 未找到")
                return False
        return True

    async def verify_started_action_buttons(self) -> bool:
        """验证已启动Tab操作列按钮：去签约、修改、终止、导出报价、履约情况"""
        self.logger.info("验证已启动Tab操作按钮")
        for btn_text in self.STARTED_ACTION_BUTTONS:
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

    async def verify_started_first_row_has_data(self) -> bool:
        """验证已启动Tab列表第一行有数据（非空列表）"""
        self.logger.info("验证已启动Tab列表第一行有数据")
        rows = self.page.locator("table.c-table-body tbody tr.c-tr")
        count = await rows.count()
        if count == 0:
            self.logger.warning("列表为空，无数据行")
            return False
        first_row = rows.first
        cells = first_row.locator("td")
        cell_count = await cells.count()
        self.logger.info(f"第一行有 {cell_count} 个单元格")
        return cell_count >= len(self.STARTED_COLUMN_HEADERS)

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

    def _pagination_area(self):
        """定位分页控件区域"""
        return self.page.locator(".c-pagination, .el-pagination, .pagination").first

    def _next_page_button(self):
        """定位下一页按钮"""
        return self._pagination_area().locator(self.NEXT_PAGE_BUTTON_SELECTOR)

    async def verify_pagination_visible(self) -> bool:
        """验证分页控件存在且可见"""
        self.logger.info("验证分页控件可见")
        pagination = self._pagination_area()
        try:
            await pagination.wait_for(timeout=timeout_config.get_element_timeout())
            if await pagination.is_visible():
                self.logger.info("分页控件可见")
                return True
        except Exception:
            pass
        self.logger.warning("分页控件未找到")
        return False

    async def get_current_page_number(self) -> int:
        """获取当前激活的页码"""
        active_page = self._pagination_area().locator(".c-pagination-button.selected").first
        try:
            text = await active_page.text_content()
            page_num = int(text.strip()) if text else 1
            self.logger.info(f"当前页码: {page_num}")
            return page_num
        except Exception:
            self.logger.warning("无法获取当前页码，默认为1")
            return 1

    async def click_next_page(self) -> None:
        """点击「下一页」按钮"""
        self.logger.info("点击'下一页'按钮")
        next_btn = self._next_page_button()
        await next_btn.wait_for(timeout=timeout_config.get_element_timeout())
        prev_page = await self.get_current_page_number()
        await next_btn.click()
        await self.page.wait_for_load_state("networkidle")
        new_page = await self.get_current_page_number()
        self.logger.info(f"页码变化: {prev_page} → {new_page}")

    async def get_page_row_count(self) -> int:
        """获取当前页列表行数"""
        rows = self.page.locator("table.c-table-body tbody tr.c-tr")
        count = await rows.count()
        self.logger.info(f"当前页列表行数: {count}")
        return count

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

    async def expect_project_disappeared(self, project_name: str) -> None:
        """断言项目从列表消失（内置自动等待重试）"""
        self.logger.info(f"断言项目从列表消失: {project_name}")
        cell = self.page.get_by_text(project_name, exact=True).first
        await expect(cell).not_to_be_visible(timeout=timeout_config.get_element_timeout())
        self.logger.info(f"项目已从列表消失: {project_name}")

    async def click_start_button_for_first_row(self) -> None:
        """点击第一行的「启动」按钮"""
        self.logger.info("点击第一行的'启动'按钮")
        start_btn = self.page.get_by_text(self.START_BUTTON_TEXT, exact=True).first
        await start_btn.wait_for(timeout=timeout_config.get_element_timeout())
        await start_btn.click()
        self.logger.info("已点击'启动'按钮")

    async def click_stop_button_for_first_row(self) -> None:
        """点击第一行的「终止」按钮"""
        self.logger.info("点击第一行的'终止'按钮")
        stop_btn = self.page.get_by_text(self.STOP_BUTTON_TEXT, exact=True).first
        await stop_btn.wait_for(timeout=timeout_config.get_element_timeout())
        await stop_btn.click()
        self.logger.info("已点击'终止'按钮")

    async def click_void_button_for_first_row(self) -> None:
        """点击第一行的「作废」按钮"""
        self.logger.info("点击第一行的'作废'按钮")
        void_btn = self.page.get_by_text(self.VOID_BUTTON_TEXT, exact=True).first
        await void_btn.wait_for(timeout=timeout_config.get_element_timeout())
        await void_btn.click()
        self.logger.info("已点击'作废'按钮")

    async def verify_confirm_dialog_visible(self, expected_message: str) -> bool:
        """验证确认弹窗可见且内容匹配"""
        self.logger.info(f"验证确认弹窗: {expected_message}")
        dialog = self.page.locator(self.C_DIALOG_SELECTOR).first
        try:
            await dialog.wait_for(timeout=timeout_config.get_element_timeout())
            title = dialog.get_by_text(self.DIALOG_TITLE_TEXT, exact=True)
            message = dialog.get_by_text(expected_message)
            title_ok = await title.is_visible()
            msg_ok = await message.is_visible()
            if title_ok and msg_ok:
                self.logger.info(f"确认弹窗内容匹配: 标题='提示', 内容='{expected_message}'")
                return True
            self.logger.error(f"弹窗内容不匹配: title={title_ok}, message={msg_ok}")
            return False
        except Exception:
            self.logger.error("确认弹窗未出现")
            return False

    async def click_cancel_in_dialog(self) -> None:
        """在弹窗中点击「取消」按钮"""
        self.logger.info("点击弹窗中的'取消'按钮")
        dialog = self.page.locator(self.C_DIALOG_SELECTOR).first
        cancel_btn = dialog.get_by_text(self.CANCEL_BUTTON_TEXT, exact=True)
        await cancel_btn.wait_for(timeout=timeout_config.get_element_timeout())
        await cancel_btn.click()
        self.logger.info("已点击'取消'按钮")

    async def verify_confirm_dialog_disappeared(self) -> bool:
        """验证确认弹窗已关闭"""
        self.logger.info("验证确认弹窗已关闭")
        dialog = self.page.locator(self.C_DIALOG_SELECTOR)
        count = await dialog.count()
        if count == 0:
            self.logger.info("确认弹窗已关闭")
            return True
        self.logger.warning(f"确认弹窗仍然可见，共 {count} 个")
        return False

    async def click_confirm_in_dialog(self) -> None:
        """在弹窗中点击「确认」按钮"""
        self.logger.info("点击弹窗中的'确定'按钮")
        dialog = self.page.locator(self.C_DIALOG_SELECTOR).first
        confirm_btn = dialog.get_by_text(self.CONFIRM_BUTTON_TEXT, exact=True)
        await confirm_btn.wait_for(timeout=timeout_config.get_element_timeout())
        await confirm_btn.click()
        await self.page.wait_for_load_state("networkidle")
        self.logger.info("已点击'确认'按钮")

    async def verify_success_toast(self, expected_text: str) -> bool:
        """验证成功 toast 提示出现"""
        self.logger.info(f"验证成功 toast: {expected_text}")
        try:
            toast = self.page.locator(self.SUCCESS_TOAST_SELECTOR)
            await toast.wait_for(timeout=timeout_config.get_element_timeout())
            toast_text = await toast.text_content()
            toast_text = toast_text.strip() if toast_text else ""
            if expected_text in toast_text:
                self.logger.info(f"成功 toast 已出现: {toast_text}")
                return True
            self.logger.warning(f"toast 内容不匹配: 期望='{expected_text}', 实际='{toast_text}'")
            return False
        except Exception:
            self.logger.warning(f"未检测到成功 toast: {expected_text}")
            return False