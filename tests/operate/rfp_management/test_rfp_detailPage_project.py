"""
RFP 报价详情页内部跟进备注测试
"""

from datetime import datetime
import allure
import pytest
from pages.operate.rfp_management.rfp_detailPage_project import RFPDetailPageProject
from utils.config import config
from utils.logger import get_logger
from utils.test_data_loader import TestDataLoader

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
