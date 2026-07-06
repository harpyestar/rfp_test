"""
E2E 跨端价格状态流转测试

测试场景: Operate 平台端 ↔ Hotel 酒店端 跨端价格状态变更

核心流程:
  Phase 1 - Operate: 签约项目 → 导入Excel设置酒店为"议价中"
  Phase 2 - Hotel:   报价项目 → 搜索 → 修改报价 → 提交报价
  Phase 3 - Operate: 修订报价Tab → 中签操作 → 验证已中签

架构说明:
  - 双 context（operate + hotel），cookies 完全隔离
  - Operate 侧复用 RFPContractMapPage
  - Hotel 侧使用 HotelBiddingPage（新建）
"""

import allure
import pytest
from pages.operate.rfp_management.rfp_contract_map_page import RFPContractMapPage
from pages.hotel.contracting.hotel_bidding_page import HotelBiddingPage
from utils.excel_utils import generate_signing_status_excel
from utils.logger import get_logger
from utils.test_data_loader import TestDataLoader

logger = get_logger("tests.e2e.test_cross_end_price_status_flow")

# 加载 E2E 参数化数据
CROSS_END_CASES = TestDataLoader.load_params(
    "e2e_params.json",
    "cross_end_price_status",
)


@allure.feature("E2E 跨端流程")
@allure.story("价格状态流转 - 平台端⇄酒店端")
class TestCrossEndPriceStatusFlow:
    """跨端价格状态流转测试"""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "case_data",
        CROSS_END_CASES,
        ids=[case["case_id"] for case in CROSS_END_CASES],
    )
    @allure.title("平台端置酒店议价中→酒店端提交报价→平台端中签")
    @allure.description("""
    测试: Operate 将酒店置为议价中 → Hotel 收到后提交报价 → Operate 操作中签

    测试流程:
    1. Operate 登录 → 签约管理 → 去签约 → 导入Excel(酒店状态→议价中)
    2. Hotel 登录 → 报价项目 → 议价中Tab → 修改报价 → 提交报价
    3. Operate → 修订报价Tab → 中签操作 → 验证酒店在已中签页签

    预期结果:
    - 酒店端提交报价成功（出现"操作成功"toast）
    - 平台端修订报价页签下存在酒店
    - 中签操作后酒店出现在已中签页签
    """)
    async def test_cross_end_price_status_flow(
        self, e2e_pages, case_data: dict
    ):
        """跨端价格状态流转测试"""
        operate_page = e2e_pages["operate"]
        hotel_page = e2e_pages["hotel"]

        project_name = case_data["project_name"]
        hotel_id = case_data["hotel_id"]
        hotel_name = case_data["hotel_name"]
        import_status = case_data["import_status"]
        message = case_data["message"]

        # ================================================================
        # Phase 1: Operate - 平台端操作
        # ================================================================
        map_page = RFPContractMapPage(operate_page)

        with allure.step("【Phase 1-1】进入 /home 页面"):
            await map_page.navigate_to_home()

        with allure.step("【Phase 1-2】点击菜单进入签约页面"):
            await map_page.navigate_to_contracting()

        with allure.step("【Phase 1-3】切换到已启动 Tab"):
            await map_page.click_started_tab()

        with allure.step(f"【Phase 1-4】搜索项目: {project_name}"):
            await map_page.search_project(project_name)

        with allure.step("【Phase 1-5】点击首个去签约按钮"):
            await map_page.click_first_go_contracting_button()

        # 生成签约状态导入 Excel
        excel_file_name = f"RFP_e2e_import_{case_data['case_id']}.xlsx"
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

        with allure.step("【Phase 1-6】切换到列表签约"):
            await map_page.switch_to_list_mode()

        with allure.step(f"【Phase 1-7】导入签约状态: {import_status}"):
            await map_page.import_signing_status_file(excel_path)

        with allure.step("【Phase 1-8】切换回地图签约"):
            await map_page.switch_to_map_mode()

        # ================================================================
        # Phase 2: Hotel - 酒店端操作
        # ================================================================
        hotel_bidding = HotelBiddingPage(hotel_page)

        with allure.step("【Phase 2-1】进入酒店端工作台"):
            await hotel_bidding.navigate_to_home()

        with allure.step("【Phase 2-2】点击报价项目"):
            await hotel_bidding.click_bidding_project()

        with allure.step("【Phase 2-3】点击议价中 Tab"):
            await hotel_bidding.click_negotiating_tab()

        with allure.step(f"【Phase 2-4】搜索项目: {project_name}, 酒店: {hotel_name}"):
            await hotel_bidding.search(project_name, hotel_name)

        with allure.step("【Phase 2-5】点击修改报价"):
            await hotel_bidding.click_modify_quote()

        with allure.step("【Phase 2-6】关闭备注留言弹窗"):
            await hotel_bidding.close_remark_dialog()

        with allure.step("【Phase 2-7】点击提交报价"):
            await hotel_bidding.click_submit_quote()

        with allure.step("【Phase 2-8】确认弹窗① - 当前报价未维护不适用日期"):
            await hotel_bidding.click_confirm()

        with allure.step("【Phase 2-9】确认弹窗② - 是否确定提交报价"):
            await hotel_bidding.click_confirm()

        with allure.step("【Phase 2-10】验证操作成功"):
            success = await hotel_bidding.is_toast_success()
            assert success, "提交报价后未出现'操作成功' toast"

        # ================================================================
        # Phase 3: Operate - 平台端中签操作
        # ================================================================
        with allure.step("【Phase 3-1】点击修订报价页签"):
            await map_page.click_price_status_tab("修订报价")

        with allure.step(f"【Phase 3-2】验证酒店存在于修订报价页签"):
            hotel_exists = await map_page.verify_hotel_exists()
            assert hotel_exists, (
                f"修订报价页签下未找到酒店 [{hotel_name}]，"
                f"酒店端提交报价后状态可能未变更"
            )

        with allure.step("【Phase 3-3】点击首个酒店"):
            await map_page.click_first_hotel()

        with allure.step("【Phase 3-4】点击中签按钮"):
            await map_page.click_hotel_signed()

        with allure.step(f"【Phase 3-5】输入留言"):
            await map_page.fill_message(message)

        with allure.step("【Phase 3-6】点击确定"):
            await map_page.click_confirm()

        with allure.step("【Phase 3-7】点击已中签页签"):
            await map_page.click_price_status_tab("已中签")

        with allure.step("【Phase 3-8】验证酒店存在于已中签页签"):
            hotel_in_signed = await map_page.verify_hotel_exists()
            assert hotel_in_signed, (
                "已中签页签下未找到酒店，中签操作可能未生效"
            )

        # ===== 报告 =====
        result_report = f"""
        [OK] E2E 跨端价格状态流转测试通过

        【用例】
        - case_id: {case_data['case_id']}
        - 项目名称: {project_name}
        - 酒店: {hotel_name} (ID: {hotel_id})

        【流转路径】
        Phase 1 - Operate: 导入Excel → 签约状态: {import_status}
        Phase 2 - Hotel: 提交报价 → 操作成功 ✓
        Phase 3 - Operate: 中签操作 → 酒店出现在已中签页签 ✓

        【测试结果】通过
        """
        allure.attach(result_report, "测试结果", allure.attachment_type.TEXT)
        logger.info("E2E 跨端价格状态流转测试通过")