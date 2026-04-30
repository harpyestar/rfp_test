"""
酒店集团折扣报价测试
"""

import allure
import pytest
from pages.hotel_group.contract_management.hotel_group_discount_price_page import (
    HotelGroupDiscountPricePage,
)
from utils.config import config
from utils.logger import get_logger
from utils.test_data_loader import TestDataLoader

logger = get_logger("tests.hotel_group.contract_management.test_hotel_group_discount_price", config.log_level)

HOTEL_GROUP_DISCOUNT_PRICE_CASES = TestDataLoader.load_params(
    "rfp_hotel_group_contract_params.json",
    "hotel_group_discount_price",
)


@allure.feature("酒店集团端合同管理")
@allure.story("集团折扣报价")
@pytest.mark.hotelgroup
@pytest.mark.regression
@pytest.mark.mark_20260507
class TestHotelGroupDiscountPrice:
    """酒店集团折扣报价测试"""

    @pytest.mark.parametrize(
        "case_data",
        HOTEL_GROUP_DISCOUNT_PRICE_CASES,
        ids=[case["case_id"] for case in HOTEL_GROUP_DISCOUNT_PRICE_CASES],
    )
    @pytest.mark.asyncio
    @pytest.mark.mark_20260507
    @allure.title("验证集团折扣详情页不会出现项目签约时间结束提示")
    @allure.description("""
    测试: HotelGroup 角色进入集团折扣详情页时，验证不会出现"项目签约时间已经结束"提示。

    测试流程:
    1. 使用 HotelGroup 角色账号登录
    2. 进入酒店集团端首页
    3. 点击"签约项目"菜单并进入签约项目页面
    4. 切换到"项目报价总览"Tab
    5. 搜索指定项目名称
    6. 点击搜索结果首项中的"集团折扣"按钮
    7. 验证进入详情页后不会出现"项目签约时间已经结束"toast

    预期结果:
    - 成功进入集团折扣详情页
    - 页面上不会出现"项目签约时间已经结束"提示
    """)
    async def test_hotel_group_discount_price_no_expired_toast(
        self,
        page_module,
        hotel_group_user,
        case_data: dict,
    ):
        """验证进入集团折扣详情时不会出现项目签约时间结束提示"""
        project_name = case_data["project_name"]
        logger.info(
            f"Starting hotel group discount price test, case: {case_data['case_id']}, project: {project_name}"
        )

        discount_price_page = HotelGroupDiscountPricePage(page_module)

        with allure.step("【步骤 1】进入酒店集团首页"):
            await discount_price_page.navigate_to_home()

        with allure.step("【步骤 2】打开签约项目菜单"):
            await discount_price_page.open_contract_project_menu()

        with allure.step("【步骤 3】切换到项目报价总览 Tab"):
            await discount_price_page.select_project_quotation_overview_tab()

        with allure.step(f"【步骤 4】搜索项目: {project_name}"):
            await discount_price_page.search_project(project_name)

        with allure.step("【步骤 5】点击首个集团折扣按钮"):
            await discount_price_page.click_first_group_discount_button()

        with allure.step("【步骤 6】等待进入集团折扣详情页"):
            await discount_price_page.wait_for_discount_detail_page()

        with allure.step("【步骤 7】验证不会出现项目签约时间已经结束提示"):
            has_expired_toast = await discount_price_page.has_expired_toast()
            assert has_expired_toast is False, "进入集团折扣详情页后，出现了toast: 项目签约时间已经结束"

        result_report = f"""
        [OK] 酒店集团端集团折扣报价测试完成

        【测试用例】
        - case_id: {case_data['case_id']}
        - description: {case_data['description']}
        - 项目名称: {project_name}

        【测试结果】
        - 成功进入集团折扣详情页
        - 未出现toast: 项目签约时间已经结束
        - 测试状态: 通过
        """
        allure.attach(result_report, "测试结果", allure.attachment_type.TEXT)

        logger.info("Hotel group discount price test passed")
