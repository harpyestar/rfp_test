"""
编辑 RFP 项目页面对象模型
负责 RFP 项目编辑流程中的 Tab 切换、保存验证等交互操作
所有超时值从 timeout_config 中读取，所有选择器统一在类变量中定义
"""

import re
import allure
from playwright.async_api import Page, Download
from pages.common.base_page import BasePage
from utils.config import config
from utils.timeout_config import timeout_config
from utils.logger import get_logger


class EditRFPProjectPage(BasePage):
    """编辑 RFP 项目 Page Object"""

    # ========== 导航菜单元素 ==========
    RFP_MANAGEMENT_MENU_TEXT = "签约管理"
    CONTRACTING_MENU_TEXT = "签约"
    MODIFY_PROJECT_BUTTON_TEXT = "修改项目"

    # ========== Contracting 页面元素 ==========
    NOT_STARTED_TAB_NAME = "^未启动$"
    STARTED_TAB_NAME = "^已启动$"
    PROJECT_SEARCH_LABEL_TEXT = "签约项目"
    SEARCH_BUTTON_SELECTOR = ".ml-15 > div"

    # ========== 项目操作按钮 ==========
    START_BUTTON_TEXT = "启动"
    CONFIRM_BUTTON_TEXT = "确定"
    CANCEL_BUTTON_TEXT = "取消"

    # ========== 项目操作 - 修改按钮 ==========
    MODIFY_BUTTON_TEXT = "修改"

    # ========== 邀请酒店 Tab 元素 ==========
    INVITE_HOTEL_TAB_NAME = "邀请酒店"
    EXPORT_BUTTON_TEXT = "^导出$"
    ADD_GROUP_INTENT_HOTEL_TEXT = "添加酒店集团意向单店"

    # ========== URL 项目 ID 提取 ==========
    PROJECT_ID_PATTERN = re.compile(r'projectId=(\d+)')

    # ========== 编辑页面 Tab 元素 ==========
    SAVE_BUTTON_NAME = "保存"
    COMPLETE_BUTTON_NAME = "完成"
    SUCCESS_MESSAGE_SELECTOR = ".c-notify-content-description"

    # ========== Tab 列表 ==========
    # 从需求中的 Playwright 录制代码提取的所有 Tab 名称（中文）
    TAB_NAMES = [
        "签约基本信息",
        "项目介绍",
        "签约项目POI",
        "邀请酒店",
        "自定义采购策略",
        "项目采购策略",
        "权重设置",
        "历史交易数据",
        "智能推荐",
        "酒店白名单",
        "Lanyon显示设置",
        "补充履约监控名单",
        "酒店违规配置",
    ]

    def __init__(self, page: Page):
        super().__init__(page)
        self.logger = get_logger(self.__class__.__name__, config.log_level)

    # ========== 导航方法 ==========
    async def navigate_to_contracting(self) -> None:
        """导航至 签约管理 > 签约 页面"""
        self.logger.info("开始导航至签约管理 > 签约页面")

        with allure.step("导航至签约管理 > 签约页面"):
            try:
                # Step 1: 点击 签约管理 菜单
                self.logger.debug(f"点击 {self.RFP_MANAGEMENT_MENU_TEXT} 菜单")
                rfp_menu = self.page.get_by_text(self.RFP_MANAGEMENT_MENU_TEXT)
                await rfp_menu.click()
                self.logger.info(f"{self.RFP_MANAGEMENT_MENU_TEXT} 菜单已点击")

                # Step 2: 等待下拉菜单
                await self.page.wait_for_timeout(300)

                # Step 3: 点击 签约 菜单项
                self.logger.debug(f"点击 {self.CONTRACTING_MENU_TEXT} 菜单项")
                contracting_menu = self.page.get_by_text(self.CONTRACTING_MENU_TEXT, exact=True)
                await contracting_menu.click()
                self.logger.info(f"{self.CONTRACTING_MENU_TEXT} 菜单项已点击")

                # Step 4: 等待页面加载
                await self.page.wait_for_load_state("networkidle")
                allure.attach("签约页面已加载", "导航结果")
                self.logger.info("[OK] 签约页面加载完成")

            except Exception as e:
                error_msg = f"导航至签约页面失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "导航错误")
                raise

    async def click_not_started_tab(self) -> None:
        """点击 未启动 Tab"""
        self.logger.info("开始点击 未启动 Tab")

        with allure.step(f"选择 {self.NOT_STARTED_TAB_NAME} Tab"):
            try:
                # 点击 未启动 Tab
                self.logger.debug(f"定位 {self.NOT_STARTED_TAB_NAME} Tab")
                not_started_tab = self.page.locator("div").filter(
                    has_text=re.compile(self.NOT_STARTED_TAB_NAME)
                ).first
                await not_started_tab.wait_for(timeout=timeout_config.get_element_timeout())
                await not_started_tab.click()
                await self.page.wait_for_timeout(300)
                self.logger.info("[OK] 未启动 Tab 已点击")
            except Exception as e:
                error_msg = f"点击 未启动 Tab 失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "Tab 错误")
                raise

    async def click_started_tab(self) -> None:
        """点击已启动 Tab"""
        self.logger.info("开始点击已启动 Tab")

        with allure.step(f"选择 {self.STARTED_TAB_NAME} Tab"):
            try:
                started_tab = self.page.locator("div").filter(
                    has_text=re.compile(self.STARTED_TAB_NAME)
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

    async def search_and_open_project(self, project_name: str) -> None:
        """搜索签约项目并打开编辑页面"""
        self.logger.info(f"开始搜索项目: {project_name}")

        with allure.step(f"搜索项目: {project_name}"):
            try:
                # Step 1: 点击 label 聚焦搜索框
                self.logger.debug(f"定位搜索框 label: {self.PROJECT_SEARCH_LABEL_TEXT}")
                project_filter = self.page.locator("label").filter(
                    has_text=self.PROJECT_SEARCH_LABEL_TEXT
                ).first
                await project_filter.wait_for(timeout=timeout_config.get_element_timeout())
                await project_filter.click()
                self.logger.info("搜索框已聚焦")

                # Step 2: 输入项目名称
                self.logger.debug(f"输入项目名称: {project_name}")
                project_input = self.page.get_by_label(self.PROJECT_SEARCH_LABEL_TEXT)
                await project_input.wait_for(timeout=timeout_config.get_element_timeout())
                await project_input.fill(project_name)
                await self.page.wait_for_timeout(200)
                self.logger.info(f"项目名称已输入: {project_name}")

                # Step 3: 点击搜索按钮
                self.logger.debug("点击搜索按钮")
                search_button = self.page.locator(self.SEARCH_BUTTON_SELECTOR).first
                await search_button.wait_for(timeout=timeout_config.get_element_timeout())
                await search_button.click()

                # Step 4: 等待搜索结果加载
                await self.page.wait_for_load_state("networkidle")
                allure.attach(f"搜索项目: {project_name}", "搜索操作")
                self.logger.info("[OK] 项目搜索完成")

                # Step 5: 点击 修改项目 按钮（第一个）
                self.logger.debug(f"定位并点击 {self.MODIFY_PROJECT_BUTTON_TEXT} 按钮（首个）")
                modify_buttons = self.page.get_by_text(self.MODIFY_PROJECT_BUTTON_TEXT)
                await modify_buttons.first.wait_for(timeout=timeout_config.get_element_timeout())
                await modify_buttons.first.click()
                self.logger.info(f"{self.MODIFY_PROJECT_BUTTON_TEXT} 按钮已点击")

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
        """检查当前 Tab 是否有保存按钮"""
        self.logger.info("检查当前 Tab 是否有保存按钮")

        try:
            save_button = self.page.get_by_text(self.SAVE_BUTTON_NAME)
            # 等待 100ms 以确保元素加载
            await self.page.wait_for_timeout(100)
            is_visible = await save_button.is_visible()
            self.logger.debug(f"保存按钮可见状态: {is_visible}")
            return is_visible
        except Exception as e:
            self.logger.debug(f"检查保存按钮失败: {str(e)}")
            return False

    async def click_save_button(self) -> None:
        """点击保存按钮"""
        self.logger.info("开始点击保存按钮")

        with allure.step("点击保存按钮"):
            try:
                save_btn = self.page.get_by_text(self.SAVE_BUTTON_NAME)
                await save_btn.click()
                self.logger.info("保存按钮已点击")

                # 等待页面响应 - 给服务器充足的响应时间
                await self.page.wait_for_timeout(3000)

            except Exception as e:
                error_msg = f"点击保存按钮失败: {str(e)}"
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

    async def handle_complete_or_skip(self) -> None:
        """处理无保存按钮的 Tab：点击完成按钮或直接跳过"""
        self.logger.info("检查是否有完成按钮")

        try:
            complete_btn = self.page.get_by_role("button", name=self.COMPLETE_BUTTON_NAME)
            is_visible = await complete_btn.is_visible()

            if is_visible:
                self.logger.info("完成按钮可见，点击跳过")
                await complete_btn.click()
                await self.page.wait_for_timeout(500)
                self.logger.info("[OK] 已点击完成按钮")
            else:
                self.logger.debug("完成按钮不可见，直接跳过")

        except Exception as e:
            self.logger.debug(f"处理完成按钮失败: {str(e)}，直接跳过")

    # ========== 项目启动相关方法 ==========
    async def search_project_by_keyword(self, project_name: str) -> None:
        """搜索签约项目"""
        self.logger.info(f"开始搜索项目: {project_name}")

        with allure.step(f"搜索项目: {project_name}"):
            try:
                # Step 1: 点击 label 聚焦搜索框
                self.logger.debug(f"定位搜索框 label: {self.PROJECT_SEARCH_LABEL_TEXT}")
                project_filter = self.page.locator("label").filter(
                    has_text=self.PROJECT_SEARCH_LABEL_TEXT
                ).first
                await project_filter.wait_for(timeout=timeout_config.get_element_timeout())
                await project_filter.click()
                self.logger.info("搜索框已聚焦")

                # Step 2: 输入项目名称
                self.logger.debug(f"输入项目名称: {project_name}")
                project_input = self.page.get_by_label(self.PROJECT_SEARCH_LABEL_TEXT)
                await project_input.wait_for(timeout=timeout_config.get_element_timeout())
                await project_input.fill(project_name)
                await self.page.wait_for_timeout(200)
                self.logger.info(f"项目名称已输入: {project_name}")

                # Step 3: 点击搜索按钮
                self.logger.debug("点击搜索按钮")
                search_button = self.page.locator(self.SEARCH_BUTTON_SELECTOR).first
                await search_button.wait_for(timeout=timeout_config.get_element_timeout())
                await search_button.click()

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
        """点击第一个 启动 按钮"""
        self.logger.info("开始点击 启动 按钮")

        with allure.step("点击 启动 按钮"):
            try:
                self.logger.debug(f"定位 {self.START_BUTTON_TEXT} 按钮")
                await self.page.get_by_text(self.START_BUTTON_TEXT, exact=True).click()
                self.logger.info("启动按钮已点击")

                # 等待弹窗出现
                await self.page.wait_for_timeout(500)
                allure.attach("启动按钮已点击，等待确认弹窗", "操作结果")
                self.logger.info("启动按钮点击完成")

            except Exception as e:
                error_msg = f"点击启动按钮失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "点击错误")
                raise

    async def verify_confirmation_dialog_visible(self) -> bool:
        """验证启动确认弹窗（确定按钮）是否可见"""
        self.logger.info("开始验证启动确认弹窗")

        with allure.step("验证 确定 确认按钮是否可见"):
            try:
                self.logger.debug(f"定位 {self.CONFIRM_BUTTON_TEXT} 按钮")
                confirm_btn = self.page.get_by_text(self.CONFIRM_BUTTON_TEXT, exact=True)

                # 等待元素加载
                await confirm_btn.wait_for(timeout=timeout_config.get_element_timeout())
                self.logger.info("确定按钮已定位")

                # 检查是否可见
                is_visible = await confirm_btn.is_visible()
                self.logger.info(f"确定按钮可见: {is_visible}")

                allure.attach(f"确定确认按钮可见: {is_visible}", "弹窗验证结果")
                return is_visible

            except Exception as e:
                error_msg = f"验证启动确认弹窗失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "验证错误")
                return False

    async def click_cancel_button(self) -> None:
        """点击 取消 按钮关闭确认弹窗"""
        self.logger.info("开始点击 取消 按钮")

        with allure.step("点击 取消 按钮关闭弹窗"):
            try:
                cancel_btn = self.page.get_by_text(self.CANCEL_BUTTON_TEXT, exact=True)
                await cancel_btn.wait_for(timeout=timeout_config.get_element_timeout())
                await cancel_btn.click()
                await self.page.wait_for_timeout(300)
                self.logger.info("[OK] 已点击取消按钮，弹窗已关闭")
            except Exception as e:
                error_msg = f"点击取消按钮失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "取消按钮错误")
                raise

    # ========== 酒店导出相关方法 ==========
    async def search_and_click_modify(self, project_name: str) -> None:
        """
        在已启动 Tab 中搜索项目并点击 修改 按钮进入编辑页

        Args:
            project_name: 项目名称
        """
        self.logger.info(f"开始搜索项目并点击修改: {project_name}")

        with allure.step(f"搜索项目并点击修改: {project_name}"):
            try:
                # Step 1: 点击 label 聚焦搜索框
                self.logger.debug(f"定位搜索框 label: {self.PROJECT_SEARCH_LABEL_TEXT}")
                project_filter = self.page.locator("label").filter(
                    has_text=self.PROJECT_SEARCH_LABEL_TEXT
                ).first
                await project_filter.wait_for(timeout=timeout_config.get_element_timeout())
                await project_filter.click()
                self.logger.info("搜索框已聚焦")

                # Step 2: 输入项目名称
                self.logger.debug(f"输入项目名称: {project_name}")
                project_input = self.page.get_by_label(self.PROJECT_SEARCH_LABEL_TEXT)
                await project_input.wait_for(timeout=timeout_config.get_element_timeout())
                await project_input.fill(project_name)
                await self.page.wait_for_timeout(200)
                self.logger.info(f"项目名称已输入: {project_name}")

                # Step 3: 点击搜索按钮
                self.logger.debug("点击搜索按钮")
                search_button = self.page.locator(self.SEARCH_BUTTON_SELECTOR).first
                await search_button.wait_for(timeout=timeout_config.get_element_timeout())
                await search_button.click()

                # Step 4: 等待搜索结果加载
                await self.page.wait_for_load_state("networkidle")
                allure.attach(f"搜索项目: {project_name}", "搜索操作")
                self.logger.info("[OK] 项目搜索完成")

                # Step 5: 点击 修改 按钮（可能存在多个，取首个匹配项）
                # 注释说明：在已启动 Tab 中，"修改" 按钮位于表格操作栏
                self.logger.debug(f"定位并点击 {self.MODIFY_BUTTON_TEXT} 按钮")
                modify_button = self.page.get_by_text(self.MODIFY_BUTTON_TEXT, exact=True).first
                await modify_button.wait_for(timeout=timeout_config.get_element_timeout())
                await modify_button.click()
                self.logger.info(f"{self.MODIFY_BUTTON_TEXT} 按钮已点击")

                # Step 6: 等待编辑页面加载
                await self.page.wait_for_load_state("networkidle")
                allure.attach("已进入项目编辑页面", "进入编辑页")
                self.logger.info("[OK] 项目编辑页面加载完成")

            except Exception as e:
                error_msg = f"搜索项目或点击修改失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "搜索/修改错误")
                raise

    async def get_project_id_from_url(self) -> str:
        """
        从编辑页面 URL 中提取项目 ID

        Returns:
            str: 项目 ID
        """
        url = self.page.url
        self.logger.info(f"当前编辑页 URL: {url}")

        match = self.PROJECT_ID_PATTERN.search(url)
        if match:
            project_id = match.group(1)
            self.logger.info(f"提取到项目 ID: {project_id}")
            allure.attach(f"项目 ID: {project_id}", "项目 ID")
            return project_id
        else:
            error_msg = f"无法从 URL 中提取项目 ID: {url}"
            self.logger.error(error_msg)
            allure.attach(error_msg, "URL 解析错误")
            raise ValueError(error_msg)

    async def export_normal_hotel_list(self) -> Download:
        """
        在 邀请酒店 Tab 中点击 导出 按钮（普通酒店名单）

        Returns:
            Download: Playwright Download 对象
        """
        self.logger.info("开始导出普通酒店名单")

        with allure.step("导出普通酒店名单"):
            try:
                async with self.page.expect_download() as download_info:
                    export_btn = self.page.locator("div").filter(
                        has_text=re.compile(self.EXPORT_BUTTON_TEXT)
                    ).nth(1)
                    await export_btn.wait_for(timeout=timeout_config.get_element_timeout())
                    await export_btn.click()

                download = await download_info.value
                self.logger.info(f"普通酒店名单导出完成: {download.suggested_filename}")
                allure.attach(f"导出文件名: {download.suggested_filename}", "导出文件")
                return download

            except Exception as e:
                error_msg = f"导出普通酒店名单失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "导出错误")
                raise

    async def click_add_group_intent_hotel_button(self) -> None:
        """点击 添加酒店集团意向单店 按钮"""
        self.logger.info("开始点击添加酒店集团意向单店按钮")

        with allure.step("点击添加酒店集团意向单店"):
            try:
                add_btn = self.page.get_by_text(self.ADD_GROUP_INTENT_HOTEL_TEXT)
                await add_btn.wait_for(timeout=timeout_config.get_element_timeout())
                await add_btn.click()
                await self.page.wait_for_timeout(500)
                self.logger.info("[OK] 已点击添加酒店集团意向单店按钮")
            except Exception as e:
                error_msg = f"点击添加酒店集团意向单店按钮失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "点击错误")
                raise

    async def export_group_hotel_list(self) -> Download:
        """
        点击 添加酒店集团意向单店 后，在展开的区域中点击 导出 按钮（集团酒店名单）

        注意：与普通导出同为 nth(1)，因为 DOM 中始终有两个「导出」按钮：
              nth(0) = 集团区域（初始可能隐藏），nth(1) = 普通区域。
              点击「添加酒店集团意向单店」后集团区域展开，nth(1) 对应集团导出。

        Returns:
            Download: Playwright Download 对象
        """
        self.logger.info("开始导出集团酒店名单")

        with allure.step("导出集团酒店名单"):
            try:
                # 等待集团区域加载
                await self.page.wait_for_timeout(1000)

                async with self.page.expect_download() as download_info:
                    export_btn = self.page.locator("div").filter(
                        has_text=re.compile(self.EXPORT_BUTTON_TEXT)
                    ).nth(1)
                    await export_btn.wait_for(timeout=timeout_config.get_element_timeout())
                    await export_btn.click()

                download = await download_info.value
                self.logger.info(f"集团酒店名单导出完成: {download.suggested_filename}")
                allure.attach(f"导出文件名: {download.suggested_filename}", "导出文件")
                return download

            except Exception as e:
                error_msg = f"导出集团酒店名单失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "导出错误")
                raise

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

                    # Step 2: 检查是否有保存按钮
                    has_save = await self.has_save_button()

                    if has_save:
                        results["tabs_with_save"] += 1
                        self.logger.info(f"[OK] {tab_name} 有保存按钮，开始点击保存")

                        with allure.step(f"Tab: {tab_name} - 点击保存并验证成功"):
                            try:
                                # 点击保存
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
                        self.logger.info(f"[INFO] {tab_name} 无保存按钮，点击完成跳过")

                        with allure.step(f"Tab: {tab_name} - 无保存按钮，点击完成跳过"):
                            try:
                                # 点击完成或跳过
                                await self.handle_complete_or_skip()

                                results["details"].append({
                                    "tab_name": tab_name,
                                    "has_save": False,
                                    "save_result": "NO_SAVE_BUTTON",
                                    "message": "无保存按钮，正常跳过"
                                })
                                self.logger.info(f"[OK] {tab_name} 正常处理（无保存按钮）")

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
            - 有保存按钮的 Tab: {results['tabs_with_save']}
            - 无保存按钮的 Tab: {results['tabs_without_save']}
            - 保存成功: {results['save_success_count']}
            - 保存失败: {results['save_failure_count']}

            详细结果:
            """
            for detail in results["details"]:
                summary += f"\n- {detail['tab_name']}: {detail['save_result']} ({detail['message']})"

            allure.attach(summary, "测试汇总报告", allure.attachment_type.TEXT)
            self.logger.info(summary)

            return results
