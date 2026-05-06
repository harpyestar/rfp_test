"""
RFP 签约价格状态变更测试
测试场景: 验证 Operate 角色在签约地图界面中的价格状态变更操作
涵盖：去签约跳转、新标→议价中/中签/否决、议价中→中签/否决、
修订报价→议价中/中签/否决、保持原价→议价中/中签/否决
"""

import allure
import pytest
from pages.operate.rfp_management.rfp_contract_map_page import RFPContractMapPage
from utils.config import config
from utils.logger import get_logger
from utils.test_data_loader import TestDataLoader
from utils.excel_utils import generate_signing_status_excel

logger = get_logger(
    "tests.operate.rfp_management.test_rfp_contract_price_status", config.log_level
)

ALL_PRICE_STATUS_CASES = TestDataLoader.load_params(
    "rfp_management_params.json",
    "rfp_contract_price_status",
)

# 去签约跳转验证用例（无 import_status 字段）
JUMP_CASES = [c for c in ALL_PRICE_STATUS_CASES if not c.get("import_status")]

# 价格状态变更用例（有 import_status 字段）
PRICE_CHANGE_CASES = [c for c in ALL_PRICE_STATUS_CASES if c.get("import_status")]

@allure.feature("RFP 项目管理")
@allure.story("签约价格状态变动")
class TestRFPContractPriceStatus:
    """RFP 签约价格状态变更测试"""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "case_data",
        JUMP_CASES,
        ids=[case["case_id"] for case in JUMP_CASES],
    )
    @allure.title("验证已启动项目点击去签约跳转到评标页面")
    @allure.description("""
    测试: Operate 角色在已启动 Tab 中点击去签约按钮，验证 URL 跳转到评标页面。

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
    - 表示成功跳转到评标/签约地图页面
    """)
    async def test_RFP_startAction_signing2jump(
        self, page_module, operate_user, case_data: dict
    ):
        """验证已启动项目点击去签约跳转到评标页面"""
        project_name = case_data["project_name"]

        logger.info(
            f"Starting signing jump test, case: {case_data['case_id']}, project: {project_name}"
        )

        map_page = RFPContractMapPage(page_module)

        with allure.step(f"【步骤 1】进入 /home 页面"):
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
        [OK] RFP 去签约跳转验证测试完成

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

        logger.info("RFP signing jump test passed")

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "case_data",
        PRICE_CHANGE_CASES,
        ids=[case["case_id"] for case in PRICE_CHANGE_CASES]
    )
    @allure.title("验证签约地图界面价格状态变更")
    @allure.description("""
    测试: Operate 角色在签约地图界面中，对指定酒店进行价格状态变更操作，
    验证状态变更成功后目标价格页签下存在酒店。

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
    12. 执行操作（继续议价/中签/否决）
    13. 输入留言
    14. 点击确定
    15. 点击目标价格状态页签
    16. 验证目标价格页签下存在酒店

    预期结果:
    - 导入签约状态成功
    - 操作执行成功
    - 目标价格页签下存在酒店
    """)
    async def test_RFP_contract_price_status_change(
        self, page_module, operate_user, case_data: dict
    ):
        """验证签约地图界面价格状态变更"""
        project_name = case_data["project_name"]
        hotel_id = case_data["hotel_id"]
        import_status = case_data["import_status"]
        initial_price_tab = case_data["initial_price_tab"]
        action = case_data["action"]
        target_price_tab = case_data["target_price_tab"]
        message = case_data["message"]
        case_id = case_data["case_id"]

        logger.info(
            f"Starting price status change test, case: {case_id}, "
            f"project: {project_name}, {import_status} → {target_price_tab}"
        )

        map_page = RFPContractMapPage(page_module)

        # ===== 导航 =====
        with allure.step(f"【步骤 1】进入 /home 页面"):
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
        excel_file_name = f"RFP_import_signing_status_{case_id}.xlsx"
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

        # ===== 执行价格变更 =====
        with allure.step(f"【步骤 9】点击价格状态页签: {initial_price_tab}"):
            await map_page.click_price_status_tab(initial_price_tab)

        with allure.step("【步骤 10】点击首个酒店"):
            await map_page.click_first_hotel()

        with allure.step(f"【步骤 11】执行操作: {action}"):
            await map_page.click_action_by_type(action)

        with allure.step(f"【步骤 12】输入留言: {message}"):
            await map_page.fill_message(message)

        with allure.step("【步骤 13】点击确定"):
            await map_page.click_confirm()

        # ===== 验证 =====
        with allure.step(f"【步骤 14】点击目标价格状态页签: {target_price_tab}"):
            await map_page.click_price_status_tab(target_price_tab)

        with allure.step("【步骤 15】验证目标价格页签下存在酒店"):
            hotel_exists = await map_page.verify_hotel_exists()
            assert hotel_exists, (
                f"切换至 [{target_price_tab}] 价格页签后，"
                f"未找到对应的酒店，状态变更可能未生效"
            )

        result_report = f"""
        [OK] RFP 签约价格状态变更测试完成

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
        - 操作执行成功
        - 目标页签 [{target_price_tab}] 酒店存在: {hotel_exists}
        - 测试状态: 通过
        """
        allure.attach(result_report, "测试结果", allure.attachment_type.TEXT)

        logger.info(
            f"RFP price status change test passed: {import_status} → {target_price_tab}"
        )
