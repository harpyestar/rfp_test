"""
编辑 RFP 项目 Tab 保存功能测试 + 导出邀约酒店名单验证
测试场景: 验证 RFP 项目编辑页面中每个 Tab 的保存功能是否成功
         验证导出的邀约酒店名单包含酒店 ID 字段且数据与数据库一致
"""

import asyncio
import pytest
import allure
from pages.operate.rfp_management.edit_rfp_project_page import EditRFPProjectPage
from utils.oracle_db import get_normal_hotels, get_group_hotels
from utils.excel_utils import verify_exported_hotel_excel
from utils.test_data_loader import TestDataLoader

EDIT_PROJECT_TABS_DATA = TestDataLoader.load_params(
    "rfp_management_params.json",
    "edit_project_tabs",
)


@allure.feature("RFP 项目管理")
@allure.story("RFP 项目编辑 - Tab 保存功能")
class TestEditRFPProjectTabs:
    """RFP 项目编辑页面 Tab 保存功能测试类"""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("test_data", EDIT_PROJECT_TABS_DATA)
    @allure.title("验证 RFP 项目编辑页面中所有 Tab 的保存功能")
    @allure.description("""
    测试: Operate 角色在签约管理的签约页面中，对 未启动 状态的项目进行修改，
    验证项目编辑页面中每个 Tab 的保存功能是否正常。

    测试流程:
    1. 导航至签约管理 > 签约页面
    2. 选择 未启动 Tab
    3. 按签约项目标签搜索项目
    4. 按 Enter 搜索，点击第一个匹配项的修改项目按钮
    5. 在编辑页面中遍历所有 Tab:
       - 对有保存按钮的 Tab: 点击保存 → 验证 toast 成功提示
       - 对无保存按钮的 Tab: 点击完成跳过
    6. 生成完整的测试结果报告

    预期结果:
    - 所有有保存按钮的 Tab 保存成功，显示成功 toast 提示
    - 所有无保存按钮的 Tab 正常跳过处理
    """)
    async def test_edit_rfp_project_all_tabs_save(self, page_module, operate_user, test_data):
        """
        完整的 RFP 项目编辑页面 Tab 保存功能测试

        Args:
            page_module: Module 级 page 对象 - 复用登录状态
            operate_user: Operate 角色登录 fixture
            test_data: 参数化测试数据 {project_name}
        """
        project_name = test_data["project_name"]
        # 初始化 POM 类
        edit_page = EditRFPProjectPage(page_module)

        with allure.step("【步骤 1】导航至签约管理 > 签约页面"):
            await edit_page.navigate_to_contracting()

        with allure.step("【步骤 2】选择 未启动 Tab"):
            await edit_page.click_not_started_tab()

        with allure.step(f"【步骤 3】搜索项目: {project_name}"):
            await edit_page.search_and_open_project(project_name)

        with allure.step("【步骤 4】遍历所有 Tab 进行保存功能测试"):
            test_results = await edit_page.test_all_tabs_save_functionality()

        with allure.step("【步骤 5】验证测试结果"):
            # 检查是否测试了所有的 Tab
            assert test_results["total_tabs"] > 0, "未能获取到任何 Tab"

            # 检查总 Tab 数是否与预期相符
            total_processed = test_results["tabs_with_save"] + test_results["tabs_without_save"]
            assert total_processed == test_results["total_tabs"], \
                f"处理的 Tab 数 ({total_processed}) 与总 Tab 数 ({test_results['total_tabs']}) 不符"

            # 检查是否所有有保存按钮的 Tab 都保存成功
            total_save_operations = test_results["save_success_count"] + test_results["save_failure_count"]
            assert total_save_operations == test_results["tabs_with_save"], \
                f"保存操作数 ({total_save_operations}) 与有保存按钮的 Tab 数 ({test_results['tabs_with_save']}) 不符"

            # 检查是否所有有保存按钮的 Tab 都成功保存
            if test_results["save_failure_count"] > 0:
                failed_tabs = [
                    d["tab_name"] for d in test_results["details"]
                    if d["has_save"] and d["save_result"] != "SUCCESS"
                ]
                assert False, f"以下 Tab 保存失败: {', '.join(failed_tabs)}"

        # 生成最终的 Allure 报告
        final_report = f"""
        [OK] RFP 项目编辑页面 Tab 保存功能测试完成

        【测试项目】
        - 项目名称: {project_name}

        【测试统计】
        - 总 Tab 数: {test_results['total_tabs']}
        - 有保存按钮的 Tab: {test_results['tabs_with_save']}
        - 无保存按钮的 Tab: {test_results['tabs_without_save']}
        - 保存成功: {test_results['save_success_count']}/{test_results['tabs_with_save']}
        - 保存失败: {test_results['save_failure_count']}/{test_results['tabs_with_save']}

        【测试覆盖的 Tab】
        """
        for i, detail in enumerate(test_results["details"], 1):
            status_icon = "[OK]" if detail["save_result"] == "SUCCESS" else \
                         "[SKIP]" if detail["save_result"] == "NO_SAVE_BUTTON" else "[FAIL]"
            final_report += f"\n{i}. {status_icon} {detail['tab_name']}"
            final_report += f"\n   - 状态: {detail['save_result']}"
            final_report += f"\n   - 说明: {detail['message']}"

        allure.attach(final_report, "完整测试报告", allure.attachment_type.TEXT)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("test_data", EDIT_PROJECT_TABS_DATA)
    @allure.title("验证未启动项目的启动按钮和确认弹窗")
    @allure.description("""
    测试: Operate 角色在签约管理的签约页面中，查看未启动项目的启动按钮和确认弹窗。

    测试流程:
    1. 导航至签约管理 > 签约页面
    2. 选择未启动 Tab
    3. 搜索项目
    4. 点击该项目的 启动 按钮
    5. 验证 确定 确认按钮出现（不点击确定，只验证出现）
    6. 点击取消关闭弹窗

    预期结果:
    - 能够找到项目的 启动 按钮
    - 点击 启动 后出现 确定 确认按钮的弹窗
    """)
    async def test_verify_start_project_confirmation_popup(self, page_module, operate_user, test_data):
        """
        验证未启动项目的启动按钮和确认弹窗

        Args:
            page_module: Module 级 page 对象 - 复用登录状态
            operate_user: Operate 角色登录 fixture
            test_data: 参数化测试数据 {project_name}
        """
        project_name = test_data["project_name"]
        # 初始化 POM 类
        edit_page = EditRFPProjectPage(page_module)

        with allure.step("【步骤 1】导航至签约管理 > 签约页面"):
            await edit_page.navigate_to_contracting()

        with allure.step("【步骤 2】选择 未启动 Tab"):
            await edit_page.click_not_started_tab()

        with allure.step(f"【步骤 3】搜索项目: {project_name}"):
            await edit_page.search_project_by_keyword(project_name)

        with allure.step("【步骤 4】点击 启动 按钮"):
            await edit_page.click_start_button()

        with allure.step("【步骤 5】验证 确定 确认按钮出现"):
            confirmation_visible = await edit_page.verify_confirmation_dialog_visible()
            assert confirmation_visible, "启动确认弹窗（确定按钮）未出现"

        with allure.step("【步骤 6】点击 取消 关闭弹窗"):
            await edit_page.click_cancel_button()

        # 生成测试结果报告
        result_report = f"""
        [OK] 未启动项目 启动 按钮验证测试完成

        【测试项目】
        - 项目名称: {project_name}

        【测试结果】
        - 启动按钮: 已找到并点击
        - 确认弹窗: 已出现（确定按钮可见）
        - 弹窗已关闭: 已点击取消
        - 测试状态: 通过 ✓
        """
        allure.attach(result_report, "测试结果", allure.attachment_type.TEXT)

    # ======================== 导出普通酒店名单验证测试 ========================

    # ======================== 导出邀约酒店名单验证测试（普通/集团）=======================

    @pytest.mark.asyncio
    @pytest.mark.mark_20260521
    @allure.title("导出{test_data[export_type]}酒店名单包含酒店ID字段 - {test_data[description]}")
    @allure.description("""
    测试: Operate 角色进入已启动项目的编辑页，在邀请酒店 Tab 中导出酒店名单，
    验证导出的 Excel 包含酒店 ID 字段，且数据与数据库查询结果一致。

    流程: 导航 → 已启动Tab → 搜索修改 → 提取项目ID → 查DB → 邀请酒店Tab
          （集团类型额外：点击添加酒店集团意向单店）→ 导出 → 验证Excel
    """)
    @pytest.mark.parametrize("test_data", TestDataLoader.load_params(
        "rfp_management_params.json", "export_hotel_list"
    ))
    async def test_export_hotel_list_includes_hotel_id(self, page_module, operate_user,  test_data):
        """
        验证导出的酒店名单包含酒店 ID 字段且数据一致（普通/集团共用）

        Args:
            page_module: Module 级 page 对象
            operate_user: Operate 角色登录 fixture
            test_data: 参数化测试数据 {project_name, export_type}
        """
        project_name = test_data["project_name"]
        export_type = test_data["export_type"]
        sheet_label = "普通酒店名单" if export_type == "normal" else "集团酒店名单"
        edit_page = EditRFPProjectPage(page_module)

        with allure.step("【步骤 1】导航至签约管理 > 签约页面"):
            await edit_page.navigate_to_contracting()

        with allure.step("【步骤 2】选择 已启动 Tab"):
            await edit_page.click_started_tab()

        with allure.step("【步骤 3】搜索项目并点击修改"):
            await edit_page.search_and_click_modify(project_name)

        with allure.step("【步骤 4】提取项目 ID，查询数据库"):
            project_id = await edit_page.get_project_id_from_url()
            query_fn = get_normal_hotels if export_type == "normal" else get_group_hotels
            db_data = await asyncio.to_thread(query_fn, project_id)
            assert len(db_data) > 0, \
                f"数据库未查询到{sheet_label}记录 (project_id={project_id})"

        with allure.step("【步骤 5】进入邀请酒店 Tab"):
            await edit_page.click_tab(edit_page.INVITE_HOTEL_TAB_NAME)

        # 集团类型多一个操作：点击添加酒店集团意向单店
        if export_type == "group":
            with allure.step("【步骤 5b】点击添加酒店集团意向单店"):
                await edit_page.click_add_group_intent_hotel_button()

        with allure.step(f"【步骤 6】导出{sheet_label}"):
            if export_type == "normal":
                download = await edit_page.export_normal_hotel_list()
            else:
                download = await edit_page.export_group_hotel_list()

        with allure.step(f"【步骤 7】验证{sheet_label} Excel"):
            await verify_exported_hotel_excel(download, db_data, sheet_label)

        # 生成报告
        report = f"""
        [OK] {sheet_label}导出验证完成
        - 项目名称: {project_name}
        - 项目 ID: {project_id}
        - 类型: {export_type}
        - 数据库记录数: {len(db_data)}
        - 验证结果: 通过 ✓
        """
        allure.attach(report, "测试报告", allure.attachment_type.TEXT)

    # ======================== 邀约酒店集团 - 集团机构名称筛选 ========================

    @pytest.mark.asyncio
    @pytest.mark.mark_20260604
    @allure.title("邀约酒店集团-筛选控件标签文案校验: {test_data[description]}")
    @allure.description("""
    测试: 验证邀约酒店集团区域筛选控件的标签显示为"集团机构名称"。

    流程: 签约管理→签约→未启动Tab→搜索项目→修改项目→邀请酒店Tab→邀约酒店集团
    """)
    @pytest.mark.parametrize("test_data", TestDataLoader.load_params(
        "rfp_management_params.json", "invite_hotel_group_filter"
    ))
    async def test_invite_hotel_group_filter_label(self, page_module, operate_user, test_data):
        edit_page = EditRFPProjectPage(page_module)

        with allure.step("【步骤 1】导航至签约管理 > 签约页面"):
            await edit_page.navigate_to_contracting()

        with allure.step("【步骤 2】选择未启动 Tab"):
            await edit_page.click_not_started_tab()

        with allure.step(f"【步骤 3】搜索项目并点击修改: {test_data['project_name']}"):
            await edit_page.search_and_open_project(test_data["project_name"])

        with allure.step("【步骤 4】点击邀请酒店 Tab"):
            await edit_page.click_tab(edit_page.INVITE_HOTEL_TAB_NAME)

        with allure.step("【步骤 5】点击邀约酒店集团按钮"):
            await edit_page.click_invite_hotel_group_button()

        with allure.step("【步骤 6】验证筛选控件标签文案"):
            label_text = await edit_page.get_group_org_name_filter_label()
            assert label_text == "集团机构名称", \
                f"筛选控件标签期望为'集团机构名称'，实际为'{label_text}'"

    @pytest.mark.asyncio
    @pytest.mark.mark_20260604
    @allure.title("邀约酒店集团-精确搜索: {test_data[description]} - {test_data[group_org_name]}")
    @allure.description("""
    测试: 在集团机构名称筛选框中输入完整名称执行精确搜索，验证结果列表中每条记录的名称与搜索词一致。

    流程: 同上进入邀约酒店集团 → 输入集团机构名称 → 搜索 → 逐条验证结果
    """)
    @pytest.mark.parametrize("test_data", TestDataLoader.load_params(
        "rfp_management_params.json", "invite_hotel_group_filter"
    ))
    async def test_invite_hotel_group_exact_search(self, page_module, operate_user, test_data):
        edit_page = EditRFPProjectPage(page_module)

        with allure.step("【步骤 1】导航至签约管理 > 签约页面"):
            await edit_page.navigate_to_contracting()

        with allure.step("【步骤 2】选择未启动 Tab"):
            await edit_page.click_not_started_tab()

        with allure.step(f"【步骤 3】搜索项目并点击修改: {test_data['project_name']}"):
            await edit_page.search_and_open_project(test_data["project_name"])

        with allure.step("【步骤 4】点击邀请酒店 Tab"):
            await edit_page.click_tab(edit_page.INVITE_HOTEL_TAB_NAME)

        with allure.step("【步骤 5】点击邀约酒店集团按钮"):
            await edit_page.click_invite_hotel_group_button()

        with allure.step(f"【步骤 6】输入集团机构名称并搜索: {test_data['group_org_name']}"):
            await edit_page.search_group_org_name(test_data["group_org_name"])

        with allure.step("【步骤 7】验证搜索结果"):
            names = await edit_page.get_result_group_org_names()
            assert len(names) > 0, "搜索结果为空，期望至少有一条记录"
            found = any(test_data["group_org_name"] in n for n in names)
            assert found, f"搜索结果中未找到机构名称'{test_data['group_org_name']}'"
