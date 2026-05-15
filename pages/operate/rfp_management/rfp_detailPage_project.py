"""
RFP 报价详情页面对象模型
负责签约列表进入报价详情页，并维护内部跟进备注
"""

from playwright.async_api import Page
from pages.common.base_page import BasePage
from utils.config import config
from utils.timeout_config import timeout_config
from utils.logger import get_logger
import allure
import re


class RFPDetailPageProject(BasePage):
    """RFP 报价详情页面对象"""

    HOME_PATH = "/operate.html#/home"

    CONTRACT_MANAGEMENT_MENU_TEXT = "签约管理"
    CONTRACTING_MENU_TEXT = "签约"

    STARTED_TAB_PATTERN = r"^已启动$"
    AWARDED_TAB_PATTERN = r"^已中签$"

    PROJECT_SEARCH_LABEL_TEXT = "签约项目"
    SEARCH_BUTTON_SELECTOR = ".ml-15 > div"
    GO_CONTRACTING_BUTTON_TEXT = "去签约"

    HOTEL_LIST_SELECTOR = ".hotel-list .item"
    VIEW_BID_DETAIL_BUTTON_TEXT = "查看报价详情"

    INTERNAL_REMARK_BUTTON_TEXT = "内部备注"
    INTERNAL_REMARK_INPUT_PLACEHOLDER = "请输入内部跟进备注"
    CONFIRM_BUTTON_TEXT = "确定"

    EXPAND_BUTTON_TEXT = "展开 ▼"
    COLLAPSE_BUTTON_TEXT = "收起 ▲"

    # ========== 价格状态变更操作 ==========
    CONTINUE_NEGOTIATION_BUTTON_TEXT = "继续议价"
    SIGNED_BUTTON_TEXT = "确认中签"
    REJECTED_BUTTON_TEXT = "否决报价"
    MESSAGE_BOARD_SELECTOR = "//div[@class='w-100p c-asm']//textarea"
    CONFIRM_ACTION_BUTTON_SELECTOR = "div.c-asm.c-button.bg-white.flex-center.size-sm.color-primary.r-sm"

    def __init__(self, page: Page):
        super().__init__(page)
        self.logger = get_logger(self.__class__.__name__, config.log_level)

    async def navigate_to_home(self) -> None:
        """进入 /home 页面"""
        self.logger.info("开始进入 /home 页面")

        with allure.step("进入 /home 页面"):
            try:
                home_url = f"{config.base_url.rstrip('/')}{self.HOME_PATH}"
                await self.page.goto(home_url, wait_until="domcontentloaded")
                await self.wait_helper.wait_for_url(
                    self.page,
                    "**/home*",
                    timeout=timeout_config.get_navigation_timeout(),
                )
                self.logger.info("[OK] 已进入 /home 页面")
            except Exception as e:
                error_msg = f"进入 /home 页面失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "导航错误")
                raise

    async def navigate_to_contracting(self) -> None:
        """通过菜单进入签约页面"""
        self.logger.info("开始进入签约页面")

        with allure.step("通过菜单进入签约页面"):
            try:
                contract_management_menu = self.page.get_by_text(
                    self.CONTRACT_MANAGEMENT_MENU_TEXT,
                    exact=True,
                )
                await contract_management_menu.wait_for(timeout=timeout_config.get_element_timeout())
                await contract_management_menu.click()
                await self.page.wait_for_timeout(300)

                contracting_menu = self.page.get_by_text(
                    self.CONTRACTING_MENU_TEXT,
                    exact=True,
                ).last
                await contracting_menu.wait_for(timeout=timeout_config.get_element_timeout())
                await contracting_menu.click()
                await self.page.wait_for_load_state("networkidle")
                self.logger.info("[OK] 已进入签约页面")
            except Exception as e:
                error_msg = f"进入签约页面失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "导航错误")
                raise

    async def click_started_tab(self) -> None:
        """点击已启动 Tab"""
        self.logger.info("开始点击已启动 Tab")

        with allure.step("点击已启动 Tab"):
            try:
                started_tab = self.page.locator("div").filter(
                    has_text=re.compile(self.STARTED_TAB_PATTERN)
                ).first
                await started_tab.wait_for(timeout=timeout_config.get_element_timeout())
                await started_tab.click()
                await self.page.wait_for_timeout(300)
                self.logger.info("[OK] 已点击已启动 Tab")
            except Exception as e:
                error_msg = f"点击已启动 Tab 失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "Tab 错误")
                raise

    async def search_project(self, project_name: str) -> None:
        """搜索签约项目"""
        self.logger.info(f"开始搜索项目: {project_name}")

        with allure.step(f"搜索项目: {project_name}"):
            try:
                project_filter = self.page.locator("label").filter(
                    has_text=self.PROJECT_SEARCH_LABEL_TEXT
                ).first
                await project_filter.wait_for(timeout=timeout_config.get_element_timeout())
                await project_filter.click()

                project_input = self.page.get_by_label(self.PROJECT_SEARCH_LABEL_TEXT)
                await project_input.wait_for(timeout=timeout_config.get_element_timeout())
                await project_input.fill(project_name)
                await self.page.wait_for_timeout(200)

                search_button = self.page.locator(self.SEARCH_BUTTON_SELECTOR).first
                await search_button.wait_for(timeout=timeout_config.get_element_timeout())
                await search_button.click()
                await self.page.wait_for_load_state("networkidle")
                self.logger.info(f"[OK] 项目搜索完成: {project_name}")
            except Exception as e:
                error_msg = f"搜索项目失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "搜索错误")
                raise

    async def click_first_go_contracting_button(self) -> None:
        """点击首个去签约按钮"""
        self.logger.info("开始点击首个去签约按钮")

        with allure.step("点击首个去签约按钮"):
            try:
                go_contracting_button = self.page.get_by_text(
                    self.GO_CONTRACTING_BUTTON_TEXT,
                    exact=True,
                ).first
                await go_contracting_button.wait_for(timeout=timeout_config.get_element_timeout())
                await go_contracting_button.click()
                await self.page.wait_for_timeout(500)
                self.logger.info("[OK] 已点击首个去签约按钮")
            except Exception as e:
                error_msg = f"点击去签约按钮失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "按钮错误")
                raise

    async def click_awarded_tab(self) -> None:
        """点击已中签 Tab"""
        self.logger.info("开始点击已中签 Tab")

        with allure.step("点击已中签 Tab"):
            try:
                awarded_tab = self.page.locator("span.name").filter(
                    has_text=re.compile(self.AWARDED_TAB_PATTERN)
                ).first
                await awarded_tab.wait_for(timeout=timeout_config.get_element_timeout())
                await awarded_tab.click()
                await self.page.wait_for_timeout(300)
                self.logger.info("[OK] 已点击已中签 Tab")
            except Exception as e:
                error_msg = f"点击已中签 Tab 失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "Tab 错误")
                raise

    async def select_first_awarded_hotel(self) -> None:
        """选择已中签列表中的首个酒店"""
        self.logger.info("开始选择首个已中签酒店")

        with allure.step("选择首个已中签酒店"):
            try:
                first_hotel = self.page.locator(self.HOTEL_LIST_SELECTOR).first
                await first_hotel.wait_for(timeout=timeout_config.get_element_timeout())
                await first_hotel.click()
                await self.page.wait_for_timeout(300)
                self.logger.info("[OK] 已选择首个已中签酒店")
            except Exception as e:
                error_msg = f"选择首个已中签酒店失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "酒店选择错误")
                raise

    async def open_first_bid_detail_popup(self) -> Page:
        """打开首个报价详情新标签页"""
        self.logger.info("开始打开报价详情新标签页")

        with allure.step("打开报价详情新标签页"):
            try:
                bid_detail_button = self.page.get_by_text(
                    self.VIEW_BID_DETAIL_BUTTON_TEXT,
                    exact=True,
                ).first
                await bid_detail_button.wait_for(timeout=timeout_config.get_element_timeout())

                async with self.page.expect_popup() as popup_info:
                    await bid_detail_button.click()

                detail_page = await popup_info.value
                await detail_page.wait_for_load_state("domcontentloaded")
                self.logger.info("[OK] 报价详情新标签页已打开")
                return detail_page
            except Exception as e:
                error_msg = f"打开报价详情新标签页失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "详情页错误")
                raise

    async def verify_internal_remark_button_visible(self) -> bool:
        """验证内部备注按钮是否可见"""
        self.logger.info("开始验证内部备注按钮是否可见")

        try:
            internal_remark_button = self.page.get_by_text(
                self.INTERNAL_REMARK_BUTTON_TEXT,
                exact=True,
            ).first
            await internal_remark_button.wait_for(timeout=timeout_config.get_element_timeout())
            is_visible = await internal_remark_button.is_visible()
            self.logger.info(f"内部备注按钮可见: {is_visible}")
            return is_visible
        except Exception as e:
            self.logger.error(f"验证内部备注按钮失败: {str(e)}")
            return False

    async def click_internal_remark_button(self) -> None:
        """点击内部备注按钮"""
        self.logger.info("开始点击内部备注按钮")

        with allure.step("点击内部备注按钮"):
            try:
                internal_remark_button = self.page.get_by_text(
                    self.INTERNAL_REMARK_BUTTON_TEXT,
                    exact=True,
                ).first
                await internal_remark_button.wait_for(timeout=timeout_config.get_element_timeout())
                await internal_remark_button.click()
                await self.page.wait_for_timeout(300)
                self.logger.info("[OK] 已点击内部备注按钮")
            except Exception as e:
                error_msg = f"点击内部备注按钮失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "备注按钮错误")
                raise

    async def add_internal_remark(self, remark_content: str) -> None:
        """填写并提交内部备注"""
        self.logger.info(f"开始填写内部备注: {remark_content}")

        with allure.step(f"填写内部备注: {remark_content}"):
            try:
                internal_remark_input = self.page.get_by_placeholder(
                    self.INTERNAL_REMARK_INPUT_PLACEHOLDER
                )
                await internal_remark_input.wait_for(timeout=timeout_config.get_element_timeout())
                await internal_remark_input.click()
                await internal_remark_input.fill(remark_content)

                confirm_button = self.page.get_by_role(
                    "button",
                    name=self.CONFIRM_BUTTON_TEXT,
                ).last
                await confirm_button.wait_for(timeout=timeout_config.get_element_timeout())
                await confirm_button.click()
                await self.page.wait_for_timeout(500)
                self.logger.info("[OK] 内部备注已提交")
            except Exception as e:
                error_msg = f"填写内部备注失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "备注错误")
                raise

    async def verify_expand_button_visible(self) -> bool:
        """验证备注展开按钮是否可见"""
        self.logger.info("开始验证备注展开按钮是否可见")

        try:
            expand_button = self.page.get_by_text(
                self.EXPAND_BUTTON_TEXT,
                exact=True,
            ).first
            await expand_button.wait_for(timeout=timeout_config.get_element_timeout())
            is_visible = await expand_button.is_visible()
            self.logger.info(f"备注展开按钮可见: {is_visible}")
            return is_visible
        except Exception as e:
            self.logger.error(f"验证备注展开按钮失败: {str(e)}")
            return False

    async def click_expand_button(self) -> None:
        """点击备注展开按钮"""
        self.logger.info("开始点击备注展开按钮")

        with allure.step("点击备注展开按钮"):
            try:
                expand_button = self.page.get_by_text(
                    self.EXPAND_BUTTON_TEXT,
                    exact=True,
                ).first
                await expand_button.wait_for(timeout=timeout_config.get_element_timeout())
                await expand_button.click()
                await self.page.wait_for_timeout(300)
                self.logger.info("[OK] 已点击备注展开按钮")
            except Exception as e:
                error_msg = f"点击备注展开按钮失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "展开按钮错误")
                raise

    async def verify_collapse_button_visible(self) -> bool:
        """验证备注收起按钮是否可见"""
        self.logger.info("开始验证备注收起按钮是否可见")

        try:
            collapse_button = self.page.get_by_text(
                self.COLLAPSE_BUTTON_TEXT,
                exact=True,
            ).first
            await collapse_button.wait_for(timeout=timeout_config.get_element_timeout())
            is_visible = await collapse_button.is_visible()
            self.logger.info(f"备注收起按钮可见: {is_visible}")
            return is_visible
        except Exception as e:
            self.logger.error(f"验证备注收起按钮失败: {str(e)}")
            return False

    async def click_collapse_button(self) -> None:
        """点击备注收起按钮"""
        self.logger.info("开始点击备注收起按钮")

        with allure.step("点击备注收起按钮"):
            try:
                collapse_button = self.page.get_by_text(
                    self.COLLAPSE_BUTTON_TEXT,
                    exact=True,
                ).first
                await collapse_button.wait_for(timeout=timeout_config.get_element_timeout())
                await collapse_button.click()
                await self.page.wait_for_timeout(300)
                self.logger.info("[OK] 已点击备注收起按钮")
            except Exception as e:
                error_msg = f"点击备注收起按钮失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "收起按钮错误")
                raise

    # ======================================================================
    # 价格状态变更操作
    # ======================================================================

    async def _click_action_text_button(self, button_text: str) -> None:
        """点击指定文本的操作按钮（继续议价/中签/否决）"""
        self.logger.info(f"点击操作按钮: {button_text}")

        with allure.step(f"点击操作按钮: {button_text}"):
            try:
                action_btn = self.page.get_by_text(button_text, exact=True).first
                await action_btn.wait_for(timeout=timeout_config.get_element_timeout())
                await action_btn.click()
                await self.page.wait_for_timeout(300)
                self.logger.info(f"[OK] 已点击操作按钮: {button_text}")
            except Exception as e:
                error_msg = f"点击操作按钮 [{button_text}] 失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "操作按钮错误")
                raise

    async def click_action_by_type(self, action: str) -> None:
        """根据动作类型点击对应的操作按钮

        Args:
            action: 操作类型，"继续议价" / "中签" / "否决"
        """
        action_text_map = {
            "继续议价": self.CONTINUE_NEGOTIATION_BUTTON_TEXT,
            "中签": self.SIGNED_BUTTON_TEXT,
            "否决": self.REJECTED_BUTTON_TEXT,
        }
        btn_text = action_text_map.get(action)
        if btn_text is None:
            raise ValueError(f"不支持的操作类型: {action}")
        await self._click_action_text_button(btn_text)

    async def fill_action_message(self, message: str) -> None:
        """在留言板输入内容"""
        self.logger.info(f"输入留言: {message}")

        with allure.step(f"输入留言: {message}"):
            try:
                msg_input = self.page.locator(self.MESSAGE_BOARD_SELECTOR)
                await msg_input.wait_for(timeout=timeout_config.get_element_timeout())
                await msg_input.click()
                await msg_input.fill(message)
                await self.page.wait_for_timeout(200)
                self.logger.info("[OK] 留言已输入")
            except Exception as e:
                error_msg = f"输入留言失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "留言输入错误")
                raise

    async def click_action_confirm(self) -> None:
        """点击操作确认对话框中的确定按钮"""
        self.logger.info("点击确定按钮")

        with allure.step("点击确定按钮"):
            try:
                confirm_btn = self.page.locator(
                    self.CONFIRM_ACTION_BUTTON_SELECTOR
                )
                await confirm_btn.wait_for(timeout=timeout_config.get_element_timeout())
                await confirm_btn.click()
                await self.page.wait_for_timeout(500)
                self.logger.info("[OK] 已点击确定按钮")
            except Exception as e:
                error_msg = f"点击确定按钮失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "确定按钮错误")
                raise

    async def refresh_detail_page(self) -> None:
        """刷新报价详情页"""
        self.logger.info("开始刷新报价详情页")

        with allure.step("刷新报价详情页"):
            try:
                await self.page.reload(wait_until="domcontentloaded")
                await self.page.wait_for_timeout(500)
                self.logger.info("[OK] 报价详情页已刷新")
            except Exception as e:
                error_msg = f"刷新报价详情页失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "刷新错误")
                raise

    async def has_internal_remark(self, remark_content: str) -> bool:
        """验证页面是否展示指定内部备注"""
        self.logger.info(f"开始验证内部备注内容是否展示: {remark_content}")

        try:
            internal_remark_text = self.page.get_by_text(remark_content).first
            await internal_remark_text.wait_for(timeout=timeout_config.get_element_timeout())
            is_visible = await internal_remark_text.is_visible()
            self.logger.info(f"内部备注内容可见: {is_visible}")
            return is_visible
        except Exception as e:
            self.logger.error(f"验证内部备注内容失败: {str(e)}")
            return False
