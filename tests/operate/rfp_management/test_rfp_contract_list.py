"""
签约项目列表页测试模块
测试签约列表页的菜单导航、默认Tab展示和Tab切换功能
"""

import allure
import pytest
from pages.operate.rfp_management.rfp_contract_list_page import RFPContractListPage
from utils.config import config
from utils.logger import get_logger
from utils.test_data_loader import TestDataLoader

logger = get_logger("tests.operate.rfp_management.test_rfp_contract_list", config.log_level)

CONTRACT_FILTER_CASES = TestDataLoader.load_params(
    "rfp_management_params.json",
    "contract_list_filter",
)


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

    @allure.title("验证切换Tab后筛选条件保持: {case_data[description]}")
    @allure.description("""
    测试: 在未启动Tab下筛选项目后切换到已启动Tab，验证筛选条件不会清空。

    测试流程:
    1. 进入签约项目列表页
    2. 在签约项目输入框输入项目名称并搜索
    3. 切换到已启动Tab
    4. 验证筛选框仍保留输入的关键词
    """)
    @pytest.mark.parametrize("case_data", [c for c in CONTRACT_FILTER_CASES if c["case_id"] == "contract_filter_001"])
    @pytest.mark.asyncio
    async def test_filter_persists_after_tab_switch(self, page_module, operate_user, case_data):
        """SIGN-LIST-006: 切换Tab后筛选条件保持"""
        logger.info("Starting SIGN-LIST-006: 切换Tab后筛选条件保持")
        contract_list_page = RFPContractListPage(page_module)

        with allure.step("【步骤 1】进入签约项目列表页"):
            await contract_list_page.navigate_to_home()
            await contract_list_page.navigate_to_contracting()

        with allure.step(f"【步骤 2】筛选签约项目: {case_data['project_name']}"):
            await contract_list_page.search_by_project_name(case_data["project_name"])

        with allure.step("【步骤 3】切换到已启动 Tab"):
            await contract_list_page.click_started_tab()

        with allure.step("【步骤 4】验证筛选条件仍保留"):
            filter_value = await contract_list_page.get_project_filter_value()
            assert case_data["project_name"] in filter_value, \
                f"切换Tab后筛选条件丢失，当前值: '{filter_value}'，期望包含: '{case_data['project_name']}'"

    @allure.title("验证按机构名筛选: {case_data[description]}")
    @allure.description("""
    测试: 在签约项目列表页按机构名筛选，验证结果列表匹配。

    测试流程:
    1. 进入签约项目列表页
    2. 在机构名输入框输入并选择机构
    3. 点击搜索
    4. 验证列表不为空
    """)
    @pytest.mark.parametrize("case_data", [c for c in CONTRACT_FILTER_CASES if c["case_id"] == "contract_filter_002"])
    @pytest.mark.asyncio
    async def test_filter_by_org_name(self, page_module, operate_user, case_data):
        """SIGN-LIST-007: 按机构名筛选"""
        logger.info("Starting SIGN-LIST-007: 按机构名筛选")
        contract_list_page = RFPContractListPage(page_module)

        with allure.step("【步骤 1】进入签约项目列表页"):
            await contract_list_page.navigate_to_home()
            await contract_list_page.navigate_to_contracting()

        with allure.step(f"【步骤 2】按机构名筛选: {case_data['org_name']}"):
            await contract_list_page.search_by_org_name(case_data["org_name"])

        with allure.step("【步骤 3】验证列表有数据"):
            is_empty = await contract_list_page.verify_list_is_empty()
            assert not is_empty, f"按机构名'{case_data['org_name']}'筛选后列表为空"

    @allure.title("验证按签约项目名称筛选: {case_data[description]}")
    @allure.description("""
    测试: 在签约项目列表页按签约项目名称筛选，验证结果匹配。

    测试流程:
    1. 进入签约项目列表页
    2. 输入项目名称并搜索
    3. 验证列表包含目标项目
    """)
    @pytest.mark.parametrize("case_data", [c for c in CONTRACT_FILTER_CASES if c["case_id"] == "contract_filter_003"])
    @pytest.mark.asyncio
    async def test_filter_by_project_name(self, page_module, operate_user, case_data):
        """SIGN-LIST-008: 按签约项目名称筛选"""
        logger.info("Starting SIGN-LIST-008: 按签约项目名称筛选")
        contract_list_page = RFPContractListPage(page_module)

        with allure.step("【步骤 1】进入签约项目列表页"):
            await contract_list_page.navigate_to_home()
            await contract_list_page.navigate_to_contracting()

        with allure.step(f"【步骤 2】按签约项目名称筛选: {case_data['project_name']}"):
            await contract_list_page.search_by_project_name(case_data["project_name"])

        with allure.step("【步骤 3】验证列表包含目标项目"):
            found = await contract_list_page.verify_project_in_list(case_data["project_name"])
            assert found, f"列表中未找到项目: {case_data['project_name']}"

    @allure.title("验证按创建人筛选: {case_data[description]}")
    @allure.description("""
    测试: 在签约项目列表页按创建人筛选，验证结果匹配。

    测试流程:
    1. 进入签约项目列表页
    2. 输入创建人名称并搜索
    3. 验证列表有数据
    """)
    @pytest.mark.parametrize("case_data", [c for c in CONTRACT_FILTER_CASES if c["case_id"] == "contract_filter_004"])
    @pytest.mark.asyncio
    async def test_filter_by_creator(self, page_module, operate_user, case_data):
        """SIGN-LIST-009: 按创建人筛选"""
        logger.info("Starting SIGN-LIST-009: 按创建人筛选")
        contract_list_page = RFPContractListPage(page_module)

        with allure.step("【步骤 1】进入签约项目列表页"):
            await contract_list_page.navigate_to_home()
            await contract_list_page.navigate_to_contracting()

        with allure.step(f"【步骤 2】按创建人筛选: {case_data['creator_name']}"):
            await contract_list_page.search_by_creator(case_data["creator_name"])

        with allure.step("【步骤 3】验证列表有数据"):
            is_empty = await contract_list_page.verify_list_is_empty()
            assert not is_empty, f"按创建人'{case_data['creator_name']}'筛选后列表为空"

    @allure.title("验证组合筛选: {case_data[description]}")
    @allure.description("""
    测试: 在签约项目列表页同时按机构名+项目名+创建人组合筛选，验证结果。

    测试流程:
    1. 进入签约项目列表页
    2. 依次按机构名、项目名、创建人筛选
    3. 验证列表包含目标项目
    """)
    @pytest.mark.parametrize("case_data", [c for c in CONTRACT_FILTER_CASES if c["case_id"] == "contract_filter_005"])
    @pytest.mark.asyncio
    async def test_combined_filter(self, page_module, operate_user, case_data):
        """SIGN-LIST-010: 组合筛选"""
        logger.info("Starting SIGN-LIST-010: 组合筛选")
        contract_list_page = RFPContractListPage(page_module)

        with allure.step("【步骤 1】进入签约项目列表页"):
            await contract_list_page.navigate_to_home()
            await contract_list_page.navigate_to_contracting()

        with allure.step(f"【步骤 2】组合筛选: 机构={case_data['org_name']}, 项目={case_data['project_name']}, 创建人={case_data['creator_name']}"):
            await contract_list_page.combined_search(
                case_data["org_name"],
                case_data["project_name"],
                case_data["creator_name"],
            )

        with allure.step("【步骤 3】验证列表包含目标项目"):
            found = await contract_list_page.verify_project_in_list(case_data["project_name"])
            assert found, f"组合筛选后列表中未找到项目: {case_data['project_name']}"

    @allure.title("验证搜索结果为空: {case_data[description]}")
    @allure.description("""
    测试: 输入不存在的项目名搜索，验证列表显示为空，页面无异常。

    测试流程:
    1. 进入签约项目列表页
    2. 输入不存在的项目名并搜索
    3. 验证列表为空，页面不报错
    """)
    @pytest.mark.parametrize("case_data", [c for c in CONTRACT_FILTER_CASES if c["case_id"] == "contract_filter_006"])
    @pytest.mark.asyncio
    async def test_search_no_results(self, page_module, operate_user, case_data):
        """SIGN-LIST-011: 搜索结果为空"""
        logger.info("Starting SIGN-LIST-011: 搜索结果为空")
        contract_list_page = RFPContractListPage(page_module)

        with allure.step("【步骤 1】进入签约项目列表页"):
            await contract_list_page.navigate_to_home()
            await contract_list_page.navigate_to_contracting()

        with allure.step(f"【步骤 2】搜索不存在的项目: {case_data['project_name']}"):
            await contract_list_page.search_by_project_name(case_data["project_name"])

        with allure.step("【步骤 3】验证列表为空"):
            is_empty = await contract_list_page.verify_list_is_empty()
            assert is_empty, "搜索不存在的项目后列表未显示为空"

