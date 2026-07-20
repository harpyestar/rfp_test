"""
酒店端 - 报价项目页面对象模型
处理酒店端的报价项目列表、搜索、修改报价、提交报价等操作
"""

from playwright.async_api import Page
from pages.common.base_page import BasePage
from utils.config import config
from utils.timeout_config import timeout_config
from utils.logger import get_logger
import allure
import re


class HotelBiddingPage(BasePage):
    """酒店端报价项目页面对象"""

    # ========== 导航 ==========
    HOME_PATH = "/hotel.html#/home"

    # ========== 首页操作按钮 ==========
    BIDDING_PROJECT_TEXT = "报价项目"

    # ========== 搜索 ==========
    PROJECT_SEARCH_LABEL = "签约项目"
    HOTEL_NAME_SEARCH_ROLE = "酒店名称"
    SEARCH_BUTTON_SELECTOR = ".c-icon-search"

    # ========== 操作按钮 ==========
    MODIFY_QUOTE_TEXT = "修改报价"
    CLOSE_TEXT = "关闭"
    SUBMIT_QUOTE_TEXT = "提交报价"
    CONFIRM_TEXT = "确定"
    SUCCESS_TOAST_TEXT = "操作成功"

    def __init__(self, page: Page):
        super().__init__(page)
        self.logger = get_logger(self.__class__.__name__, config.log_level)

    async def navigate_to_home(self) -> None:
        """进入酒店端工作台页面"""
        self.logger.info("进入酒店端工作台")
        with allure.step("进入酒店端工作台"):
            try:
                home_url = f"{config.base_url.rstrip('/')}{self.HOME_PATH}"
                await self.goto(home_url)
                await self.wait_helper.wait_for_url(
                    self.page, "**/home*", timeout=timeout_config.get_navigation_timeout()
                )
                self.logger.info("[OK] 已进入酒店端工作台")
            except Exception as e:
                error_msg = f"进入酒店端工作台失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "导航错误")
                raise

    async def click_bidding_project(self) -> None:
        """点击报价项目"""
        self.logger.info("点击报价项目")
        with allure.step("点击报价项目"):
            try:
                btn = self.page.get_by_text(self.BIDDING_PROJECT_TEXT, exact=True)
                await btn.wait_for(timeout=timeout_config.get_element_timeout())
                await btn.click()
                await self.page.wait_for_load_state("networkidle")
                self.logger.info("[OK] 已点击报价项目")
            except Exception as e:
                error_msg = f"点击报价项目失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "点击报价项目错误")
                raise

    async def click_negotiating_tab(self) -> None:
        """点击议价中Tab（后面可能带数字，模糊匹配）"""
        self.logger.info("点击议价中Tab")
        with allure.step("点击议价中Tab"):
            try:
                tab = self.page.locator("div").filter(
                    has_text=re.compile(r"^议价中")
                ).first
                await tab.wait_for(timeout=timeout_config.get_element_timeout())
                await tab.click()
                await self.page.wait_for_timeout(300)
                self.logger.info("[OK] 已点击议价中Tab")
            except Exception as e:
                error_msg = f"点击议价中Tab失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "议价中Tab错误")
                raise

    async def search(self, project_name: str, hotel_name: str) -> None:
        """搜索项目和酒店"""
        self.logger.info(f"搜索项目: {project_name}, 酒店: {hotel_name}")
        with allure.step(f"搜索项目并输入酒店名称"):
            try:
                # 签约项目
                project_input = self.page.get_by_label(self.PROJECT_SEARCH_LABEL)
                await project_input.wait_for(timeout=timeout_config.get_element_timeout())
                await project_input.fill(project_name)
                await self.page.wait_for_timeout(200)

                # 酒店名称
                hotel_input = self.page.get_by_role(
                    "textbox", name=self.HOTEL_NAME_SEARCH_ROLE
                )
                await hotel_input.wait_for(timeout=timeout_config.get_element_timeout())
                await hotel_input.fill(hotel_name)
                await self.page.wait_for_timeout(200)

                # 搜索按钮
                search_btn = self.page.locator(self.SEARCH_BUTTON_SELECTOR).first
                await search_btn.wait_for(timeout=timeout_config.get_element_timeout())
                await search_btn.click()
                await self.page.wait_for_load_state("networkidle")
                self.logger.info("[OK] 搜索完成")
            except Exception as e:
                error_msg = f"搜索失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "搜索错误")
                raise

    async def click_modify_quote(self) -> None:
        """点击修改报价"""
        self.logger.info("点击修改报价")
        with allure.step("点击修改报价"):
            try:
                btn = self.page.get_by_text(self.MODIFY_QUOTE_TEXT, exact=True)
                await btn.wait_for(timeout=timeout_config.get_element_timeout())
                await btn.click()
                await self.page.wait_for_load_state("networkidle")
                self.logger.info("[OK] 已点击修改报价")
            except Exception as e:
                error_msg = f"点击修改报价失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "修改报价错误")
                raise

    async def close_remark_dialog(self) -> None:
        """关闭备注留言弹窗（若弹窗未出现则跳过）"""
        self.logger.info("关闭备注留言弹窗")
        with allure.step("关闭备注留言弹窗"):
            close_btn = self.page.get_by_text(self.CLOSE_TEXT)
            try:
                await close_btn.wait_for(timeout=timeout_config.get_quick_step_timeout())
                await close_btn.click()
                await self.page.wait_for_timeout(1000)
                self.logger.info("[OK] 备注留言弹窗已关闭")
            except Exception:
                self.logger.info("备注留言弹窗未出现，跳过关闭")

    async def click_submit_quote(self) -> None:
        """点击顶部提交报价按钮（div.c-button.ml-20.bg-primary:has-text('提交报价')）"""
        self.logger.info("点击提交报价")
        with allure.step("点击提交报价"):
            try:
                await self.page.wait_for_timeout(1000)
                # 顶部按钮有 ml-20 class，底部按钮在 .c-division 内、无 ml-20
                btn = self.page.locator(
                    'div.c-button.ml-20.bg-primary:has-text("提交报价")'
                )
                await btn.wait_for(timeout=timeout_config.get_element_timeout())
                await btn.click()
                await self.page.wait_for_timeout(500)
                self.logger.info("[OK] 已点击提交报价")
            except Exception as e:
                error_msg = f"点击提交报价失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "提交报价错误")
                raise

    async def click_confirm(self) -> None:
        """二次确认弹窗 - 点击确定"""
        self.logger.info("二次确认弹窗 - 点击确定")
        with allure.step("二次确认弹窗 - 点击确定"):
            try:
                # 优先匹配通用确认弹窗，否则匹配中签弹窗
                confirm_btn = self.page.locator("div.c-asm.c-button.bg-white").filter(
                    has_text=self.CONFIRM_TEXT
                ).first
                if not await confirm_btn.count():
                    confirm_btn = self.page.locator("button.winning-confirm-btn--primary")
                await confirm_btn.wait_for(timeout=timeout_config.get_element_timeout())
                await confirm_btn.click()
                await self.page.wait_for_timeout(500)
                self.logger.info("[OK] 已点击确定按钮")
            except Exception as e:
                error_msg = f"点击确定按钮失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "确定按钮错误")
                raise

    async def is_toast_success(self) -> bool:
        """验证操作成功toast是否存在"""
        self.logger.info("验证操作成功toast")
        with allure.step("验证操作成功"):
            try:
                toast = self.page.get_by_text(self.SUCCESS_TOAST_TEXT)
                await toast.wait_for(timeout=timeout_config.get_element_timeout())
                self.logger.info("操作成功toast已出现")
                return True
            except Exception as e:
                self.logger.warning(f"操作成功toast未出现: {str(e)}")
                return False