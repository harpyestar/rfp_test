"""
RFP 报价详情页内部跟进备注测试
"""

from datetime import datetime
import allure
import pytest
from pages.operate.rfp_management.rfp_detailPage_project import RFPDetailPageProject
from pages.operate.rfp_management.rfp_contract_map_page import RFPContractMapPage
from utils.config import config
from utils.logger import get_logger
from utils.test_data_loader import TestDataLoader
from utils.excel_utils import generate_signing_status_excel

logger = get_logger("tests.operate.rfp_management.test_rfp_detailPage_project", config.log_level)

RFP_DETAIL_PAGE_CASES = TestDataLoader.load_params(
    "rfp_management_params.json",
    "rfp_detail_page",
)

REMARK_CASES = [case for case in RFP_DETAIL_PAGE_CASES if case["case_id"] == "detail_001"]
EXPAND_CASES = [case for case in RFP_DETAIL_PAGE_CASES if case["case_id"] == "detail_002"]


@allure.feature("RFP 项目管理")
@allure.story("报价详情页内部跟进备注")
class TestRFPDetailPageProject:
    """RFP 报价详情页内部跟进备注测试"""

    @pytest.mark.parametrize(
        "case_data",
        REMARK_CASES,
        ids=[case["case_id"] for case in REMARK_CASES],
    )
    @pytest.mark.asyncio
    @allure.title("验证报价详情页可以新增内部跟进备注")
    @allure.description("""
    测试: Operate 角色进入报价详情页后，验证可以新增内部跟进备注并在刷新后正常展示。

    测试流程:
    1. 使用 Operate 角色账号登录
    2. 进入 /home 页面
    3. 点击菜单: 签约管理 > 签约
    4. 切换到已启动 Tab
    5. 搜索指定项目
    6. 点击首个去签约按钮
    7. 切换到已中签 Tab，并选择首个酒店
    8. 打开报价详情新标签页
    9. 验证内部备注按钮存在
    10. 填写内部备注并提交
    11. 刷新报价详情页
    12. 验证页面展示刚刚填写的内部备注内容

    预期结果:
    - 报价详情页存在内部备注按钮
    - 提交内部备注成功
    - 刷新后仍可看到刚刚填写的内部备注内容
    """)
    async def test_add_internal_follow_up_remark(self, page_module, operate_user, case_data: dict):
        """验证报价详情页可以新增内部跟进备注"""
        project_name = case_data["project_name"]
        search_keyword = case_data.get("search_keyword", project_name)
        remark_content = f"hy-自动化书写文字-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        logger.info(
            f"Starting RFP detail page remark test, case: {case_data['case_id']}, project: {project_name}"
        )

        rfp_detail_page = RFPDetailPageProject(page_module)

        with allure.step("【步骤 1】进入 /home 页面"):
            await rfp_detail_page.navigate_to_home()

        with allure.step("【步骤 2】点击菜单进入签约页面"):
            await rfp_detail_page.navigate_to_contracting()

        with allure.step("【步骤 3】切换到已启动 Tab"):
            await rfp_detail_page.click_started_tab()

        with allure.step(f"【步骤 4】搜索项目: {search_keyword}"):
            await rfp_detail_page.search_project(search_keyword)

        with allure.step("【步骤 5】点击首个去签约按钮"):
            await rfp_detail_page.click_first_go_contracting_button()

        with allure.step("【步骤 6】切换到已中签 Tab"):
            await rfp_detail_page.click_awarded_tab()

        with allure.step("【步骤 7】选择首个已中签酒店"):
            await rfp_detail_page.select_first_awarded_hotel()

        with allure.step("【步骤 8】打开报价详情页"):
            detail_popup = await rfp_detail_page.open_first_bid_detail_popup()
            detail_page = RFPDetailPageProject(detail_popup)

        with allure.step("【步骤 9】验证内部备注按钮存在"):
            has_internal_remark_button = await detail_page.verify_internal_remark_button_visible()
            assert has_internal_remark_button, "报价详情页未显示内部备注按钮"

        with allure.step("【步骤 10】点击内部备注按钮"):
            await detail_page.click_internal_remark_button()

        with allure.step("【步骤 11】填写并提交内部备注"):
            await detail_page.add_internal_remark(remark_content)

        with allure.step("【步骤 12】刷新报价详情页"):
            await detail_page.refresh_detail_page()

        with allure.step("【步骤 13】验证内部备注内容展示"):
            has_internal_remark = await detail_page.has_internal_remark(remark_content)
            assert has_internal_remark, f"刷新报价详情页后，未找到内部备注内容: {remark_content}"

        result_report = f"""
        [OK] RFP 报价详情页内部跟进备注测试完成

        【测试用例】
        - case_id: {case_data['case_id']}
        - description: {case_data['description']}
        - 项目名称: {project_name}
        - 搜索关键词: {search_keyword}

        【备注内容】
        - {remark_content}

        【测试结果】
        - 报价详情页存在内部备注按钮
        - 内部备注提交成功
        - 刷新后仍可看到备注内容
        - 测试状态: 通过
        """
        allure.attach(result_report, "测试结果", allure.attachment_type.TEXT)

        logger.info("RFP detail page remark test passed")

    @pytest.mark.parametrize(
        "case_data",
        EXPAND_CASES,
        ids=[case["case_id"] for case in EXPAND_CASES],
    )
    @pytest.mark.asyncio
    @allure.title("验证报价详情页内部跟进备注展开/收起功能")
    @allure.description("""
    测试: Operate 角色进入报价详情页后，验证存在备注信息的酒店在备注栏目中存在展开/收起按钮功能。

    测试流程:
    1. 使用 Operate 角色账号登录
    2. 进入 /home 页面
    3. 点击菜单: 签约管理 > 签约
    4. 切换到已启动 Tab
    5. 搜索指定项目
    6. 点击首个去签约按钮
    7. 切换到已中签 Tab，并选择首个酒店
    8. 打开报价详情新标签页
    9. 验证备注栏目中存在展开按钮
    10. 点击展开按钮
    11. 验证备注栏目中存在收起按钮

    预期结果:
    - 备注栏目展示展开按钮
    - 点击展开按钮后，展示收起按钮
    """)
    async def test_verify_internal_remark_expand_collapse(self, page_module, operate_user, case_data: dict):
        """验证报价详情页内部跟进备注展开/收起功能"""
        project_name = case_data["project_name"]
        search_keyword = case_data.get("search_keyword", project_name)

        logger.info(
            f"Starting RFP detail page expand/collapse test, case: {case_data['case_id']}, project: {project_name}"
        )

        rfp_detail_page = RFPDetailPageProject(page_module)

        with allure.step("【步骤 1】进入 /home 页面"):
            await rfp_detail_page.navigate_to_home()

        with allure.step("【步骤 2】点击菜单进入签约页面"):
            await rfp_detail_page.navigate_to_contracting()

        with allure.step("【步骤 3】切换到已启动 Tab"):
            await rfp_detail_page.click_started_tab()

        with allure.step(f"【步骤 4】搜索项目: {search_keyword}"):
            await rfp_detail_page.search_project(search_keyword)

        with allure.step("【步骤 5】点击首个去签约按钮"):
            await rfp_detail_page.click_first_go_contracting_button()

        with allure.step("【步骤 6】切换到已中签 Tab"):
            await rfp_detail_page.click_awarded_tab()

        with allure.step("【步骤 7】选择首个已中签酒店"):
            await rfp_detail_page.select_first_awarded_hotel()

        with allure.step("【步骤 8】打开报价详情页"):
            detail_popup = await rfp_detail_page.open_first_bid_detail_popup()
            detail_page = RFPDetailPageProject(detail_popup)

        with allure.step("【步骤 9】验证备注栏目中存在展开按钮"):
            has_expand = await detail_page.verify_expand_button_visible()
            assert has_expand, "报价详情页备注栏目中未显示展开按钮"

        with allure.step("【步骤 10】点击展开按钮"):
            await detail_page.click_expand_button()

        with allure.step("【步骤 11】验证备注栏目中存在收起按钮"):
            has_collapse = await detail_page.verify_collapse_button_visible()
            assert has_collapse, "报价详情页备注栏目中未显示收起按钮"

        result_report = f"""
        [OK] RFP 报价详情页内部跟进备注展开/收起功能测试完成

        【测试用例】
        - case_id: {case_data['case_id']}
        - description: {case_data['description']}
        - 项目名称: {project_name}
        - 搜索关键词: {search_keyword}

        【测试结果】
        - 备注栏目存在展开按钮
        - 点击展开后显示收起按钮
        - 测试状态: 通过
        """
        allure.attach(result_report, "测试结果", allure.attachment_type.TEXT)

        logger.info("RFP detail page expand/collapse test passed")


@allure.feature("RFP 项目管理")
@allure.story("报价详情页价格状态变更")
class TestRFPDetailPagePriceStatus:
    """RFP 报价详情页价格状态变更测试"""

    PRICE_DETAIL_STATUS_CASES = TestDataLoader.load_params(
        "rfp_management_params.json",
        "rfp_detail_page_price_status",
    )

    JUMP_CASES = [c for c in PRICE_DETAIL_STATUS_CASES if not c.get("import_status")]
    PRICE_CHANGE_CASES = [c for c in PRICE_DETAIL_STATUS_CASES if c.get("import_status")]

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "case_data",
        JUMP_CASES,
        ids=[case["case_id"] for case in JUMP_CASES],
    )
    @allure.title("验证报价详情页去签约跳转")
    @allure.description("""
    测试: Operate 角色在已启动 Tab 中点击去签约按钮，验证进入评标/签约地图页面。

    测试流程:
    1. 使用 Operate 角色账号登录
    2. 进入 /home 页面
    3. 点击菜单: 签约管理 > 签约
    4. 切换到已启动 Tab
    5. 搜索指定项目
    6. 点击首个去签约按钮
    7. 验证当前页面 URL 包含 bidEvaluationDetails

    预期结果:
    - 点击去签约后，页面 URL 包含 bidEvaluationDetails 关键字
    """)
    async def test_priceDetail_startAction_priceDetail2jump(
        self, page_module, operate_user, case_data: dict
    ):
        """验证已启动项目点击去签约跳转到评标页面"""
        project_name = case_data["project_name"]

        logger.info(
            f"Starting detail price jump test, case: {case_data['case_id']}, project: {project_name}"
        )

        map_page = RFPContractMapPage(page_module)

        with allure.step("【步骤 1】进入 /home 页面"):
            await map_page.navigate_to_home()

        with allure.step("【步骤 2】点击菜单进入签约页面"):
            await map_page.navigate_to_contracting()

        with allure.step("【步骤 3】切换到已启动 Tab"):
            await map_page.click_started_tab()

        with allure.step(f"【步骤 4】搜索项目: {project_name}"):
            await map_page.search_project(project_name)

        with allure.step("【步骤 5】点击首个去签约按钮"):
            await map_page.click_first_go_contracting_button()

        with allure.step("【步骤 6】验证 URL 包含 bidEvaluationDetails"):
            current_url = await map_page.get_current_url()
            has_keyword = map_page.url_contains_bid_evaluation(current_url)
            assert has_keyword, (
                f"去签约按钮跳转失败，跳转页面 URL 未包含 "
                f"[bidEvaluationDetails]，实际 URL: {current_url}"
            )

        result_report = f"""
        [OK] RFP 报价详情页去签约跳转验证测试完成

        【测试用例】
        - case_id: {case_data['case_id']}
        - description: {case_data['description']}
        - 项目名称: {project_name}

        【测试结果】
        - 跳转 URL: {current_url}
        - URL 包含 bidEvaluationDetails: {has_keyword}
        - 测试状态: 通过
        """
        allure.attach(result_report, "测试结果", allure.attachment_type.TEXT)

        logger.info("RFP detail price jump test passed")

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "case_data",
        PRICE_CHANGE_CASES,
        ids=[case["case_id"] for case in PRICE_CHANGE_CASES],
    )
    @allure.title("验证报价详情页价格状态变更")
    @allure.description("""
    测试: Operate 角色在签约地图界面中，通过报价详情页进行价格状态变更操作。

    测试流程:
    1. 使用 Operate 角色账号登录
    2. 进入 /home 页面
    3. 点击菜单: 签约管理 > 签约
    4. 切换到已启动 Tab
    5. 搜索指定项目
    6. 点击首个去签约按钮
    7. 切换到列表模式
    8. 导入签约状态 Excel 文件，将酒店置为指定初始状态
    9. 切换回地图模式
	10. 点击初始价格状态页签
	11. 点击首个酒店
	12. 点击查看报价详情按钮，打开报价详情页
	13. 在报价详情页执行操作（继续议价/确认中签/否决报价）
	14. 输入留言
	15. 点击确定
	16. 关闭报价详情页，回到地图页面
	17. 点击目标价格状态页签
	18. 验证目标价格页签下存在酒店

    预期结果:
    - 导入签约状态成功
    - 报价详情页打开成功
    - 操作执行成功
    - 目标价格页签下存在酒店
    """)
    async def test_priceDetail_price_status_change(
        self, page_module, operate_user, case_data: dict
    ):
        """验证报价详情页价格状态变更"""
        project_name = case_data["project_name"]
        hotel_id = case_data["hotel_id"]
        import_status = case_data["import_status"]
        initial_price_tab = case_data["initial_price_tab"]
        action = case_data["action"]
        target_price_tab = case_data["target_price_tab"]
        message = case_data["message"]
        case_id = case_data["case_id"]

        logger.info(
            f"Starting detail page price status change test, case: {case_id}, "
            f"project: {project_name}, {import_status} → {target_price_tab}"
        )

        map_page = RFPContractMapPage(page_module)

        # ===== 导航 =====
        with allure.step("【步骤 1】进入 /home 页面"):
            await map_page.navigate_to_home()

        with allure.step("【步骤 2】点击菜单进入签约页面"):
            await map_page.navigate_to_contracting()

        with allure.step("【步骤 3】切换到已启动 Tab"):
            await map_page.click_started_tab()

        with allure.step(f"【步骤 4】搜索项目: {project_name}"):
            await map_page.search_project(project_name)

        with allure.step("【步骤 5】点击首个去签约按钮"):
            await map_page.click_first_go_contracting_button()

        # ===== 生成并导入签约状态 =====
        excel_file_name = f"RFP_detail_import_{case_id}.xlsx"
        excel_path = generate_signing_status_excel(
            header=["房仓酒店id", "签约状态枚举值", "留言（文本最大500字符）"],
            data_rows=[[hotel_id, import_status, ""]],
            file_name=excel_file_name,
        )
        allure.attach(
            f"酒店ID: {hotel_id}, 导入状态: {import_status}",
            "签约状态导入文件内容",
            allure.attachment_type.TEXT,
        )

        with allure.step("【步骤 6】切换到列表模式"):
            await map_page.switch_to_list_mode()

        with allure.step(f"【步骤 7】导入签约状态: {import_status}"):
            await map_page.import_signing_status_file(excel_path)

        with allure.step("【步骤 8】切换回地图模式"):
            await map_page.switch_to_map_mode()

        # ===== 打开报价详情页并执行操作 =====
        with allure.step(f"【步骤 9】点击价格状态页签: {initial_price_tab}"):
            await map_page.click_price_status_tab(initial_price_tab)

        with allure.step("【步骤 10】点击首个酒店"):
            await map_page.click_first_hotel()

        with allure.step("【步骤 11】点击查看报价详情按钮"):
            detail_popup = await map_page.click_first_view_bid_detail()

        try:
            # 使用报价详情页对象进行操作
            detail_page = RFPDetailPageProject(detail_popup)

            with allure.step(f"【步骤 12】在报价详情页执行操作: {action}"):
                await detail_page.click_action_by_type(action)

            with allure.step(f"【步骤 13】输入留言: {message}"):
                await detail_page.fill_action_message(message)

            with allure.step("【步骤 14】点击确定"):
                await detail_page.click_action_confirm()

        finally:
            # ===== 关闭详情页，回到地图页面验证 =====
            with allure.step("【步骤 15】关闭报价详情页"):
                if not detail_popup.is_closed():
                    await detail_popup.close()

        with allure.step(f"【步骤 16】点击目标价格状态页签: {target_price_tab}"):
            await map_page.click_price_status_tab(target_price_tab)

        with allure.step("【步骤 17】验证目标价格页签下存在酒店"):
            hotel_exists = await map_page.verify_hotel_exists()
            assert hotel_exists, (
                f"切换至 [{target_price_tab}] 价格页签后，"
                f"未找到对应的酒店，状态变更可能未生效"
            )

        result_report = f"""
        [OK] RFP 报价详情页价格状态变更测试完成

        【测试用例】
        - case_id: {case_id}
        - description: {case_data['description']}
        - 项目名称: {project_name}

        【价格变更流程】
        - 导入状态: {import_status}
        - 初始价格页签: {initial_price_tab}
        - 执行操作: {action}
        - 留言内容: {message}
        - 目标价格页签: {target_price_tab}

        【测试结果】
        - 签约状态文件已导入: {excel_path}
        - 报价详情页操作执行成功
        - 目标页签 [{target_price_tab}] 酒店存在: {hotel_exists}
        - 测试状态: 通过
        """
        allure.attach(result_report, "测试结果", allure.attachment_type.TEXT)

        logger.info(
            f"RFP detail page price status change test passed: {import_status} → {target_price_tab}"
        )
