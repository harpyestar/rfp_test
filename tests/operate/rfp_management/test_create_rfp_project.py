"""
创建 RFP 项目测试
测试场景: 验证 Operate 角色创建新 RFP 项目的完整流程
可变业务数据从 data/test_cases/rfp_management_params.json 读取
"""

import json
from datetime import datetime

import pytest
import allure

from pages.operate.rfp_management.create_rfp_project_page import CreateRFPProjectPage
from utils.config import config

# ======================================================================
# 从 JSON 加载参数化测试数据
# ======================================================================
_PARAMS_PATH = config.PROJECT_ROOT / "data" / "test_cases" / "rfp_management_params.json"

with open(_PARAMS_PATH, encoding="utf-8") as _f:
    _ALL_PARAMS = json.load(_f)

CREATE_PROJECT_TEST_DATA = _ALL_PARAMS["create_rfp_project"]


def generate_project_name(prefix: str) -> str:
    """生成唯一的签约项目名称（前缀 + 时间戳）"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{prefix}-{timestamp}"


@allure.feature("RFP 项目管理")
@allure.story("RFP 项目创建")
class TestCreateRFPProject:
    """创建 RFP 项目测试类"""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("project_data", CREATE_PROJECT_TEST_DATA)
    @allure.title("验证 Operate 创建新 RFP 项目流程")
    @allure.description("""
    测试: Operate 角色创建新的 RFP 项目，填写完整表单并保存

    测试流程:
    1. 使用 operate 角色账号登录 (fixture 自动完成)
    2. 导航至 签约管理 > 发布项目
    3. 填写签约机构、项目名称、联系人、联系电话
    4. 选择签约方式: 邀请签约
    5. 选择报名起止时间、第一轮报价起止时间、协议报价日期范围
    6. 填写预计签约酒店数量、公司差标最小值/最大值
    7. 点击保存并下一步
    8. 验证 Toast 成功提示

    预期结果:
    - 所有表单字段填写成功
    - 点击保存后出现操作成功/保存成功的 Toast 提示
    """)
    async def test_create_rfp_project(self, page_module, operate_user, project_data: dict):
        """
        验证创建新 RFP 项目的完整流程

        Args:
            page_module: Module 级 page 对象 - 复用登录状态
            operate_user: Operate 角色登录 fixture
            project_data: JSON 参数化的项目表单数据
        """
        project_name = generate_project_name(project_data["project_name_prefix"])

        create_page = CreateRFPProjectPage(page_module)

        # ========== Step 1: 导航 ==========
        with allure.step("【步骤 1】导航至 签约管理 > 发布项目"):
            await create_page.navigate_to_create_project()

        # ========== Step 2-6: 填写表单 ==========
        with allure.step(f"【步骤 2】填写签约机构: {project_data['agency_name']}"):
            await create_page.select_contracting_agency(project_data["agency_name"])

        with allure.step(f"【步骤 3】填写签约项目名称: {project_name}"):
            await create_page.fill_project_name(project_name)

        with allure.step(f"【步骤 4】填写联系人: {project_data['contact_person']}"):
            await create_page.fill_contact_person(project_data["contact_person"])

        with allure.step(f"【步骤 5】填写联系电话: {project_data['contact_phone']}"):
            await create_page.fill_contact_phone(project_data["contact_phone"])

        with allure.step("【步骤 6】选择签约方式: 邀请签约"):
            await create_page.select_invitation_sign_method()

        # ========== Step 7-9: 日期范围 ==========
        with allure.step(f"【步骤 7】选择报名起止时间（第{project_data['start_day']}-{project_data['end_day']}天）"):
            await create_page.select_registration_date(project_data["start_day"], project_data["end_day"])

        with allure.step(f"【步骤 8】选择第一轮报价起止时间（第{project_data['start_day']}-{project_data['end_day']}天）"):
            await create_page.select_first_round_date(project_data["start_day"], project_data["end_day"])

        with allure.step(f"【步骤 9】选择协议报价日期范围（第{project_data['start_day']}-{project_data['end_day']}天）"):
            await create_page.select_agreement_date(project_data["start_day"], project_data["end_day"])

        # ========== Step 10-12: 数值字段 ==========
        with allure.step(f"【步骤 10】填写预计签约酒店数量: {project_data['expected_hotel_count']}"):
            await create_page.fill_expected_hotel_count(project_data["expected_hotel_count"])

        with allure.step(f"【步骤 11】填写公司差标最小值: {project_data['min_diff_std']}"):
            await create_page.fill_min_diff_std(project_data["min_diff_std"])

        with allure.step(f"【步骤 12】填写公司差标最大值: {project_data['max_diff_std']}"):
            await create_page.fill_max_diff_std(project_data["max_diff_std"])

        # ========== Step 13-14: 保存并验证 ==========
        with allure.step("【步骤 13】点击保存并下一步"):
            await create_page.click_save_and_next()

        with allure.step("【步骤 14】验证保存成功 Toast"):
            toast_text = await create_page.verify_save_success()

            assert toast_text, "保存后未检测到 Toast 提示信息"
            assert any(
                keyword in toast_text
                for keyword in ["成功", "操作成功", "保存成功"]
            ), f"Toast 内容不包含成功关键词，实际内容: {toast_text}"

        # ========== Step 15-18: 清理 - 作废项目 ==========
        with allure.step("【步骤 15】导航至签约管理页面"):
            await create_page.navigate_to_contracting()

        with allure.step("【步骤 16】选择未启动 Tab"):
            await create_page.click_not_started_tab()

        with allure.step(f"【步骤 17】搜索刚创建的项目: {project_name}"):
            await create_page.search_project_by_name(project_name)

        with allure.step("【步骤 18】作废项目（清理数据）"):
            await create_page.void_first_project()

        # 测试报告
        report = f"""
        [OK] 创建 RFP 项目测试完成

        【测试项目】
        - 项目名称: {project_name}

        【测试数据】（来自 rfp_management_params.json）
        - case_id: {project_data.get('case_id', 'N/A')}
        - 签约机构: {project_data['agency_name']}
        - 联系人: {project_data['contact_person']}
        - 联系电话: {project_data['contact_phone']}
        - 预计签约酒店数量: {project_data['expected_hotel_count']}
        - 公司差标: {project_data['min_diff_std']} ~ {project_data['max_diff_std']}

        【验证结果】
        - Toast 提示: {toast_text}
        - 测试状态: 通过 ✓
        """
        allure.attach(report, "测试结果报告", allure.attachment_type.TEXT)
        
