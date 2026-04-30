"""
编辑 RFP 项目页面对象模型
负责 RFP 项目编辑流程中的 Tab 切换、保存验证等交互操作
所有超时值从 timeout_config 中读取，所有选择器统一在类变量中定义
"""

from playwright.async_api import Page
from pages.common.base_page import BasePage
from utils.config import config
from utils.timeout_config import timeout_config
from utils.logger import get_logger
import allure
import re


class EditRFPProjectPage(BasePage):
    """编辑 RFP 项目 Page Object"""

    # ========== 导航菜单元素 ==========
    RFP_MANAGEMENT_MENU_NAME = "RFP Management"
    CONTRACTING_MENU_TEXT = "Contracting"
    MODIFY_PROJECT_BUTTON_TEXT = "Modify Project"

    # ========== Contracting 页面元素 ==========
    NOT_STARTED_TAB_NAME = "Not Started"
    STARTED_TAB_NAME = "Started"
    PROJECT_SEARCH_FILTER_PATTERN = r"^Project$"
    PROJECT_SEARCH_FILTER_NTH = 1
    SEARCH_BUTTON_SELECTOR = ".search > .btn"
    PROJECT_SEARCH_INPUT_PLACEHOLDER = "请输入项目名称"

    # ========== 项目操作按钮 ==========
    START_BUTTON_TEXT = "Start"
    YES_CONFIRMATION_BUTTON_TEXT = "Yes"

    # ========== 编辑页面 Tab 元素 ==========
    SAVE_BUTTON_NAME = "Save"
    PREVIOUS_STEP_BUTTON_NAME = "Previous step"
    SUCCESS_MESSAGE_SELECTOR = ".el-message__content"

    # ========== Tab 列表 ==========
    # 从需求中的 Playwright 录制代码提取的所有 Tab 名称
    TAB_NAMES = [
        "Basic Contract Information",
        "Project Brief",
        "Company POI",
        "Invited Hotel",
        "Custom Procurement Strategy",
        "Project Procurement Strategy",
        "Weighted Settings",
        "Intelligent Recommendation",
        "Hotel Whitelist",
        "Lanyon Display Settings",
        "Historical Transaction Data"
    ]

    def __init__(self, page: Page):
        super().__init__(page)
        self.logger = get_logger(self.__class__.__name__, config.log_level)

    # ========== 导航方法 ==========
    async def navigate_to_contracting(self) -> None:
        """导航至 Contracting 页面"""
        self.logger.info("开始导航至 Contracting 页面")

        with allure.step("导航至 Contracting 页面"):
            try:
                # Step 1: 点击 RFP Management 菜单
                self.logger.debug("点击 RFP Management 菜单")
                rfp_menu = self.page.get_by_role("button", name=self.RFP_MANAGEMENT_MENU_NAME)
                await rfp_menu.click()
                self.logger.info("RFP Management 菜单已点击")

                # Step 2: 等待下拉菜单
                await self.page.wait_for_timeout(300)

                # Step 3: 点击 Contracting 菜单项
                self.logger.debug(f"点击 {self.CONTRACTING_MENU_TEXT} 菜单项")
                contracting_menu = self.page.get_by_label(self.RFP_MANAGEMENT_MENU_NAME).get_by_text(
                    self.CONTRACTING_MENU_TEXT
                )
                await contracting_menu.click()
                self.logger.info("Contracting 菜单项已点击")

                # Step 4: 等待页面加载
                await self.page.wait_for_load_state("networkidle")
                allure.attach("Contracting 页面已加载", "导航结果")
                self.logger.info("[OK] Contracting 页面加载完成")

            except Exception as e:
                error_msg = f"导航至 Contracting 页面失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "导航错误")
                raise

    async def click_not_started_tab(self) -> None:
        """点击 Not Started Tab"""
        self.logger.info("开始点击 Not Started Tab")

        with allure.step(f"选择 {self.NOT_STARTED_TAB_NAME} Tab"):
            try:
                # 点击 Not Started Tab
                self.logger.debug(f"定位 {self.NOT_STARTED_TAB_NAME} Tab")
                not_started_tab = self.page.get_by_role("tab", name=self.NOT_STARTED_TAB_NAME)
                await not_started_tab.click()
                self.logger.info("Not Started Tab 已点击")

                # 等待表格加载
                await self.page.wait_for_load_state("networkidle")
                allure.attach(f"已选择: {self.NOT_STARTED_TAB_NAME}", "Tab 选择")
                self.logger.info("[OK] Not Started Tab 加载完成")

            except Exception as e:
                error_msg = f"点击 Not Started Tab 失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "点击错误")
                raise

    async def click_started_tab(self) -> None:
        """点击 Started Tab"""
        self.logger.info("开始点击 Started Tab")

        with allure.step(f"选择 {self.STARTED_TAB_NAME} Tab"):
            try:
                # 点击 Started Tab
                self.logger.debug(f"定位 {self.STARTED_TAB_NAME} Tab")
                started_tab = self.page.get_by_role("tab", name=self.STARTED_TAB_NAME, exact=True)
                await started_tab.click()
                self.logger.info("Started Tab 已点击")

                # 等待表格加载
                await self.page.wait_for_load_state("networkidle")
                allure.attach(f"已选择: {self.STARTED_TAB_NAME}", "Tab 选择")
                self.logger.info("[OK] Started Tab 加载完成")

            except Exception as e:
                error_msg = f"点击 Started Tab 失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "点击错误")
                raise

    async def search_and_open_project(self, project_name: str) -> None:
        """搜索项目并打开编辑页面"""
        self.logger.info(f"开始搜索项目: {project_name}")

        with allure.step(f"搜索项目: {project_name}"):
            try:
                # Step 1: 点击 Project 搜索框 (使用 locator + filter)
                self.logger.debug("定位 Project 搜索框")
                project_filter = self.page.locator("div").filter(
                    has_text=re.compile(self.PROJECT_SEARCH_FILTER_PATTERN)
                ).nth(self.PROJECT_SEARCH_FILTER_NTH)
                await project_filter.click()
                self.logger.info("Project 搜索框已点击")

                # Step 2: 等待并输入项目名称
                await self.page.wait_for_timeout(300)
                self.logger.debug(f"输入项目名称: {project_name}")
                # 使用精准定位：外层+内层
                # 外层：已经通过filter定位到的project_filter (project_filter)
                # 内层：在该外层内找到 class="el-input__inner" 的 input
                search_input = project_filter.locator("input.el-input__inner")
                await search_input.clear()
                await search_input.fill(project_name)
                await self.page.wait_for_timeout(200)
                self.logger.info(f"项目名称已输入: {project_name}")

                # Step 3: 点击搜索按钮
                self.logger.debug("点击搜索按钮")
                search_btn = self.page.locator(self.SEARCH_BUTTON_SELECTOR)
                await search_btn.click()
                self.logger.info("搜索按钮已点击")

                # Step 4: 等待搜索结果加载
                await self.page.wait_for_load_state("networkidle")
                allure.attach(f"搜索项目: {project_name}", "搜索操作")
                self.logger.info("[OK] 项目搜索完成")

                # Step 5: 点击 Modify Project 按钮（首个）
                self.logger.debug(f"定位并点击 {self.MODIFY_PROJECT_BUTTON_TEXT} 按钮（首个）")
                modify_buttons = self.page.get_by_text(self.MODIFY_PROJECT_BUTTON_TEXT)
                first_modify_btn = modify_buttons.first
                await first_modify_btn.click()
                self.logger.info("Modify Project 按钮已点击")

                # Step 6: 等待编辑页面加载
                await self.page.wait_for_load_state("networkidle")
                allure.attach(f"已进入项目编辑页面: {project_name}", "进入编辑页面")
                self.logger.info("[OK] 项目编辑页面加载完成")

            except Exception as e:
                error_msg = f"搜索或打开项目失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "搜索/打开错误")
                raise

    # ========== Tab 切换与保存验证方法 ==========
    async def click_tab(self, tab_name: str) -> None:
        """点击指定的 Tab"""
        self.logger.info(f"开始点击 Tab: {tab_name}")

        with allure.step(f"点击 Tab: {tab_name}"):
            try:
                self.logger.debug(f"定位 Tab: {tab_name}")
                tab = self.page.get_by_role("tab", name=tab_name)
                await tab.click()
                self.logger.info(f"Tab 已点击: {tab_name}")

                # 等待页面响应
                await self.page.wait_for_timeout(500)
                self.logger.debug(f"Tab 加载完成: {tab_name}")

            except Exception as e:
                error_msg = f"点击 Tab 失败: {str(e)}"
                self.logger.error(error_msg)
                raise

    async def has_save_button(self) -> bool:
        """检查当前 Tab 是否有 Save 按钮"""
        self.logger.info("检查当前 Tab 是否有 Save 按钮")

        try:
            save_button = self.page.get_by_role("button", name=self.SAVE_BUTTON_NAME)
            # 等待 100ms 以确保元素加载
            await self.page.wait_for_timeout(100)
            is_visible = await save_button.is_visible()
            self.logger.debug(f"Save 按钮可见状态: {is_visible}")
            return is_visible
        except Exception as e:
            self.logger.debug(f"检查 Save 按钮失败: {str(e)}")
            return False

    async def click_save_button(self) -> None:
        """点击 Save 按钮"""
        self.logger.info("开始点击 Save 按钮")

        with allure.step("点击 Save 按钮"):
            try:
                save_btn = self.page.get_by_role("button", name=self.SAVE_BUTTON_NAME)
                await save_btn.click()
                self.logger.info("Save 按钮已点击")

                # 等待页面响应 - 给服务器充足的响应时间
                await self.page.wait_for_timeout(3000)

            except Exception as e:
                error_msg = f"点击 Save 按钮失败: {str(e)}"
                self.logger.error(error_msg)
                raise

    async def verify_save_success(self) -> bool:
        """验证保存成功（检查成功提示信息）"""
        self.logger.info("开始验证保存成功")

        with allure.step("验证保存成功提示"):
            try:
                # 增加等待时间确保成功提示出现 - 使用重试逻辑
                max_retries = 3
                retry_count = 0
                is_visible = False
                success_msg = ""

                while retry_count < max_retries and not is_visible:
                    try:
                        self.logger.debug(f"[尝试 {retry_count + 1}/{max_retries}] 等待成功提示: {self.SUCCESS_MESSAGE_SELECTOR}")

                        # 等待成功提示出现（使用更长的超时时间）
                        await self.wait_helper.wait_for_selector(
                            self.page,
                            self.SUCCESS_MESSAGE_SELECTOR,
                            timeout=timeout_config.get_element_timeout()
                        )

                        # 验证提示是否可见
                        is_visible = await self.page.locator(self.SUCCESS_MESSAGE_SELECTOR).is_visible()

                        if is_visible:
                            # 获取提示文本
                            success_msg = await self.page.locator(self.SUCCESS_MESSAGE_SELECTOR).text_content()
                            self.logger.info(f"成功提示已出现: {success_msg}")
                            break

                    except Exception as e:
                        retry_count += 1
                        if retry_count < max_retries:
                            self.logger.debug(f"尝试 {retry_count} 失败，等待后重试: {str(e)}")
                            await self.page.wait_for_timeout(500)
                        else:
                            self.logger.error(f"经过 {max_retries} 次尝试仍未找到成功提示: {str(e)}")

                allure.attach(f"成功提示: {success_msg}\n可见: {is_visible}\n重试次数: {retry_count}", "验证结果")
                self.logger.info(f"保存成功验证完成: {is_visible}")
                return is_visible

            except Exception as e:
                error_msg = f"验证保存成功失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "验证错误")
                return False

    async def handle_previous_step(self) -> None:
        """处理 Previous step 按钮（用于没有 Save 按钮的 Tab）"""
        self.logger.info("检查是否有 Previous step 按钮")

        try:
            prev_btn = self.page.get_by_role("button", name=self.PREVIOUS_STEP_BUTTON_NAME)
            is_visible = await prev_btn.is_visible()

            if is_visible:
                self.logger.info("Previous step 按钮可见，点击返回")
                await prev_btn.click()
                await self.page.wait_for_timeout(300)
                self.logger.info("[OK] 已点击 Previous step 按钮")
            else:
                self.logger.debug("Previous step 按钮不可见，跳过")

        except Exception as e:
            self.logger.debug(f"处理 Previous step 按钮失败: {str(e)}")

    # ========== 项目启动相关方法 ==========
    async def search_project_by_keyword(self, project_name: str) -> None:
        """搜索项目（通用方法，用于 Started/Not Started Tab）"""
        self.logger.info(f"开始搜索项目: {project_name}")

        with allure.step(f"搜索项目: {project_name}"):
            try:
                # Step 1: 点击 Project 搜索框
                self.logger.debug("定位 Project 搜索框")
                project_filter = self.page.locator("div").filter(
                    has_text=re.compile(self.PROJECT_SEARCH_FILTER_PATTERN)
                ).nth(self.PROJECT_SEARCH_FILTER_NTH)
                await project_filter.click()
                self.logger.info("Project 搜索框已点击")

                # Step 2: 等待并输入项目名称
                await self.page.wait_for_timeout(300)
                self.logger.debug(f"输入项目名称: {project_name}")
                search_input = project_filter.locator("input.el-input__inner")
                await search_input.clear()
                await search_input.fill(project_name)
                await self.page.wait_for_timeout(200)
                self.logger.info(f"项目名称已输入: {project_name}")

                # Step 3: 点击搜索按钮
                self.logger.debug("点击搜索按钮")
                search_btn = self.page.locator(self.SEARCH_BUTTON_SELECTOR)
                await search_btn.click()
                self.logger.info("搜索按钮已点击")

                # Step 4: 等待搜索结果加载
                await self.page.wait_for_load_state("networkidle")
                allure.attach(f"搜索项目: {project_name}", "搜索操作")
                self.logger.info("[OK] 项目搜索完成")

            except Exception as e:
                error_msg = f"搜索项目失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "搜索错误")
                raise

    async def click_start_button(self) -> None:
        """点击第一个 Start 按钮"""
        self.logger.info("开始点击 Start 按钮")

        with allure.step("点击 Start 按钮"):
            try:
                # 使用 locator + filter 精确定位 Start 按钮
                self.logger.debug(f"定位 {self.START_BUTTON_TEXT} 按钮")
                await self.page.locator("div").filter(
                    has_text=re.compile(r"^Start$")
                ).click()
                self.logger.info("Start 按钮已点击")

                # 等待弹窗出现
                await self.page.wait_for_timeout(500)
                allure.attach("Start 按钮已点击，等待确认弹窗", "操作结果")
                self.logger.info("Start 按钮点击完成")

            except Exception as e:
                error_msg = f"点击 Start 按钮失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "点击错误")
                raise

    async def verify_start_confirmation_popup_visible(self) -> bool:
        """验证 Start 确认弹窗（Yes 按钮）是否可见"""
        self.logger.info("开始验证 Start 确认弹窗")

        with allure.step("验证 Yes 确认按钮是否可见"):
            try:
                # 查找 Yes 按钮
                self.logger.debug(f"定位 {self.YES_CONFIRMATION_BUTTON_TEXT} 按钮")
                yes_btn = self.page.get_by_text(self.YES_CONFIRMATION_BUTTON_TEXT, exact=True)

                # 等待元素加载
                await yes_btn.wait_for(timeout=timeout_config.get_element_timeout())
                self.logger.info("Yes 按钮已定位")

                # 检查是否可见
                is_visible = await yes_btn.is_visible()
                self.logger.info(f"Yes 按钮可见: {is_visible}")

                allure.attach(f"Yes 确认按钮可见: {is_visible}", "弹窗验证结果")
                return is_visible

            except Exception as e:
                error_msg = f"验证 Start 确认弹窗失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "验证错误")
                return False

    # ========== 完整流程方法 ==========
    async def test_all_tabs_save_functionality(self) -> dict:
        """
        测试所有 Tab 的保存功能

        Returns:
            dict: 测试结果统计 {
                "total_tabs": int,
                "tabs_with_save": int,
                "tabs_without_save": int,
                "save_success_count": int,
                "save_failure_count": int,
                "details": list
            }
        """
        self.logger.info("开始测试所有 Tab 的保存功能")

        with allure.step("遍历所有 Tab 进行保存功能测试"):
            results = {
                "total_tabs": len(self.TAB_NAMES),
                "tabs_with_save": 0,
                "tabs_without_save": 0,
                "save_success_count": 0,
                "save_failure_count": 0,
                "details": []
            }

            for tab_name in self.TAB_NAMES:
                self.logger.info(f"--- 处理 Tab: {tab_name} ---")

                try:
                    # Step 1: 点击 Tab
                    await self.click_tab(tab_name)

                    # Step 2: 检查是否有 Save 按钮
                    has_save = await self.has_save_button()

                    if has_save:
                        results["tabs_with_save"] += 1
                        self.logger.info(f"[OK] {tab_name} 有 Save 按钮，开始点击保存")

                        with allure.step(f"Tab: {tab_name} - 点击 Save 并验证成功"):
                            try:
                                # 点击 Save
                                await self.click_save_button()

                                # 验证成功提示
                                success = await self.verify_save_success()

                                if success:
                                    results["save_success_count"] += 1
                                    results["details"].append({
                                        "tab_name": tab_name,
                                        "has_save": True,
                                        "save_result": "SUCCESS",
                                        "message": "保存成功，成功提示已显示"
                                    })
                                    self.logger.info(f"[OK] {tab_name} 保存成功")
                                else:
                                    results["save_failure_count"] += 1
                                    results["details"].append({
                                        "tab_name": tab_name,
                                        "has_save": True,
                                        "save_result": "FAILED",
                                        "message": "保存失败，成功提示未显示"
                                    })
                                    self.logger.error(f"[FAIL] {tab_name} 保存失败，成功提示未出现")

                            except Exception as e:
                                results["save_failure_count"] += 1
                                results["details"].append({
                                    "tab_name": tab_name,
                                    "has_save": True,
                                    "save_result": "ERROR",
                                    "message": f"保存过程出错: {str(e)}"
                                })
                                self.logger.error(f"[FAIL] {tab_name} 保存过程出错: {str(e)}")

                    else:
                        results["tabs_without_save"] += 1
                        self.logger.info(f"[INFO] {tab_name} 无 Save 按钮，处理 Previous step")

                        with allure.step(f"Tab: {tab_name} - 无 Save 按钮，处理 Previous step"):
                            try:
                                # 处理 Previous step
                                await self.handle_previous_step()

                                results["details"].append({
                                    "tab_name": tab_name,
                                    "has_save": False,
                                    "save_result": "NO_SAVE_BUTTON",
                                    "message": "无 Save 按钮，正常跳过"
                                })
                                self.logger.info(f"[OK] {tab_name} 正常处理（无 Save 按钮）")

                            except Exception as e:
                                results["details"].append({
                                    "tab_name": tab_name,
                                    "has_save": False,
                                    "save_result": "ERROR",
                                    "message": f"处理过程出错: {str(e)}"
                                })
                                self.logger.error(f"[FAIL] {tab_name} 处理过程出错: {str(e)}")

                except Exception as e:
                    results["details"].append({
                        "tab_name": tab_name,
                        "has_save": None,
                        "save_result": "ERROR",
                        "message": f"Tab 切换或检查出错: {str(e)}"
                    })
                    self.logger.error(f"[FAIL] {tab_name} 处理失败: {str(e)}")

                # 等待一段时间，避免操作过快
                await self.page.wait_for_timeout(300)

            # 生成测试汇总报告
            summary = f"""
            测试汇总:
            - 总 Tab 数: {results['total_tabs']}
            - 有 Save 按钮的 Tab: {results['tabs_with_save']}
            - 无 Save 按钮的 Tab: {results['tabs_without_save']}
            - 保存成功: {results['save_success_count']}
            - 保存失败: {results['save_failure_count']}
            
            详细结果:
            """
            for detail in results["details"]:
                summary += f"\n- {detail['tab_name']}: {detail['save_result']} ({detail['message']})"

            allure.attach(summary, "测试汇总报告", allure.attachment_type.TEXT)
            self.logger.info(summary)

            return results
