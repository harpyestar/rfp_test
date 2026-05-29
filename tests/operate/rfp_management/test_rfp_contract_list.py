"""
签约项目列表页测试模块
测试签约列表页的菜单导航、默认Tab展示和Tab切换功能
"""

import allure
import pytest
from pages.operate.rfp_management.rfp_contract_list_page import RFPContractListPage
from utils.config import config
from utils.logger import get_logger

logger = get_logger("tests.operate.rfp_management.test_rfp_contract_list", config.log_level)


@allure.feature("RFP 项目管理")
@allure.story("签约项目列表页")
@pytest.mark.operate
@pytest.mark.regression
class TestRFPContractList:
    """签约项目列表页测试"""

    @allure.title("验证从菜单进入签约页面")
    @allure.description("""
    测试: Operate 角色从侧边栏菜单导航至签约项目列表页。

    测试流程:
    1. 进入 /home 页面
    2. 点击侧边栏「签约管理」菜单展开子菜单
    3. 点击子菜单「签约」
    4. 验证页面Tab栏显示三个选项

    预期结果:
    - 「签约管理」菜单可点击展开
    - 点击「签约」后进入签约项目列表页
    - Tab栏显示「未启动」「已启动」「已完成」
    """)
    @pytest.mark.asyncio
    async def test_navigate_to_contracting_from_menu(self, page_module, operate_user):
        """SIGN-LIST-001: 从菜单进入签约页面"""
        logger.info("Starting SIGN-LIST-001: 从菜单进入签约页面")
        contract_list_page = RFPContractListPage(page_module)

        with allure.step("【步骤 1】进入 /home 页面"):
            await contract_list_page.navigate_to_home()

        with allure.step("【步骤 2】通过菜单进入签约页面"):
            await contract_list_page.navigate_to_contracting()

        with allure.step("【步骤 3】验证三个 Tab 可见"):
            tabs_visible = await contract_list_page.verify_tabs_visible()
            assert tabs_visible, "签约页面未显示三个 Tab（未启动、已启动、已完成）"

    @allure.title("验证默认展示未启动项目")
    @allure.description("""
    测试: 进入签约项目列表页后，验证操作列按钮显示正确。

    测试流程:
    1. 进入签约项目列表页
    2. 验证操作列存在按钮：启动、修改项目、作废

    预期结果:
    - 列表操作列显示启动、修改项目、作废按钮
    """)
    @pytest.mark.asyncio
    async def test_default_show_unstarted_projects(self, page_module, operate_user):
        """SIGN-LIST-003: 默认展示未启动项目"""
        logger.info("Starting SIGN-LIST-003: 默认展示未启动项目")
        contract_list_page = RFPContractListPage(page_module)

        with allure.step("【步骤 1】进入签约项目列表页"):
            await contract_list_page.navigate_to_home()
            await contract_list_page.navigate_to_contracting()
        with allure.step("【步骤 2】验证操作列按钮存在"):
            buttons_ok = await contract_list_page.verify_unstarted_action_buttons()
            assert buttons_ok, "未启动Tab操作列按钮不完整（启动、修改项目、作废）"

    @allure.title("验证切换到已完成Tab")
    @allure.description("""
    测试: 在签约项目列表页中切换到已完成Tab，验证操作按钮。

    测试流程:
    1. 进入签约项目列表页
    2. 点击「已完成」Tab
    3. 验证操作列正确显示按钮

    预期结果:
    - 操作列显示：签约详情、项目详情、导出报价、履约情况
    """)
    @pytest.mark.asyncio
    async def test_switch_to_completed_tab(self, page_module, operate_user):
        """SIGN-LIST-005: 切换到已完成Tab"""
        logger.info("Starting SIGN-LIST-005: 切换到已完成Tab")
        contract_list_page = RFPContractListPage(page_module)

        with allure.step("【步骤 1】进入签约项目列表页"):
            await contract_list_page.navigate_to_home()
            await contract_list_page.navigate_to_contracting()

        with allure.step("【步骤 2】点击「已完成」Tab"):
            await contract_list_page.click_completed_tab()

        with allure.step("【步骤 3】验证操作列按钮"):
            buttons_ok = await contract_list_page.verify_completed_action_buttons()
            assert buttons_ok, "已完成Tab操作列按钮不完整（签约详情、项目详情、导出报价、履约情况）"

