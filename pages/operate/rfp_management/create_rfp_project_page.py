"""
创建 RFP 项目页面对象模型
负责创建新的 RFP 项目流程：导航至创建页面、填写表单、保存并验证
所有可变业务数据由调用方从 JSON 参数传入
"""

from playwright.async_api import Page
from pages.common.base_page import BasePage
from utils.config import config
from utils.timeout_config import timeout_config
from utils.logger import get_logger
import allure


class CreateRFPProjectPage(BasePage):
    """创建 RFP 项目 Page Object"""

    # ========== 导航菜单 ==========
    RFP_MANAGEMENT_MENU_TEXT = "签约管理"
    CREATE_PROJECT_DROPDOWN_TEXT = "发布项目"

    # ========== 按钮文本 ==========
    SAVE_AND_NEXT_BUTTON_TEXT = "保存并下一步"

    # ========== Toast 提示 ==========
    SUCCESS_TOAST_SELECTOR = ".c-view.c-notify-content-description.bold"

    # ========== 表单输入框定位 ==========
    # 模式：按 label 文本定位邻近 input
    AGENCY_INPUT = "xpath=//div[text()='签约机构']/../following-sibling::div//input"
    PROJECT_NAME_INPUT = "xpath=//div[text()='签约项目名称']/../following-sibling::div//input"
    CONTACT_PERSON_INPUT = "xpath=//div[text()='联系人']/../following-sibling::div//input"
    CONTACT_PHONE_INPUT = "xpath=//div[text()='联系电话']/../following-sibling::div//input"
    HOTEL_COUNT_INPUT = "xpath=//div[text()='预计签约酒店数量']/../following-sibling::div//input"
    MIN_DIFF_STD_INPUT = "xpath=//div[text()='公司差标最小值']/../following-sibling::div//input"
    MAX_DIFF_STD_INPUT = "xpath=//div[text()='公司差标最大值']/../following-sibling::div//input"

    # ========== 签约方式单选 ==========
    INVITATION_SIGN_RADIO = (
        "xpath=//div[text()='签约方式']/../following-sibling::div"
        "//div[@title='邀请签约(仅邀请的酒店参与)']"
        "/../preceding-sibling::div[@class='c-select-radio']"
    )

    # ========== 日期触发区定位 ==========
    # 模式：按 label 文本定位日期触发区域（展开日历用）
    REGISTRATION_DATE_TRIGGER = (
        "xpath=//div[text()='报名起止时间']/../following-sibling::div"
        "//i[@class='c-animated-arrow noshrink']/preceding-sibling::div"
    )
    SPLIT_DATE_TRIGGER_FORMAT = (
        "xpath=//div[text()='{}']/../following-sibling::div"
        "//i[@class='c-animated-arrow noshrink']/preceding-sibling::div"
    )

    # ========== 日历面板日期数字 ==========
    CALENDAR_DAY_FORMAT = (
        "xpath=//div[@class='c-calendar-body']"
        "//div[@class='c-calendar-date-cell-label' and text()='{}']"
    )

    # ========== 清理：Contracting 列表页 ==========
    CONTRACTING_MENU_TEXT = "签约"
    NOT_STARTED_TAB_TEXT = "未启动"
    PROJECT_SEARCH_INPUT = (
        "xpath=//div[@class='c-division']//label[@class='c-input flex-row-start align-center']"
        "//div[text()='签约项目']/../following-sibling::input"
    )
    SEARCH_BUTTON = "xpath=//div[contains(@class, 'ml-15 ')]//i"
    VOID_BUTTON = "xpath=//tbody//a[contains(text(), '作废')]"
    CONFIRM_BUTTON_TEXT = "确定"

    def __init__(self, page: Page):
        super().__init__(page)
        self.logger = get_logger(self.__class__.__name__, config.log_level)

    # ======================================================================
    # 导航
    # ======================================================================

    async def navigate_to_create_project(self) -> None:
        """导航至 签约管理 > 发布项目"""
        self.logger.info("开始导航至创建 RFP 项目页面")

        with allure.step("导航至 签约管理 > 发布项目"):
            try:
                try:
                    await self.page.reload()
                except Exception:
                    pass
                self.logger.debug("点击 签约管理 菜单")
                rfp_menu = self.page.get_by_text(self.RFP_MANAGEMENT_MENU_TEXT, exact=True)
                await rfp_menu.wait_for(timeout=timeout_config.get_element_timeout())
                await rfp_menu.click()
                await self.page.wait_for_timeout(300)

                self.logger.debug(f"点击 {self.CREATE_PROJECT_DROPDOWN_TEXT} 选项")
                create_option = self.page.get_by_text(self.CREATE_PROJECT_DROPDOWN_TEXT, exact=True).first
                await create_option.wait_for(timeout=timeout_config.get_element_timeout())
                await create_option.click()

                await self.page.wait_for_load_state("networkidle")
                self.logger.info("[OK] 已进入创建 RFP 项目页面")

            except Exception as e:
                error_msg = f"导航至创建项目页面失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "导航错误")
                raise

    # ======================================================================
    # 表单字段填写方法
    # ======================================================================

    async def select_contracting_agency(self, agency_name: str) -> None:
        """填写并选择签约机构"""
        self.logger.info(f"填写签约机构: {agency_name}")

        with allure.step(f"填写签约机构: {agency_name}"):
            try:
                agency_input = self.page.locator(self.AGENCY_INPUT)
                await agency_input.wait_for(timeout=timeout_config.get_element_timeout())
                await agency_input.click()
                await agency_input.fill(agency_name)
                self.logger.debug("等待下拉选项出现")
                await self.page.wait_for_timeout(500)

                option = self.page.get_by_text(agency_name, exact=True)
                await option.wait_for(timeout=timeout_config.get_element_timeout())
                await option.click()
                self.logger.info(f"[OK] 签约机构已选择: {agency_name}")

            except Exception as e:
                error_msg = f"选择签约机构失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "签约机构错误")
                raise

    async def fill_project_name(self, project_name: str) -> None:
        """填写签约项目名称"""
        self.logger.info(f"填写签约项目名称: {project_name}")

        with allure.step(f"填写签约项目名称: {project_name}"):
            try:
                name_input = self.page.locator(self.PROJECT_NAME_INPUT)
                await name_input.wait_for(timeout=timeout_config.get_element_timeout())
                await name_input.click()
                await name_input.fill(project_name)
                self.logger.info(f"[OK] 签约项目名称已填写: {project_name}")

            except Exception as e:
                error_msg = f"填写签约项目名称失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "项目名称错误")
                raise

    async def fill_contact_person(self, person_name: str) -> None:
        """填写联系人"""
        self.logger.info(f"填写联系人: {person_name}")

        with allure.step(f"填写联系人: {person_name}"):
            try:
                contact_input = self.page.locator(self.CONTACT_PERSON_INPUT)
                await contact_input.wait_for(timeout=timeout_config.get_element_timeout())
                await contact_input.click()
                await contact_input.fill(person_name)
                self.logger.info(f"[OK] 联系人已填写: {person_name}")

            except Exception as e:
                error_msg = f"填写联系人失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "联系人错误")
                raise

    async def fill_contact_phone(self, phone: str) -> None:
        """填写联系电话"""
        self.logger.info(f"填写联系电话: {phone}")

        with allure.step(f"填写联系电话: {phone}"):
            try:
                phone_input = self.page.locator(self.CONTACT_PHONE_INPUT)
                await phone_input.wait_for(timeout=timeout_config.get_element_timeout())
                await phone_input.click()
                await phone_input.fill(phone)
                self.logger.info(f"[OK] 联系电话已填写: {phone}")

            except Exception as e:
                error_msg = f"填写联系电话失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "联系电话错误")
                raise

    async def select_invitation_sign_method(self) -> None:
        """选择签约方式：邀请签约(仅邀请的酒店参与)"""
        self.logger.info("选择签约方式: 邀请签约")

        with allure.step("选择签约方式: 邀请签约"):
            try:
                radio = self.page.locator(self.INVITATION_SIGN_RADIO)
                await radio.wait_for(timeout=timeout_config.get_element_timeout())
                await radio.click()
                self.logger.info("[OK] 签约方式已选择: 邀请签约")

            except Exception as e:
                error_msg = f"选择签约方式失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "签约方式错误")
                raise

    # ======================================================================
    # 日期选择方法
    # ======================================================================

    async def _click_calendar_day(self, day: int) -> None:
        """在日历面板中点击指定日期数字"""
        day_locator = self.page.locator(self.CALENDAR_DAY_FORMAT.format(day))
        await day_locator.wait_for(timeout=timeout_config.get_element_timeout())
        await day_locator.click()

    async def select_registration_date(self, start_day: int, end_day: int) -> None:
        """选择报名起止时间（单范围选择器）"""
        self.logger.info(f"选择报名起止时间: {start_day} - {end_day}")

        with allure.step(f"选择报名起止时间: 第{start_day}天 - 第{end_day}天"):
            try:
                trigger = self.page.locator(self.REGISTRATION_DATE_TRIGGER)
                await trigger.wait_for(timeout=timeout_config.get_element_timeout())
                await trigger.click()
                await self.page.wait_for_timeout(300)

                await self._click_calendar_day(start_day)
                await self.page.wait_for_timeout(200)
                await self._click_calendar_day(end_day)
                self.logger.info(f"[OK] 报名起止时间已选择: {start_day} - {end_day}")

            except Exception as e:
                error_msg = f"选择报名起止时间失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "报名起止时间错误")
                raise

    async def _select_split_date_range(self, label: str, start_day: int, end_day: int) -> None:
        """选择分离式日期范围（有独立开始/结束字段）"""
        container = self.page.locator(self.SPLIT_DATE_TRIGGER_FORMAT.format(label))

        await container.first.wait_for(timeout=timeout_config.get_element_timeout())
        await container.first.click()
        await self.page.wait_for_timeout(200)
        await self._click_calendar_day(start_day)
        self.logger.debug(f"{label} 开始日已选: {start_day}")

        await self.page.wait_for_timeout(200)
        await container.last.click()
        await self.page.wait_for_timeout(200)
        await self._click_calendar_day(end_day)
        self.logger.debug(f"{label} 结束日已选: {end_day}")

    async def select_first_round_date(self, start_day: int, end_day: int) -> None:
        """选择第一轮报价起止时间"""
        self.logger.info(f"选择第一轮报价起止时间: {start_day} - {end_day}")

        with allure.step(f"选择第一轮报价起止时间: 第{start_day}天 - 第{end_day}天"):
            try:
                await self._select_split_date_range("第一轮报价起止时间", start_day, end_day)
                self.logger.info(f"[OK] 第一轮报价起止时间已选择: {start_day} - {end_day}")
            except Exception as e:
                error_msg = f"选择第一轮报价起止时间失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "第一轮报价起止时间错误")
                raise

    async def select_agreement_date(self, start_day: int, end_day: int) -> None:
        """选择协议报价日期范围"""
        self.logger.info(f"选择协议报价日期范围: {start_day} - {end_day}")

        with allure.step(f"选择协议报价日期范围: 第{start_day}天 - 第{end_day}天"):
            try:
                await self._select_split_date_range("协议报价日期范围", start_day, end_day)
                self.logger.info(f"[OK] 协议报价日期范围已选择: {start_day} - {end_day}")
            except Exception as e:
                error_msg = f"选择协议报价日期范围失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "协议报价日期范围错误")
                raise

    # ======================================================================
    # 数值字段填写
    # ======================================================================

    async def fill_expected_hotel_count(self, count: str) -> None:
        """填写预计签约酒店数量"""
        self.logger.info(f"填写预计签约酒店数量: {count}")

        with allure.step(f"填写预计签约酒店数量: {count}"):
            try:
                count_input = self.page.locator(self.HOTEL_COUNT_INPUT)
                await count_input.wait_for(timeout=timeout_config.get_element_timeout())
                await count_input.click()
                await count_input.fill(count)
                self.logger.info(f"[OK] 预计签约酒店数量已填写: {count}")
            except Exception as e:
                error_msg = f"填写预计签约酒店数量失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "预计签约酒店数量错误")
                raise

    async def fill_min_diff_std(self, value: str) -> None:
        """填写公司差标最小值"""
        self.logger.info(f"填写公司差标最小值: {value}")

        with allure.step(f"填写公司差标最小值: {value}"):
            try:
                min_input = self.page.locator(self.MIN_DIFF_STD_INPUT)
                await min_input.wait_for(timeout=timeout_config.get_element_timeout())
                await min_input.click()
                await min_input.fill(value)
                self.logger.info(f"[OK] 公司差标最小值已填写: {value}")
            except Exception as e:
                error_msg = f"填写公司差标最小值失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "公司差标最小值错误")
                raise

    async def fill_max_diff_std(self, value: str) -> None:
        """填写公司差标最大值"""
        self.logger.info(f"填写公司差标最大值: {value}")

        with allure.step(f"填写公司差标最大值: {value}"):
            try:
                max_input = self.page.locator(self.MAX_DIFF_STD_INPUT)
                await max_input.wait_for(timeout=timeout_config.get_element_timeout())
                await max_input.click()
                await max_input.fill(value)
                self.logger.info(f"[OK] 公司差标最大值已填写: {value}")
            except Exception as e:
                error_msg = f"填写公司差标最大值失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "公司差标最大值错误")
                raise

    # ======================================================================
    # 清理：作废已创建的项目
    # ======================================================================

    async def navigate_to_contracting(self) -> None:
        """导航至 签约管理 > 签约（Contracting 列表页）"""
        self.logger.info("开始导航至 Contracting 页面")

        with allure.step("导航至 签约管理 > 签约"):
            try:
                try:
                    await self.page.reload()
                except Exception:
                    pass
                contracting_option = self.page.get_by_text(self.CONTRACTING_MENU_TEXT, exact=True)

                # 先检查子菜单是否已可见，避免重击父级导致折叠
                if not await contracting_option.is_visible():
                    rfp_menu = self.page.get_by_text(self.RFP_MANAGEMENT_MENU_TEXT, exact=True)
                    await rfp_menu.wait_for(timeout=timeout_config.get_element_timeout())
                    await rfp_menu.click()
                    await self.page.wait_for_timeout(300)

                await contracting_option.wait_for(timeout=timeout_config.get_element_timeout())
                await contracting_option.click()

                await self.page.wait_for_load_state("networkidle")
                self.logger.info("[OK] 已进入 Contracting 页面")

            except Exception as e:
                error_msg = f"导航至 Contracting 页面失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "导航错误")
                raise

    async def click_not_started_tab(self) -> None:
        """选择 Not Started Tab"""
        self.logger.info("点击 Not Started Tab")

        with allure.step("选择 Not Started Tab"):
            try:
                not_started_tab = self.page.get_by_text(self.NOT_STARTED_TAB_TEXT, exact=True)
                await not_started_tab.wait_for(timeout=timeout_config.get_element_timeout())
                await not_started_tab.click()
                await self.page.wait_for_load_state("networkidle")
                self.logger.info("[OK] 已选择 Not Started Tab")

            except Exception as e:
                error_msg = f"点击 Not Started Tab 失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "Tab 错误")
                raise

    async def search_project_by_name(self, project_name: str) -> None:
        """在 Contracting 列表页中按名称搜索项目"""
        self.logger.info(f"搜索项目: {project_name}")

        with allure.step(f"搜索项目: {project_name}"):
            try:
                search_input = self.page.locator(self.PROJECT_SEARCH_INPUT)
                await search_input.wait_for(timeout=timeout_config.get_element_timeout())
                await search_input.click()
                await search_input.fill(project_name)
                await self.page.wait_for_timeout(300)

                search_btn = self.page.locator(self.SEARCH_BUTTON).first
                await search_btn.wait_for(timeout=timeout_config.get_element_timeout())
                await search_btn.click()
                await self.page.wait_for_load_state("networkidle")
                self.logger.info(f"[OK] 项目搜索完成: {project_name}")

            except Exception as e:
                error_msg = f"搜索项目失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "搜索错误")
                raise

    async def void_first_project(self) -> None:
        """作废搜索结果中的首个项目"""
        self.logger.info("开始作废首个匹配项目")

        with allure.step("作废首个匹配项目"):
            try:
                void_btn = self.page.locator(self.VOID_BUTTON).first
                await void_btn.wait_for(timeout=timeout_config.get_element_timeout())
                await void_btn.click()
                await self.page.wait_for_timeout(300)

                confirm_btn = self.page.get_by_text(self.CONFIRM_BUTTON_TEXT, exact=True)
                await confirm_btn.wait_for(timeout=timeout_config.get_element_timeout())
                await confirm_btn.click()
                await self.page.wait_for_timeout(500)
                self.logger.info("[OK] 已作废项目")

            except Exception as e:
                error_msg = f"作废项目失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "作废错误")
                raise

    # ======================================================================
    # 保存操作
    # ======================================================================

    async def click_save_and_next(self) -> None:
        """点击保存并下一步"""
        self.logger.info("点击保存并下一步")

        with allure.step("点击保存并下一步"):
            try:
                save_btn = self.page.get_by_text(self.SAVE_AND_NEXT_BUTTON_TEXT, exact=True)
                await save_btn.wait_for(timeout=timeout_config.get_element_timeout())
                await save_btn.click()
                self.logger.info("[OK] 已点击保存并下一步")
                await self.page.wait_for_timeout(2000)

            except Exception as e:
                error_msg = f"点击保存并下一步失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "保存按钮错误")
                raise

    async def verify_save_success(self) -> str:
        """验证保存成功并返回 toast 文本"""
        self.logger.info("开始验证保存成功提示")

        with allure.step("验证保存成功提示"):
            try:
                toast = self.page.locator(self.SUCCESS_TOAST_SELECTOR)
                await toast.wait_for(timeout=timeout_config.get_element_timeout())

                toast_text = await toast.text_content()
                toast_text = toast_text.strip() if toast_text else ""
                self.logger.info(f"[OK] 保存成功提示: {toast_text}")

                allure.attach(toast_text, "Toast 提示内容")
                return toast_text

            except Exception as e:
                error_msg = f"验证保存成功失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "验证错误")
                raise

    # ======================================================================
    # 完整流程组合方法
    # ======================================================================

    async def create_project_full_flow(self, project_name: str, project_data: dict) -> str:
        """
        完整的创建 RFP 项目流程

        Args:
            project_name: 签约项目名称（已含时间戳）
            project_data: 项目业务数据字典（从 JSON 参数读取）

        Returns:
            str: 保存成功的 toast 文本
        """
        self.logger.info("=== 开始完整创建 RFP 项目流程 ===")

        await self.navigate_to_create_project()

        await self.select_contracting_agency(project_data["agency_name"])
        await self.fill_project_name(project_name)
        await self.fill_contact_person(project_data["contact_person"])
        await self.fill_contact_phone(project_data["contact_phone"])
        await self.select_invitation_sign_method()

        await self.select_registration_date(project_data["start_day"], project_data["end_day"])
        await self.select_first_round_date(project_data["start_day"], project_data["end_day"])
        await self.select_agreement_date(project_data["start_day"], project_data["end_day"])

        await self.fill_expected_hotel_count(project_data["expected_hotel_count"])
        await self.fill_min_diff_std(project_data["min_diff_std"])
        await self.fill_max_diff_std(project_data["max_diff_std"])

        await self.click_save_and_next()
        toast_text = await self.verify_save_success()

        self.logger.info(f"=== 创建 RFP 项目流程完成，toast: {toast_text} ===")
        return toast_text