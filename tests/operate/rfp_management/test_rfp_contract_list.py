"""
签约项目列表页测试模块
测试签约列表页的菜单导航、默认Tab展示和Tab切换功能
"""
import json
from datetime import datetime

import allure
import pytest
from pages.operate.rfp_management.create_rfp_project_page import CreateRFPProjectPage
from pages.operate.rfp_management.rfp_contract_list_page import RFPContractListPage
from utils.config import config
from utils.logger import get_logger
from utils.test_data_loader import TestDataLoader
from utils.timeout_config import timeout_config

logger = get_logger("tests.operate.rfp_management.test_rfp_contract_list", config.log_level)

CONTRACT_FILTER_CASES = TestDataLoader.load_params(
    "rfp_management_params.json",
    "contract_list_filter",
)

with open(config.PROJECT_ROOT / "data" / "test_cases" / "rfp_management_params.json", encoding="utf-8") as _f:
    _ALL_PARAMS = json.load(_f)
    _START_STOP_ALL = _ALL_PARAMS["start_and_stop_project"]
    START_STOP_PROJECT_DATA = _START_STOP_ALL[0]
    VOID_PROJECT_DATA = _START_STOP_ALL[1]
    VOID_CANCEL_DATA = _ALL_PARAMS["void_cancel_project"][0]


def generate_project_name(prefix: str) -> str:
    return f"{prefix}-{datetime.now().strftime('%Y%m%d%H%M%S')}"


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
            await contract_list_page.click_unstarted_tab()

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
            await contract_list_page.click_unstarted_tab()

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
            await contract_list_page.click_unstarted_tab()

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

        with allure.step("【步骤 2】选择未启动 Tab"):
            await contract_list_page.click_unstarted_tab()

        with allure.step(f"【步骤 3】组合筛选: 机构={case_data['org_name']}, 项目={case_data['project_name']}, 创建人={case_data['creator_name']}"):
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
            await contract_list_page.click_unstarted_tab()

        with allure.step(f"【步骤 2】搜索不存在的项目: {case_data['project_name']}"):
            await contract_list_page.search_by_project_name(case_data["project_name"])

        with allure.step("【步骤 3】验证列表为空"):
            is_empty = await contract_list_page.verify_list_is_empty()
            assert is_empty, "搜索不存在的项目后列表未显示为空"

    @allure.title("验证重置筛选条件: {case_data[description]}")
    @allure.description("""
    测试: 执行筛选后点击重置按钮，验证筛选条件清空、列表恢复全部数据。

    测试流程:
    1. 进入签约项目列表页
    2. 按项目名称筛选并确认列表已过滤
    3. 点击「重置」按钮
    4. 验证所有筛选条件清空、列表重新加载
    """)
    @pytest.mark.parametrize("case_data", [c for c in CONTRACT_FILTER_CASES if c["case_id"] == "contract_filter_007"])
    @pytest.mark.asyncio
    async def test_reset_filter(self, page_module, operate_user, case_data):
        """SIGN-LIST-012: 重置筛选条件"""
        logger.info("Starting SIGN-LIST-012: 重置筛选条件")
        contract_list_page = RFPContractListPage(page_module)

        with allure.step("【步骤 1】进入签约项目列表页"):
            await contract_list_page.navigate_to_home()
            await contract_list_page.navigate_to_contracting()
            await contract_list_page.click_unstarted_tab()

        with allure.step(f"【步骤 2】按签约项目名称筛选: {case_data['project_name']}"):
            await contract_list_page.search_by_project_name(case_data["project_name"])

        with allure.step("【步骤 3】确认列表已按筛选条件过滤"):
            filter_value = await contract_list_page.get_project_filter_value()
            assert case_data["project_name"] in filter_value, \
                f"筛选条件未生效，当前值: '{filter_value}'"

        with allure.step("【步骤 4】点击「重置」按钮"):
            await contract_list_page.reset_filter()

        with allure.step("【步骤 5】验证所有筛选条件已清空"):
            all_cleared = await contract_list_page.verify_all_filters_cleared()
            assert all_cleared, "筛选条件未完全清空"

        with allure.step("【步骤 6】验证列表重新加载恢复全部数据"):
            is_empty = await contract_list_page.verify_list_is_empty()
            assert not is_empty, "重置后列表为空，预期恢复全部数据"

    @allure.title("验证未启动Tab列表字段展示完整")
    @allure.description("""
    测试: 在未启动Tab下校验列表字段列完整且第一行有数据。

    测试流程:
    1. 进入签约项目列表页
    2. 确保在「未启动」Tab
    3. 逐一核对列表字段列名称
    4. 验证第一行数据完整
    5. 验证操作列按钮存在
    """)
    @pytest.mark.asyncio
    async def test_verify_unstarted_list_fields(self, page_module, operate_user):
        """SIGN-LIST-013: 签约项目字段校验-未启动Tab"""
        logger.info("Starting SIGN-LIST-013: 签约项目字段校验-未启动Tab")
        contract_list_page = RFPContractListPage(page_module)

        with allure.step("【步骤 1】进入签约项目列表页"):
            await contract_list_page.navigate_to_home()
            await contract_list_page.navigate_to_contracting()

        with allure.step("【步骤 2】确保在「未启动」Tab"):
            unstarted_tab = contract_list_page.page.get_by_text(
                contract_list_page.UNSTARTED_TAB_TEXT, exact=True
            ).first
            await unstarted_tab.wait_for(timeout=timeout_config.get_element_timeout())
            assert await unstarted_tab.is_visible(), "未启动Tab不可见"

        with allure.step("【步骤 2.5】点击「未启动」Tab"):
            await contract_list_page.click_unstarted_tab()

        with allure.step("【步骤 3】逐一核对列表字段列名称"):
            columns_ok = await contract_list_page.verify_unstarted_list_columns()
            assert columns_ok, "未启动Tab列表字段列不完整"

        with allure.step("【步骤 4】验证第一行数据完整"):
            has_data = await contract_list_page.verify_unstarted_first_row_has_data()
            assert has_data, "未启动Tab列表第一行无数据"

        with allure.step("【步骤 5】验证操作列按钮：启动、修改项目、作废"):
            buttons_ok = await contract_list_page.verify_unstarted_action_buttons()
            assert buttons_ok, "操作列按钮不完整"

    @allure.title("验证已启动Tab列表字段展示完整")
    @allure.description("""
    测试: 在已启动Tab下校验列表字段列完整、操作按钮正确。

    测试流程:
    1. 进入签约项目列表页
    2. 切换到「已启动」Tab
    3. 逐一核对列表字段列名称（含已报价/受邀酒店数）
    4. 验证第一行数据完整
    5. 验证操作列按钮：去签约、修改、终止、导出报价、履约情况
    """)
    @pytest.mark.asyncio
    async def test_verify_started_list_fields(self, page_module, operate_user):
        """SIGN-LIST-014: 签约项目字段校验-已启动Tab"""
        logger.info("Starting SIGN-LIST-014: 签约项目字段校验-已启动Tab")
        contract_list_page = RFPContractListPage(page_module)

        with allure.step("【步骤 1】进入签约项目列表页"):
            await contract_list_page.navigate_to_home()
            await contract_list_page.navigate_to_contracting()

        with allure.step("【步骤 2】切换到「已启动」Tab"):
            await contract_list_page.click_started_tab()

        with allure.step("【步骤 3】逐一核对列表字段列名称"):
            columns_ok = await contract_list_page.verify_started_list_columns()
            assert columns_ok, "已启动Tab列表字段列不完整"

        with allure.step("【步骤 4】验证第一行数据完整"):
            has_data = await contract_list_page.verify_started_first_row_has_data()
            assert has_data, "已启动Tab列表第一行无数据"

        with allure.step("【步骤 5】验证操作列按钮：去签约、修改、终止、导出报价、履约情况"):
            buttons_ok = await contract_list_page.verify_started_action_buttons()
            assert buttons_ok, "操作列按钮不完整"

    @allure.title("验证分页功能正常")
    @allure.description("""
    测试: 在已启动Tab下验证列表底部分页控件存在、点击下一页后数据切换。

    测试流程:
    1. 进入签约项目列表页
    2. 切换到「已启动」Tab
    3. 验证分页控件可见
    4. 记录第一页行数
    5. 点击「下一页」
    6. 验证页码变化、数据刷新
    """)
    @pytest.mark.asyncio
    async def test_verify_pagination(self, page_module, operate_user):
        """SIGN-LIST-015: 分页功能"""
        logger.info("Starting SIGN-LIST-015: 分页功能")
        contract_list_page = RFPContractListPage(page_module)

        with allure.step("【步骤 1】进入签约项目列表页"):
            await contract_list_page.navigate_to_home()
            await contract_list_page.navigate_to_contracting()

        with allure.step("【步骤 2】切换到「已启动」Tab"):
            await contract_list_page.click_started_tab()

        with allure.step("【步骤 3】验证分页控件可见"):
            pagination_visible = await contract_list_page.verify_pagination_visible()
            assert pagination_visible, "分页控件不可见"

        with allure.step("【步骤 4】记录首页当前页码和行数"):
            first_page_num = await contract_list_page.get_current_page_number()
            first_page_rows = await contract_list_page.get_page_row_count()
            logger.info(f"首页页码={first_page_num}, 行数={first_page_rows}")

        with allure.step("【步骤 5】点击「下一页」"):
            await contract_list_page.click_next_page()

        with allure.step("【步骤 6】验证页码已变化"):
            second_page_num = await contract_list_page.get_current_page_number()
            assert second_page_num > first_page_num, \
                f"页码未变化: {first_page_num} → {second_page_num}"

        with allure.step("【步骤 7】验证第二页有数据"):
            second_page_rows = await contract_list_page.get_page_row_count()
            assert second_page_rows > 0, "第二页无数据"

    @allure.title("验证启动项目→终止项目联动")
    @allure.description("""
    联动测试 SIGN-LIST-016 + SIGN-LIST-023：
    创建项目 → 启动 → 到已启动Tab终止项目。

    测试流程:
    1. 创建新项目
    2. 进入签约列表，搜索项目，点击「启动」并确认
    3. 切换到已启动Tab，搜索项目，点击「终止」并确认
    """)
    @pytest.mark.asyncio
    async def test_start_and_stop_project(self, page_module, operate_user):
        """SIGN-LIST-016: 启动项目 + SIGN-LIST-023: 终止项目"""
        project_name = generate_project_name(START_STOP_PROJECT_DATA["project_name_prefix"])
        logger.info(f"Starting SIGN-LIST-016+023 联动测试, 项目={project_name}")

        # ===== 阶段1: 创建项目 =====
        with allure.step("【阶段1-创建】创建新项目"):
            create_page = CreateRFPProjectPage(page_module)
            await create_page.navigate_to_create_project()
            await create_page.select_contracting_agency(START_STOP_PROJECT_DATA["agency_name"])
            await create_page.fill_project_name(project_name)
            await create_page.fill_contact_person(START_STOP_PROJECT_DATA["contact_person"])
            await create_page.fill_contact_phone(START_STOP_PROJECT_DATA["contact_phone"])
            await create_page.select_invitation_sign_method()
            await create_page.select_registration_date(START_STOP_PROJECT_DATA["start_day"], START_STOP_PROJECT_DATA["end_day"])
            await create_page.select_first_round_date(START_STOP_PROJECT_DATA["start_day"], START_STOP_PROJECT_DATA["end_day"])
            await create_page.select_agreement_date(START_STOP_PROJECT_DATA["start_day"], START_STOP_PROJECT_DATA["end_day"])
            await create_page.fill_expected_hotel_count(START_STOP_PROJECT_DATA["expected_hotel_count"])
            await create_page.fill_min_diff_std(START_STOP_PROJECT_DATA["min_diff_std"])
            await create_page.fill_max_diff_std(START_STOP_PROJECT_DATA["max_diff_std"])
            await create_page.click_save_and_next()
            toast_text = await create_page.verify_save_success()
            assert toast_text, "项目创建后未检测到成功提示"
            logger.info(f"项目创建完成: {project_name}")

        # ===== 阶段2: SIGN-LIST-016 启动项目 =====
        contract_page = RFPContractListPage(page_module)

        with allure.step("【阶段2-启动】进入签约列表并搜索项目"):
            await contract_page.navigate_to_home()
            await contract_page.navigate_to_contracting()
            await contract_page.click_unstarted_tab()
            await contract_page.search_by_project_name(project_name)

        with allure.step("【阶段2-启动】点击「启动」按钮"):
            await contract_page.click_start_button_for_first_row()

        with allure.step("【阶段2-启动】验证确认弹窗"):
            dialog_ok = await contract_page.verify_confirm_dialog_visible(
                contract_page.START_CONFIRM_MSG
            )
            assert dialog_ok, "启动确认弹窗未出现或内容不匹配"

        with allure.step("【阶段2-启动】点击弹窗「确认」"):
            await contract_page.click_confirm_in_dialog()

        with allure.step("【阶段2-启动】验证启动成功提示"):
            toast_ok = await contract_page.verify_success_toast(contract_page.START_SUCCESS_TEXT)
            assert toast_ok, "未检测到启动成功提示"

        # ===== 阶段3: SIGN-LIST-023 终止项目 =====
        with allure.step("【阶段3-终止】切换到已启动Tab并搜索项目"):
            await contract_page.click_started_tab()
            await contract_page.search_by_project_name(project_name)

        with allure.step("【阶段3-终止】点击「终止」按钮"):
            await contract_page.click_stop_button_for_first_row()

        with allure.step("【阶段3-终止】验证确认弹窗"):
            dialog_ok = await contract_page.verify_confirm_dialog_visible(
                contract_page.STOP_CONFIRM_MSG
            )
            assert dialog_ok, "终止确认弹窗未出现或内容不匹配"

        with allure.step("【阶段3-终止】点击弹窗「确认」"):
            await contract_page.click_confirm_in_dialog()

        with allure.step("【阶段3-终止】验证终止成功提示"):
            toast_ok = await contract_page.verify_success_toast(contract_page.STOP_SUCCESS_TEXT)
            assert toast_ok, "未检测到终止成功提示"

    @allure.title(" ")
    @allure.description("""
    测试 SIGN-LIST-019：创建项目 → 未启动Tab下作废项目。

    测试流程:
    1. 创建新项目
    2. 进入签约列表，搜索项目，点击「作废」并确认
    3. 验证项目从列表消失
    """)
    @pytest.mark.asyncio
    async def test_void_project(self, page_module, operate_user):
        """SIGN-LIST-019: 作废项目-确认"""
        project_name = generate_project_name(VOID_PROJECT_DATA["project_name_prefix"])
        logger.info(f"Starting SIGN-LIST-019 作废项目测试, 项目={project_name}")

        # ===== 阶段1: 创建项目 =====
        with allure.step("【阶段1-创建】创建新项目"):
            create_page = CreateRFPProjectPage(page_module)
            await create_page.navigate_to_create_project()
            await create_page.select_contracting_agency(VOID_PROJECT_DATA["agency_name"])
            await create_page.fill_project_name(project_name)
            await create_page.fill_contact_person(VOID_PROJECT_DATA["contact_person"])
            await create_page.fill_contact_phone(VOID_PROJECT_DATA["contact_phone"])
            await create_page.select_invitation_sign_method()
            await create_page.select_registration_date(VOID_PROJECT_DATA["start_day"], VOID_PROJECT_DATA["end_day"])
            await create_page.select_first_round_date(VOID_PROJECT_DATA["start_day"], VOID_PROJECT_DATA["end_day"])
            await create_page.select_agreement_date(VOID_PROJECT_DATA["start_day"], VOID_PROJECT_DATA["end_day"])
            await create_page.fill_expected_hotel_count(VOID_PROJECT_DATA["expected_hotel_count"])
            await create_page.fill_min_diff_std(VOID_PROJECT_DATA["min_diff_std"])
            await create_page.fill_max_diff_std(VOID_PROJECT_DATA["max_diff_std"])
            await create_page.click_save_and_next()
            toast_text = await create_page.verify_save_success()
            assert toast_text, "项目创建后未检测到成功提示"
            logger.info(f"项目创建完成: {project_name}")

        # ===== 阶段2: SIGN-LIST-019 作废项目 =====
        contract_page = RFPContractListPage(page_module)

        with allure.step("【阶段2-作废】进入签约列表并搜索项目"):
            await contract_page.navigate_to_home()
            await contract_page.navigate_to_contracting()
            await contract_page.click_unstarted_tab()
            await contract_page.search_by_project_name(project_name)

        with allure.step("【阶段2-作废】点击「作废」按钮"):
            await contract_page.click_void_button_for_first_row()

        with allure.step("【阶段2-作废】验证确认弹窗"):
            dialog_ok = await contract_page.verify_confirm_dialog_visible(
                contract_page.VOID_CONFIRM_MSG
            )
            assert dialog_ok, "作废确认弹窗未出现或内容不匹配"

        with allure.step("【阶段2-作废】点击弹窗「确定」"):
            await contract_page.click_confirm_in_dialog()

        with allure.step("【阶段2-作废】验证作废成功提示"):
            toast_ok = await contract_page.verify_success_toast(contract_page.VOID_SUCCESS_TEXT)
            assert toast_ok, "未检测到作废成功提示"

        with allure.step("【阶段2-作废】断言项目从列表消失"):
            await contract_page.expect_project_disappeared(project_name)

    @allure.title("验证作废项目-取消: {case_data[description]}")
    @allure.description("""
    测试 SIGN-LIST-020：点击作废后在弹窗中取消，项目保持不变。

    测试流程:
    1. 进入签约列表，搜索指定项目
    2. 点击「作废」，验证弹窗出现
    3. 点击「取消」，验证弹窗关闭
    4. 验证项目仍在列表中
    """)
    @pytest.mark.parametrize("case_data", [VOID_CANCEL_DATA])
    @pytest.mark.asyncio
    async def test_void_project_cancel(self, page_module, operate_user, case_data):
        """SIGN-LIST-020: 作废项目-取消"""
        project_name = case_data["project_name"]
        logger.info(f"Starting SIGN-LIST-020 作废取消测试, 项目={project_name}")
        contract_page = RFPContractListPage(page_module)

        with allure.step("【步骤 1】进入签约列表并搜索项目"):
            await contract_page.navigate_to_home()
            await contract_page.navigate_to_contracting()
            await contract_page.click_unstarted_tab()
            await contract_page.search_by_project_name(project_name)

        with allure.step("【步骤 2】确认项目存在于列表中"):
            found = await contract_page.verify_project_in_list(project_name)
            assert found, f"未找到目标项目: {project_name}"

        with allure.step("【步骤 3】点击「作废」按钮"):
            await contract_page.click_void_button_for_first_row()

        with allure.step("【步骤 4】验证作废确认弹窗"):
            dialog_ok = await contract_page.verify_confirm_dialog_visible(
                contract_page.VOID_CONFIRM_MSG
            )
            assert dialog_ok, "作废确认弹窗未出现或内容不匹配"

        with allure.step("【步骤 5】点击弹窗「取消」"):
            await contract_page.click_cancel_in_dialog()

        with allure.step("【步骤 6】验证弹窗已关闭"):
            dialog_gone = await contract_page.verify_confirm_dialog_disappeared()
            assert dialog_gone, "弹窗未关闭"

        with allure.step("【步骤 7】验证项目仍在列表中"):
            found = await contract_page.verify_project_in_list(project_name)
            assert found, f"取消作废后项目消失: {project_name}"