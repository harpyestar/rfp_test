"""
RFP 签约地图/列表页面对象模型
负责去签约后的价格状态变更操作：导入签约状态、切换价格页签、执行议价/中签/否决等
"""

from playwright.async_api import Page
from pages.common.base_page import BasePage
from utils.config import config
from utils.timeout_config import timeout_config
from utils.logger import get_logger
import allure
import re


class RFPContractMapPage(BasePage):
    """RFP 签约地图/列表页面对象 - 价格状态变更操作"""

    # ========== 导航菜单 ==========
    HOME_PATH = "/operate.html#/home"
    CONTRACT_MANAGEMENT_MENU_TEXT = "签约管理"
    CONTRACTING_MENU_TEXT = "签约"

    # ========== Tab ==========
    STARTED_TAB_PATTERN = r"^已启动$"

    # ========== 搜索 ==========
    PROJECT_SEARCH_LABEL_TEXT = "签约项目"
    SEARCH_BUTTON_SELECTOR = ".ml-15 > div"
    GO_CONTRACTING_BUTTON_TEXT = "去签约"

    # ========== 视图模式切换 ==========
    VIEW_MODE_DROPDOWN_SELECTOR = "//div[@class='c-popper c-dropdown ml-10']"
    LIST_MODE_OPTION_SELECTOR = "//div[@class='c-popper c-dropdown ml-10']//div[@title='列表模式']"
    MAP_MODE_OPTION_SELECTOR = "//div[@class='c-popper c-dropdown ml-10']//div[@title='地图模式']"

    # ========== 导入签约状态 ==========
    IMPORT_STATUS_FILE_SELECTOR = (
        "//div[text()='导入签约状态']/../../preceding-sibling::input[@type='file']"
    )

    # ========== 价格状态页签 ==========
    PRICE_TAB_XPATH_FORMAT = "//div[@class='tab-wrap']//span[text()='{}']"

    # ========== 酒店列表 ==========
    HOTEL_LIST_ITEM_SELECTOR = (
        "//div[@id='contentList']//div[contains(@class, 'border-bottom')]"
    )

    # ========== 操作按钮 ==========
    CONTINUE_NEGOTIATION_BUTTON_TEXT = "继续议价"
    SIGNED_BUTTON_TEXT = "中签"
    REJECTED_BUTTON_TEXT = "否决"

    # ========== 留言板 ==========
    MESSAGE_BOARD_SELECTOR = "//div[@class='w-100p c-asm']//textarea"

    # ========== 通用按钮 ==========
    CONFIRM_BUTTON_TEXT = "确定"

    # ========== URL 验证关键字 ==========
    BID_EVALUATION_KEYWORD = "bidEvaluationDetails"

    def __init__(self, page: Page):
        super().__init__(page)
        self.logger = get_logger(self.__class__.__name__, config.log_level)

    # ======================================================================
    # 导航
    # ======================================================================

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
                    self.CONTRACT_MANAGEMENT_MENU_TEXT, exact=True
                )
                await contract_management_menu.wait_for(
                    timeout=timeout_config.get_element_timeout()
                )
                await contract_management_menu.click()
                await self.page.wait_for_timeout(300)

                contracting_menu = self.page.get_by_text(
                    self.CONTRACTING_MENU_TEXT, exact=True
                ).last
                await contracting_menu.wait_for(
                    timeout=timeout_config.get_element_timeout()
                )
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
                await started_tab.wait_for(
                    timeout=timeout_config.get_element_timeout()
                )
                await started_tab.click()
                await self.page.wait_for_timeout(300)
                self.logger.info("[OK] 已点击已启动 Tab")
            except Exception as e:
                error_msg = f"点击已启动 Tab 失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "Tab 错误")
                raise

    async def search_project(self, project_name: str) -> None:
        """搜索项目"""
        self.logger.info(f"开始搜索项目: {project_name}")

        with allure.step(f"搜索项目: {project_name}"):
            try:
                project_filter = self.page.locator("label").filter(
                    has_text=self.PROJECT_SEARCH_LABEL_TEXT
                ).first
                await project_filter.wait_for(
                    timeout=timeout_config.get_element_timeout()
                )
                await project_filter.click()

                project_input = self.page.get_by_label(self.PROJECT_SEARCH_LABEL_TEXT)
                await project_input.wait_for(
                    timeout=timeout_config.get_element_timeout()
                )
                await project_input.fill(project_name)
                await self.page.wait_for_timeout(200)

                search_button = self.page.locator(self.SEARCH_BUTTON_SELECTOR).first
                await search_button.wait_for(
                    timeout=timeout_config.get_element_timeout()
                )
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
                go_contracting_btn = self.page.get_by_text(
                    self.GO_CONTRACTING_BUTTON_TEXT, exact=True
                ).first
                await go_contracting_btn.wait_for(
                    timeout=timeout_config.get_element_timeout()
                )
                await go_contracting_btn.click()
                await self.page.wait_for_load_state("networkidle")
                self.logger.info("[OK] 已点击去签约按钮")
            except Exception as e:
                error_msg = f"点击去签约按钮失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "按钮错误")
                raise

    # ======================================================================
    # 视图模式切换
    # ======================================================================

    async def _open_view_mode_dropdown(self) -> None:
        """打开视图模式切换下拉框"""
        dropdown = self.page.locator(self.VIEW_MODE_DROPDOWN_SELECTOR)
        await dropdown.wait_for(timeout=timeout_config.get_element_timeout())
        await dropdown.click()
        await self.page.wait_for_timeout(300)

    async def switch_to_list_mode(self) -> None:
        """切换至列表模式"""
        self.logger.info("切换至列表模式")

        with allure.step("切换至列表模式"):
            try:
                await self._open_view_mode_dropdown()
                list_mode = self.page.locator(self.LIST_MODE_OPTION_SELECTOR)
                await list_mode.wait_for(
                    timeout=timeout_config.get_element_timeout()
                )
                await list_mode.click()
                await self.page.wait_for_timeout(300)
                self.logger.info("[OK] 已切换至列表模式")
            except Exception as e:
                error_msg = f"切换至列表模式失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "列表模式错误")
                raise

    async def switch_to_map_mode(self) -> None:
        """切换至地图模式"""
        self.logger.info("切换至地图模式")

        with allure.step("切换至地图模式"):
            try:
                await self._open_view_mode_dropdown()
                map_mode = self.page.locator(self.MAP_MODE_OPTION_SELECTOR)
                await map_mode.wait_for(
                    timeout=timeout_config.get_element_timeout()
                )
                await map_mode.click()
                await self.page.wait_for_timeout(300)
                self.logger.info("[OK] 已切换至地图模式")
            except Exception as e:
                error_msg = f"切换至地图模式失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "地图模式错误")
                raise

    # ======================================================================
    # 导入签约状态
    # ======================================================================

    async def import_signing_status_file(self, excel_path: str) -> None:
        """导入签约状态 Excel 文件"""
        self.logger.info(f"导入签约状态文件: {excel_path}")

        with allure.step("导入签约状态文件"):
            try:
                file_input = self.page.locator(self.IMPORT_STATUS_FILE_SELECTOR)
                await file_input.set_input_files(excel_path)
                await self.page.wait_for_timeout(500)
                self.logger.info("[OK] 签约状态文件已导入")
            except Exception as e:
                error_msg = f"导入签约状态文件失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "导入错误")
                raise

    # ======================================================================
    # 价格状态页签
    # ======================================================================

    async def click_price_status_tab(self, tab_name: str) -> None:
        """点击指定价格状态页签"""
        self.logger.info(f"点击价格状态页签: {tab_name}")

        with allure.step(f"点击价格状态页签: {tab_name}"):
            try:
                price_tab = self.page.locator(
                    self.PRICE_TAB_XPATH_FORMAT.format(tab_name)
                )
                await price_tab.wait_for(
                    timeout=timeout_config.get_element_timeout()
                )
                await price_tab.click()
                await self.page.wait_for_timeout(300)
                self.logger.info(f"[OK] 已点击价格状态页签: {tab_name}")
            except Exception as e:
                error_msg = f"点击价格状态页签 [{tab_name}] 失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "价格页签错误")
                raise

    # ======================================================================
    # 酒店操作
    # ======================================================================

    async def click_first_hotel(self) -> None:
        """点击当前价格状态下的首个酒店"""
        self.logger.info("点击首个酒店")

        with allure.step("点击首个酒店"):
            try:
                first_hotel = self.page.locator(self.HOTEL_LIST_ITEM_SELECTOR).first
                await first_hotel.wait_for(
                    timeout=timeout_config.get_element_timeout()
                )
                await first_hotel.click()
                await self.page.wait_for_timeout(300)
                self.logger.info("[OK] 已点击首个酒店")
            except Exception as e:
                error_msg = f"点击首个酒店失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "酒店点击错误")
                raise

    async def verify_hotel_exists(self) -> bool:
        """验证当前价格状态页签下是否存在酒店"""
        self.logger.info("验证当前价格状态页签下是否存在酒店")
        try:
            hotel = self.page.locator(self.HOTEL_LIST_ITEM_SELECTOR).first
            await hotel.wait_for(timeout=timeout_config.get_element_timeout())
            is_visible = await hotel.is_visible()
            self.logger.info(f"酒店存在: {is_visible}")
            return is_visible
        except Exception as e:
            self.logger.error(f"验证酒店存在失败: {str(e)}")
            return False

    # ======================================================================
    # 操作按钮
    # ======================================================================

    async def click_continue_negotiation(self) -> None:
        """点击继续议价按钮"""
        self.logger.info("点击继续议价按钮")

        with allure.step("点击继续议价按钮"):
            try:
                # 使用 XPath 精确定位
                btn = self.page.locator(
                    f"//div[@class='btn-tr main mr-16' and text()='{self.CONTINUE_NEGOTIATION_BUTTON_TEXT}']"
                )
                await btn.wait_for(timeout=timeout_config.get_element_timeout())
                await btn.click()
                await self.page.wait_for_timeout(300)
                self.logger.info("[OK] 已点击继续议价按钮")
            except Exception as e:
                error_msg = f"点击继续议价按钮失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "继续议价错误")
                raise

    async def click_hotel_signed(self) -> None:
        """点击中签按钮"""
        self.logger.info("点击中签按钮")

        with allure.step("点击中签按钮"):
            try:
                # 中签按钮可能有前导空格，使用 contains 匹配
                btn = self.page.locator(
                    f"//div[@class='btn-tr main mr-16' and contains(text(), '{self.SIGNED_BUTTON_TEXT}')]"
                )
                await btn.wait_for(timeout=timeout_config.get_element_timeout())
                await btn.click()
                await self.page.wait_for_timeout(300)
                self.logger.info("[OK] 已点击中签按钮")
            except Exception as e:
                error_msg = f"点击中签按钮失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "中签按钮错误")
                raise

    async def click_hotel_rejected(self) -> None:
        """点击否决按钮"""
        self.logger.info("点击否决按钮")

        with allure.step("点击否决按钮"):
            try:
                rejected_btn = self.page.get_by_text(
                    self.REJECTED_BUTTON_TEXT, exact=True
                )
                await rejected_btn.wait_for(
                    timeout=timeout_config.get_element_timeout()
                )
                await rejected_btn.click()
                await self.page.wait_for_timeout(300)
                self.logger.info("[OK] 已点击否决按钮")
            except Exception as e:
                error_msg = f"点击否决按钮失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "否决按钮错误")
                raise

    async def click_action_by_type(self, action: str) -> None:
        """根据动作类型点击对应的操作按钮

        Args:
            action: 操作类型，"继续议价" / "中签" / "否决"
        """
        action_map = {
            "继续议价": self.click_continue_negotiation,
            "中签": self.click_hotel_signed,
            "否决": self.click_hotel_rejected,
        }
        handler = action_map.get(action)
        if handler is None:
            raise ValueError(f"不支持的操作类型: {action}")
        await handler()

    # ======================================================================
    # 留言板
    # ======================================================================

    async def fill_message(self, message: str) -> None:
        """在留言板输入内容"""
        self.logger.info(f"输入留言: {message}")

        with allure.step(f"输入留言: {message}"):
            try:
                msg_input = self.page.locator(self.MESSAGE_BOARD_SELECTOR)
                await msg_input.wait_for(
                    timeout=timeout_config.get_element_timeout()
                )
                await msg_input.click()
                await msg_input.fill(message)
                await self.page.wait_for_timeout(200)
                self.logger.info("[OK] 留言已输入")
            except Exception as e:
                error_msg = f"输入留言失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "留言输入错误")
                raise

    # ======================================================================
    # 确定按钮
    # ======================================================================

    async def click_confirm(self) -> None:
        """点击确定按钮"""
        self.logger.info("点击确定按钮")

        with allure.step("点击确定按钮"):
            try:
                confirm_btn = self.page.get_by_text(
                    self.CONFIRM_BUTTON_TEXT, exact=True
                )
                await confirm_btn.wait_for(
                    timeout=timeout_config.get_element_timeout()
                )
                await confirm_btn.click()
                await self.page.wait_for_timeout(500)
                self.logger.info("[OK] 已点击确定按钮")
            except Exception as e:
                error_msg = f"点击确定按钮失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "确定按钮错误")
                raise

    # ======================================================================
    # URL 验证
    # ======================================================================

    async def get_current_url(self) -> str:
        """获取当前页面 URL"""
        url = self.page.url
        self.logger.info(f"当前 URL: {url}")
        return url

    def url_contains_bid_evaluation(self, url: str) -> bool:
        """判断 URL 是否包含去签约成功跳转标识"""
        result = self.BID_EVALUATION_KEYWORD in url
        self.logger.info(f"URL 包含 bidEvaluationDetails: {result}")
        return result