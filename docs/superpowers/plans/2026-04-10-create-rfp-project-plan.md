# 创建新 RFP 项目功能测试 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现 RFP 项目创建功能的自动化测试，包括 POM 类、测试用例、元素定位探索、双层日志集成。

**Architecture:** 
- 使用 playwright-skill 探索实际页面元素选择器
- 创建细粒度 POM 类 (CreateNewRFPProjectPage)，分离各字段的填充逻辑
- 实现单一完整测试用例，验证端到端流程
- 集成文件日志和 Allure 报告，实现双层日志记录

**Tech Stack:** pytest + pytest-asyncio + Playwright + Allure + Logger单例

---

## 📋 文件结构映射

**新建文件：**
- `pages/operate/rfp_management/__init__.py` - 空文件
- `pages/operate/rfp_management/create_rfp_project_page.py` - CreateNewRFPProjectPage POM 类
- `tests/operate/rfp_management/__init__.py` - 空文件  
- `tests/operate/rfp_management/test_create_rfp_project.py` - 测试用例

**修改文件：** 无

**日志目录：**
- `reports/logs/` - 创建目录（运行时自动生成日志文件）

---

## 🎯 Task 分解

### Task 1: 使用 playwright-skill 探索页面元素和选择器

**Files:**
- Reference: `pages/operate/rfp_management/create_rfp_project_page.py` (待创建，占位符)

**目标:** 获取实际页面的元素选择器，为后续代码编写提供基础

- [ ] **Step 1: 使用 playwright-skill 访问应用**

使用 playwright-skill 完成以下探索任务：

```
探索目标页面：RFP Management > Create new RFP project 页面

需要定位的元素：

1. 导航菜单
   - RFP Management 菜单项选择器
   - Create new RFP project 下拉菜单项选择器

2. 表单字段
   - Organization Name 输入框选择器
   - Project Name 输入框选择器
   - Contact Person 输入框选择器
   - Area Code 输入框选择器 (联系电话第一部分)
   - Phone Number 输入框选择器 (联系电话第二部分)

3. 单选框和下拉菜单
   - Method of Signing 单选框 - "Private RFP" 选项选择器
   - Signing Status Notification Method - "Manual Notification" 选择器
   - GROUP QUOTATION STATUS REPORT - "NO NEED" 选择器
   - Enterprise Quotation Status Report - "NO NEED" 选择器

4. 日期选择器
   - Bidding Date Range 日期选择器（开始日期）选择器
   - Bidding Date Range 日期选择器（结束日期）选择器
   - Registration Period 日期选择器（开始日期）选择器
   - Registration Period 日期选择器（结束日期）选择器
   - First Round Bidding Period 日期选择器（开始日期）选择器
   - First Round Bidding Period 日期选择器（结束日期）选择器

5. 酒店数量字段
   - Expected number of contracted hotels 输入框选择器

6. 按钮
   - 保存按钮选择器

7. 成功提示
   - 成功提示信息容器选择器（toast/modal/alert）
   - 成功提示文本内容 (如 "Success!", "保存成功" 等)

请用 playwright-skill 逐一探索这些元素，获取正确的 CSS selector 或 data-* 定位符。
```

- [ ] **Step 2: 记录所有选择器信息**

在探索完成后，整理一份选择器参考表，包括：
- 元素名称
- 选择器类型 (CSS selector / data attribute / text selector)
- 选择器内容
- 元素类型 (input / button / radio / checkbox / select 等)
- 备注

例如：
```
导航菜单
- RFP Management: nav-item[data-menu="rfp_management"] 或 a:has-text("RFP Management")
- Create new RFP project: dropdown-item:has-text("Create new RFP project")

表单字段
- Organization Name input: input[name="organizationName"] 或 input[placeholder="Organization Name"]
- Project Name input: input[name="projectName"]
...
```

---

### Task 2: 创建页面对象类骨架 - 导入和选择器定义

**Files:**
- Create: `pages/operate/rfp_management/__init__.py`
- Create: `pages/operate/rfp_management/create_rfp_project_page.py` (骨架)

- [ ] **Step 1: 创建 __init__.py 文件**

```bash
touch /d/work_dev/GRFP/grfp-ui-test/pages/operate/rfp_management/__init__.py
```

- [ ] **Step 2: 创建 create_rfp_project_page.py 骨架**

创建文件 `pages/operate/rfp_management/create_rfp_project_page.py`，包含以下内容：

```python
"""
创建新 RFP 项目页面对象模型
负责 RFP 项目创建流程的所有交互操作
所有超时值从 timeout_config 中读取，所有选择器统一在类变量中定义
"""

from playwright.async_api import Page
from pages.common.base_page import BasePage
from utils.config import config
from utils.timeout_config import timeout_config
from utils.logger import get_logger
from datetime import datetime
import random
import allure


class CreateNewRFPProjectPage(BasePage):
    """创建新 RFP 项目 Page Object"""

    # ========== 导航菜单元素 ==========
    # 需要通过 playwright-skill 探索获得
    RFP_MANAGEMENT_MENU = None  # TODO: 通过 playwright-skill 探索获得
    CREATE_NEW_RFP_PROJECT_MENU = None  # TODO: 通过 playwright-skill 探索获得

    # ========== 表单字段元素 ==========
    # 需要通过 playwright-skill 探索获得
    ORGANIZATION_NAME_INPUT = None  # TODO: 通过 playwright-skill 探索获得
    PROJECT_NAME_INPUT = None  # TODO: 通过 playwright-skill 探索获得
    CONTACT_PERSON_INPUT = None  # TODO: 通过 playwright-skill 探索获得
    AREA_CODE_INPUT = None  # TODO: 通过 playwright-skill 探索获得
    PHONE_NUMBER_INPUT = None  # TODO: 通过 playwright-skill 探索获得

    # ========== 单选框和下拉菜单 ==========
    # 需要通过 playwright-skill 探索获得
    PRIVATE_RFP_RADIO = None  # TODO: 通过 playwright-skill 探索获得
    MANUAL_NOTIFICATION_OPTION = None  # TODO: 通过 playwright-skill 探索获得
    GROUP_QUOTATION_NO_NEED = None  # TODO: 通过 playwright-skill 探索获得
    ENTERPRISE_QUOTATION_NO_NEED = None  # TODO: 通过 playwright-skill 探索获得

    # ========== 日期选择器 ==========
    # 需要通过 playwright-skill 探索获得
    BIDDING_DATE_START_PICKER = None  # TODO: 通过 playwright-skill 探索获得
    BIDDING_DATE_END_PICKER = None  # TODO: 通过 playwright-skill 探索获得
    REGISTRATION_DATE_START_PICKER = None  # TODO: 通过 playwright-skill 探索获得
    REGISTRATION_DATE_END_PICKER = None  # TODO: 通过 playwright-skill 探索获得
    BIDDING_ROUND_DATE_START_PICKER = None  # TODO: 通过 playwright-skill 探索获得
    BIDDING_ROUND_DATE_END_PICKER = None  # TODO: 通过 playwright-skill 探索获得

    # ========== 其他字段 ==========
    EXPECTED_HOTELS_COUNT_INPUT = None  # TODO: 通过 playwright-skill 探索获得
    SAVE_BUTTON = None  # TODO: 通过 playwright-skill 探索获得
    SUCCESS_MESSAGE_CONTAINER = None  # TODO: 通过 playwright-skill 探索获得

    def __init__(self, page: Page):
        super().__init__(page)
        self.logger = get_logger(self.__class__.__name__, config.log_level)

    # ========== 辅助方法 ==========
    def _generate_timestamp(self) -> str:
        """生成时间戳格式: YYYYMMDD-HHMMSS"""
        return datetime.now().strftime("%Y%m%d-%H%M%S")

    def _generate_random_hotels_count(self) -> int:
        """生成随机酒店数量: 1-50"""
        return random.randint(1, 50)

    # ========== 导航方法 ==========
    async def navigate_to_create_rfp(self) -> None:
        """导航至创建新 RFP 项目页面"""
        self.logger.info("开始导航至创建新 RFP 项目页面")
        # 实现待完成
        pass

    # ========== 表单填充方法 ==========
    async def fill_organization_name(self, org_name: str = "hyg测试机构") -> None:
        """填写组织名称"""
        self.logger.info(f"开始填写组织名称: {org_name}")
        # 实现待完成
        pass

    async def fill_project_name(self) -> str:
        """填写项目名称（自动生成）"""
        self.logger.info("开始填写项目名称")
        # 实现待完成
        pass

    async def fill_contact_person(self, person: str = "荷叶") -> None:
        """填写联系人"""
        self.logger.info(f"开始填写联系人: {person}")
        # 实现待完成
        pass

    async def fill_contact_number(self, area_code: str, phone: str) -> None:
        """填写联系电话（区号 + 电话号码）"""
        self.logger.info(f"开始填写联系电话: {area_code} {phone}")
        # 实现待完成
        pass

    # ========== 选择器方法 ==========
    async def select_signing_method(self) -> None:
        """选择签约方式: Private RFP"""
        self.logger.info("开始选择签约方式: Private RFP")
        # 实现待完成
        pass

    async def select_notification_method(self) -> None:
        """选择通知方式: Manual Notification"""
        self.logger.info("开始选择通知方式: Manual Notification")
        # 实现待完成
        pass

    async def handle_quotation_reports(self) -> None:
        """设置报价报告为 NO NEED"""
        self.logger.info("开始设置报价报告为 NO NEED")
        # 实现待完成
        pass

    # ========== 日期选择方法 ==========
    async def select_bidding_dates(self, start_date: str, end_date: str) -> None:
        """选择招标日期范围"""
        self.logger.info(f"开始选择招标日期: {start_date} ~ {end_date}")
        # 实现待完成
        pass

    # ========== 数量输入方法 ==========
    async def fill_expected_hotels_count(self) -> int:
        """填写预期合同酒店数量（随机生成）"""
        self.logger.info("开始填写预期合同酒店数量")
        # 实现待完成
        pass

    # ========== 提交和验证方法 ==========
    async def click_save_button(self) -> None:
        """点击保存按钮"""
        self.logger.info("开始点击保存按钮")
        # 实现待完成
        pass

    async def verify_save_success(self) -> bool:
        """验证保存成功"""
        self.logger.info("开始验证保存成功")
        # 实现待完成
        pass
```

- [ ] **Step 3: 验证文件创建**

```bash
ls -la /d/work_dev/GRFP/grfp-ui-test/pages/operate/rfp_management/
```

预期输出：
```
__init__.py
create_rfp_project_page.py
```

- [ ] **Step 4: Commit**

```bash
cd /d/work_dev/GRFP/grfp-ui-test && git add pages/operate/rfp_management/ && git commit -m "feat: add CreateNewRFPProjectPage POM class skeleton with selectors placeholders"
```

---

### Task 3: 在 Task 1 获得选择器后，回填所有选择器值

**Files:**
- Modify: `pages/operate/rfp_management/create_rfp_project_page.py:10-50` (选择器定义部分)

**前置条件:** Task 1 已完成，已获得所有选择器信息

- [ ] **Step 1: 将 Task 1 获得的选择器填入类变量**

根据 Task 1 的探索结果，更新 `create_rfp_project_page.py` 中的所有选择器定义。

例如（实际选择器由 Task 1 探索结果决定）：

```python
class CreateNewRFPProjectPage(BasePage):
    # ========== 导航菜单元素 ==========
    RFP_MANAGEMENT_MENU = "a[data-menu='rfp_management']"  # 或其他实际选择器
    CREATE_NEW_RFP_PROJECT_MENU = "div[data-action='create_rfp']:has-text('Create new RFP project')"

    # ========== 表单字段元素 ==========
    ORGANIZATION_NAME_INPUT = "input[name='organizationName']"
    PROJECT_NAME_INPUT = "input[name='projectName']"
    CONTACT_PERSON_INPUT = "input[name='contactPerson']"
    AREA_CODE_INPUT = "input[name='areaCode']"
    PHONE_NUMBER_INPUT = "input[name='phoneNumber']"

    # ========== 单选框和下拉菜单 ==========
    PRIVATE_RFP_RADIO = "input[type='radio'][value='PRIVATE_RFP']"
    MANUAL_NOTIFICATION_OPTION = "select[name='notificationMethod'] option:has-text('Manual Notification')"
    GROUP_QUOTATION_NO_NEED = "input[type='radio'][name='groupQuotation'][value='NO_NEED']"
    ENTERPRISE_QUOTATION_NO_NEED = "input[type='radio'][name='enterpriseQuotation'][value='NO_NEED']"

    # ========== 日期选择器 ==========
    BIDDING_DATE_START_PICKER = "input[name='biddingDateStart']"
    BIDDING_DATE_END_PICKER = "input[name='biddingDateEnd']"
    REGISTRATION_DATE_START_PICKER = "input[name='registrationDateStart']"
    REGISTRATION_DATE_END_PICKER = "input[name='registrationDateEnd']"
    BIDDING_ROUND_DATE_START_PICKER = "input[name='roundDateStart']"
    BIDDING_ROUND_DATE_END_PICKER = "input[name='roundDateEnd']"

    # ========== 其他字段 ==========
    EXPECTED_HOTELS_COUNT_INPUT = "input[name='expectedHotelsCount']"
    SAVE_BUTTON = "button:has-text('Save') >> visible=true"
    SUCCESS_MESSAGE_CONTAINER = "div.el-message__content:has-text('Success')"
```

- [ ] **Step 2: 验证选择器语法**

确保所有选择器都是有效的 Playwright 选择器语法

- [ ] **Step 3: Commit**

```bash
cd /d/work_dev/GRFP/grfp-ui-test && git add pages/operate/rfp_management/create_rfp_project_page.py && git commit -m "feat: fill in element selectors from playwright exploration"
```

---

### Task 4: 实现导航方法

**Files:**
- Modify: `pages/operate/rfp_management/create_rfp_project_page.py:navigate_to_create_rfp()`

- [ ] **Step 1: 实现导航方法**

```python
async def navigate_to_create_rfp(self) -> None:
    """导航至创建新 RFP 项目页面"""
    self.logger.info("开始导航至创建新 RFP 项目页面")
    
    with allure.step("导航至 RFP Management > Create new RFP project"):
        try:
            # 1. 点击 RFP Management 菜单
            self.logger.debug(f"点击 RFP Management 菜单: {self.RFP_MANAGEMENT_MENU}")
            rfp_menu = await self.find_element(self.RFP_MANAGEMENT_MENU)
            await rfp_menu.click()
            self.logger.info("RFP Management 菜单已点击")
            
            # 2. 等待下拉菜单出现
            self.logger.debug("等待下拉菜单出现")
            await self.wait_helper.wait_for_selector(
                self.page,
                self.CREATE_NEW_RFP_PROJECT_MENU,
                timeout=timeout_config.get_element_timeout()
            )
            self.logger.info("下拉菜单已出现")
            
            # 3. 点击 Create new RFP project
            self.logger.debug(f"点击 Create new RFP project: {self.CREATE_NEW_RFP_PROJECT_MENU}")
            create_menu = await self.find_element(self.CREATE_NEW_RFP_PROJECT_MENU)
            await create_menu.click()
            self.logger.info("Create new RFP project 菜单项已点击")
            
            # 4. 等待表单加载完成（通过等待第一个表单字段）
            self.logger.debug("等待表单字段加载完成")
            await self.wait_helper.wait_for_selector(
                self.page,
                self.ORGANIZATION_NAME_INPUT,
                timeout=timeout_config.get_navigation_timeout()
            )
            
            allure.attach_text("导航成功，表单已加载", "导航结果")
            self.logger.info("导航成功，创建新 RFP 项目表单已加载")
            
        except Exception as e:
            error_msg = f"导航至创建页面失败: {str(e)}"
            self.logger.error(error_msg)
            allure.attach_text(error_msg, "导航错误")
            raise
```

- [ ] **Step 2: 运行快速测试验证方法签名**

```bash
cd /d/work_dev/GRFP/grfp-ui-test && python -c "from pages.operate.rfp_management.create_rfp_project_page import CreateNewRFPProjectPage; print('方法签名检查: OK')"
```

预期：无错误输出

- [ ] **Step 3: Commit**

```bash
cd /d/work_dev/GRFP/grfp-ui-test && git add pages/operate/rfp_management/create_rfp_project_page.py && git commit -m "feat: implement navigate_to_create_rfp method"
```

---

### Task 5: 实现表单字段填充方法

**Files:**
- Modify: `pages/operate/rfp_management/create_rfp_project_page.py` (fill_* 方法)

- [ ] **Step 1: 实现 fill_organization_name 方法**

```python
async def fill_organization_name(self, org_name: str = "hyg测试机构") -> None:
    """填写组织名称"""
    self.logger.info(f"开始填写组织名称: {org_name}")
    
    with allure.step(f"填写组织名称: {org_name}"):
        try:
            self.logger.debug(f"查找组织名称输入框: {self.ORGANIZATION_NAME_INPUT}")
            org_input = await self.find_element(self.ORGANIZATION_NAME_INPUT)
            await org_input.fill(org_name)
            allure.attach_text(f"组织名称: {org_name}", "填充数据")
            self.logger.info(f"组织名称填写成功: {org_name}")
        except Exception as e:
            error_msg = f"填写组织名称失败: {str(e)}"
            self.logger.error(error_msg)
            allure.attach_text(error_msg, "填充错误")
            raise
```

- [ ] **Step 2: 实现 fill_project_name 方法**

```python
async def fill_project_name(self) -> str:
    """填写项目名称（自动生成时间戳）"""
    self.logger.info("开始填写项目名称")
    
    with allure.step("填写项目名称"):
        try:
            timestamp = self._generate_timestamp()
            project_name = f"hyg-自动化项目-{timestamp}"
            
            self.logger.debug(f"查找项目名称输入框: {self.PROJECT_NAME_INPUT}")
            project_input = await self.find_element(self.PROJECT_NAME_INPUT)
            await project_input.fill(project_name)
            
            allure.attach_text(f"生成的项目名称: {project_name}", "项目名称")
            self.logger.info(f"项目名称填写成功: {project_name}")
            return project_name
        except Exception as e:
            error_msg = f"填写项目名称失败: {str(e)}"
            self.logger.error(error_msg)
            allure.attach_text(error_msg, "填充错误")
            raise
```

- [ ] **Step 3: 实现 fill_contact_person 方法**

```python
async def fill_contact_person(self, person: str = "荷叶") -> None:
    """填写联系人"""
    self.logger.info(f"开始填写联系人: {person}")
    
    with allure.step(f"填写联系人: {person}"):
        try:
            self.logger.debug(f"查找联系人输入框: {self.CONTACT_PERSON_INPUT}")
            contact_input = await self.find_element(self.CONTACT_PERSON_INPUT)
            await contact_input.fill(person)
            allure.attach_text(f"联系人: {person}", "填充数据")
            self.logger.info(f"联系人填写成功: {person}")
        except Exception as e:
            error_msg = f"填写联系人失败: {str(e)}"
            self.logger.error(error_msg)
            allure.attach_text(error_msg, "填充错误")
            raise
```

- [ ] **Step 4: 实现 fill_contact_number 方法**

```python
async def fill_contact_number(self, area_code: str, phone: str) -> None:
    """填写联系电话（区号 + 电话号码分两个字段）"""
    self.logger.info(f"开始填写联系电话: {area_code} {phone}")
    
    with allure.step(f"填写联系电话: {area_code} {phone}"):
        try:
            # 填写区号
            self.logger.debug(f"查找区号输入框: {self.AREA_CODE_INPUT}")
            area_input = await self.find_element(self.AREA_CODE_INPUT)
            await area_input.fill(area_code)
            self.logger.debug(f"区号填写成功: {area_code}")
            
            # 填写电话号码
            self.logger.debug(f"查找电话号码输入框: {self.PHONE_NUMBER_INPUT}")
            phone_input = await self.find_element(self.PHONE_NUMBER_INPUT)
            await phone_input.fill(phone)
            self.logger.debug(f"电话号码填写成功: {phone}")
            
            allure.attach_text(f"区号: {area_code}, 电话: {phone}", "联系电话")
            self.logger.info(f"联系电话填写成功: {area_code} {phone}")
        except Exception as e:
            error_msg = f"填写联系电话失败: {str(e)}"
            self.logger.error(error_msg)
            allure.attach_text(error_msg, "填充错误")
            raise
```

- [ ] **Step 5: Commit**

```bash
cd /d/work_dev/GRFP/grfp-ui-test && git add pages/operate/rfp_management/create_rfp_project_page.py && git commit -m "feat: implement form field filling methods (organization, project name, contact)"
```

---

### Task 6: 实现选择器方法（单选框、下拉菜单）

**Files:**
- Modify: `pages/operate/rfp_management/create_rfp_project_page.py` (select_* 和 handle_* 方法)

- [ ] **Step 1: 实现 select_signing_method 方法**

```python
async def select_signing_method(self) -> None:
    """选择签约方式: Private RFP"""
    self.logger.info("开始选择签约方式: Private RFP")
    
    with allure.step("选择签约方式: Private RFP"):
        try:
            self.logger.debug(f"查找 Private RFP 单选框: {self.PRIVATE_RFP_RADIO}")
            private_radio = await self.find_element(self.PRIVATE_RFP_RADIO)
            await private_radio.click()
            allure.attach_text("已选择: Private RFP", "签约方式")
            self.logger.info("Private RFP 已选中")
        except Exception as e:
            error_msg = f"选择签约方式失败: {str(e)}"
            self.logger.error(error_msg)
            allure.attach_text(error_msg, "选择错误")
            raise
```

- [ ] **Step 2: 实现 select_notification_method 方法**

```python
async def select_notification_method(self) -> None:
    """选择通知方式: Manual Notification"""
    self.logger.info("开始选择通知方式: Manual Notification")
    
    with allure.step("选择通知方式: Manual Notification"):
        try:
            self.logger.debug(f"查找 Manual Notification 选项: {self.MANUAL_NOTIFICATION_OPTION}")
            notification_option = await self.find_element(self.MANUAL_NOTIFICATION_OPTION)
            await notification_option.click()
            allure.attach_text("已选择: Manual Notification", "通知方式")
            self.logger.info("Manual Notification 已选中")
        except Exception as e:
            error_msg = f"选择通知方式失败: {str(e)}"
            self.logger.error(error_msg)
            allure.attach_text(error_msg, "选择错误")
            raise
```

- [ ] **Step 3: 实现 handle_quotation_reports 方法**

```python
async def handle_quotation_reports(self) -> None:
    """设置报价报告为 NO NEED"""
    self.logger.info("开始设置报价报告为 NO NEED")
    
    with allure.step("设置报价报告为 NO NEED"):
        try:
            # 设置 GROUP QUOTATION STATUS REPORT 为 NO NEED
            self.logger.debug(f"查找 GROUP QUOTATION 'NO NEED' 选项: {self.GROUP_QUOTATION_NO_NEED}")
            group_quota = await self.find_element(self.GROUP_QUOTATION_NO_NEED)
            await group_quota.click()
            self.logger.debug("GROUP QUOTATION STATUS REPORT 已设置为 NO NEED")
            
            # 设置 Enterprise Quotation Status Report 为 NO NEED
            self.logger.debug(f"查找 ENTERPRISE QUOTATION 'NO NEED' 选项: {self.ENTERPRISE_QUOTATION_NO_NEED}")
            enterprise_quota = await self.find_element(self.ENTERPRISE_QUOTATION_NO_NEED)
            await enterprise_quota.click()
            self.logger.debug("Enterprise Quotation Status Report 已设置为 NO NEED")
            
            allure.attach_text("GROUP QUOTATION STATUS: NO NEED\nEnterprise Quotation Status: NO NEED", "报价报告设置")
            self.logger.info("报价报告设置成功: 两个都设置为 NO NEED")
        except Exception as e:
            error_msg = f"设置报价报告失败: {str(e)}"
            self.logger.error(error_msg)
            allure.attach_text(error_msg, "设置错误")
            raise
```

- [ ] **Step 4: Commit**

```bash
cd /d/work_dev/GRFP/grfp-ui-test && git add pages/operate/rfp_management/create_rfp_project_page.py && git commit -m "feat: implement selector methods (signing method, notification, quotation reports)"
```

---

### Task 7: 实现日期选择方法

**Files:**
- Modify: `pages/operate/rfp_management/create_rfp_project_page.py:select_bidding_dates()`

**说明:** 日期选择通常涉及日历组件交互，可能需要根据实际 UI 调整

- [ ] **Step 1: 实现 select_bidding_dates 方法**

```python
async def select_bidding_dates(self, start_date: str, end_date: str) -> None:
    """
    选择三个日期范围：
    1. Bidding Date Range
    2. Registration Period
    3. First Round Bidding Period
    
    Args:
        start_date: 开始日期 (格式: YYYY-MM-DD, 例: 2026-04-10)
        end_date: 结束日期 (格式: YYYY-MM-DD, 例: 2026-05-10)
    """
    self.logger.info(f"开始选择日期范围: {start_date} ~ {end_date}")
    
    with allure.step(f"选择日期范围: {start_date} ~ {end_date}"):
        try:
            # 选择 Bidding Date Range
            self.logger.debug("开始选择 Bidding Date Range")
            await self._select_date_range(
                self.BIDDING_DATE_START_PICKER,
                self.BIDDING_DATE_END_PICKER,
                start_date,
                end_date,
                "Bidding Date Range"
            )
            
            # 选择 Registration Period
            self.logger.debug("开始选择 Registration Period")
            await self._select_date_range(
                self.REGISTRATION_DATE_START_PICKER,
                self.REGISTRATION_DATE_END_PICKER,
                start_date,
                end_date,
                "Registration Period"
            )
            
            # 选择 First Round Bidding Period
            self.logger.debug("开始选择 First Round Bidding Period")
            await self._select_date_range(
                self.BIDDING_ROUND_DATE_START_PICKER,
                self.BIDDING_ROUND_DATE_END_PICKER,
                start_date,
                end_date,
                "First Round Bidding Period"
            )
            
            allure.attach_text(
                f"Bidding Date Range: {start_date} ~ {end_date}\n"
                f"Registration Period: {start_date} ~ {end_date}\n"
                f"First Round Bidding Period: {start_date} ~ {end_date}",
                "日期范围"
            )
            self.logger.info(f"三个日期范围选择成功: {start_date} ~ {end_date}")
        except Exception as e:
            error_msg = f"选择日期范围失败: {str(e)}"
            self.logger.error(error_msg)
            allure.attach_text(error_msg, "日期选择错误")
            raise

async def _select_date_range(
    self,
    start_selector: str,
    end_selector: str,
    start_date: str,
    end_date: str,
    range_name: str
) -> None:
    """
    辅助方法：选择日期范围
    
    Args:
        start_selector: 开始日期选择器
        end_selector: 结束日期选择器
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
        range_name: 日期范围名称（用于日志）
    """
    self.logger.debug(f"_select_date_range: {range_name} - {start_date} ~ {end_date}")
    
    try:
        # 尝试直接填充开始日期
        self.logger.debug(f"填充 {range_name} 开始日期: {start_date}")
        start_input = await self.find_element(start_selector)
        await start_input.fill(start_date)
        self.logger.debug(f"{range_name} 开始日期填充成功")
        
        # 尝试直接填充结束日期
        self.logger.debug(f"填充 {range_name} 结束日期: {end_date}")
        end_input = await self.find_element(end_selector)
        await end_input.fill(end_date)
        self.logger.debug(f"{range_name} 结束日期填充成功")
        
    except Exception as e:
        self.logger.warning(f"直接填充日期失败，尝试日历交互: {str(e)}")
        # 如果直接填充失败，可能需要与日历组件交互
        # 这需要根据实际的 Element UI Calendar 组件进行调整
        # 示例代码（需要根据实际情况调整）：
        # await start_input.click()
        # await self.page.fill(calendar_input_selector, start_date)
        # await self.page.keyboard.press("Enter")
        raise Exception(f"选择 {range_name} 日期失败: {str(e)}")
```

- [ ] **Step 2: 验证日期格式**

确保所有日期字符串使用 YYYY-MM-DD 格式

- [ ] **Step 3: Commit**

```bash
cd /d/work_dev/GRFP/grfp-ui-test && git add pages/operate/rfp_management/create_rfp_project_page.py && git commit -m "feat: implement date range selection methods"
```

---

### Task 8: 实现酒店数量填充和保存/验证方法

**Files:**
- Modify: `pages/operate/rfp_management/create_rfp_project_page.py` (fill_expected_hotels_count, click_save_button, verify_save_success)

- [ ] **Step 1: 实现 fill_expected_hotels_count 方法**

```python
async def fill_expected_hotels_count(self) -> int:
    """填写预期合同酒店数量（随机生成 1-50）"""
    self.logger.info("开始填写预期合同酒店数量")
    
    with allure.step("填写预期合同酒店数量"):
        try:
            hotels_count = self._generate_random_hotels_count()
            self.logger.debug(f"生成随机酒店数量: {hotels_count}")
            
            self.logger.debug(f"查找酒店数量输入框: {self.EXPECTED_HOTELS_COUNT_INPUT}")
            count_input = await self.find_element(self.EXPECTED_HOTELS_COUNT_INPUT)
            await count_input.fill(str(hotels_count))
            
            allure.attach_text(f"预期合同酒店数量: {hotels_count}", "酒店数量")
            self.logger.info(f"预期合同酒店数量填写成功: {hotels_count}")
            return hotels_count
        except Exception as e:
            error_msg = f"填写酒店数量失败: {str(e)}"
            self.logger.error(error_msg)
            allure.attach_text(error_msg, "填充错误")
            raise
```

- [ ] **Step 2: 实现 click_save_button 方法**

```python
async def click_save_button(self) -> None:
    """点击保存按钮"""
    self.logger.info("开始点击保存按钮")
    
    with allure.step("点击保存按钮"):
        try:
            self.logger.debug(f"查找保存按钮: {self.SAVE_BUTTON}")
            save_btn = await self.find_element(self.SAVE_BUTTON)
            await save_btn.click()
            
            # 等待页面响应（可选：等待加载指示消失）
            self.logger.debug("等待页面响应")
            await self.page.wait_for_load_state("networkidle", timeout=timeout_config.get_navigation_timeout())
            
            allure.attach_text("保存按钮已点击", "操作结果")
            self.logger.info("保存按钮已点击，等待响应")
        except Exception as e:
            error_msg = f"点击保存按钮失败: {str(e)}"
            self.logger.error(error_msg)
            allure.attach_text(error_msg, "点击错误")
            raise
```

- [ ] **Step 3: 实现 verify_save_success 方法**

```python
async def verify_save_success(self) -> bool:
    """验证保存成功（检查成功提示信息）"""
    self.logger.info("开始验证保存成功")
    
    with allure.step("验证保存成功提示"):
        try:
            # 等待成功提示出现
            self.logger.debug(f"等待成功提示: {self.SUCCESS_MESSAGE_CONTAINER}")
            await self.wait_helper.wait_for_selector(
                self.page,
                self.SUCCESS_MESSAGE_CONTAINER,
                timeout=timeout_config.get_element_timeout()
            )
            
            # 获取提示文本
            success_msg = await self.page.locator(self.SUCCESS_MESSAGE_CONTAINER).text_content()
            self.logger.info(f"成功提示已出现: {success_msg}")
            
            # 验证提示是否可见
            is_visible = await self.page.locator(self.SUCCESS_MESSAGE_CONTAINER).is_visible()
            
            allure.attach_text(f"成功提示: {success_msg}\n可见: {is_visible}", "验证结果")
            self.logger.info(f"保存成功验证完成: {is_visible}")
            return is_visible
        except Exception as e:
            error_msg = f"验证保存成功失败: {str(e)}"
            self.logger.error(error_msg)
            allure.attach_text(error_msg, "验证错误")
            return False
```

- [ ] **Step 4: Commit**

```bash
cd /d/work_dev/GRFP/grfp-ui-test && git add pages/operate/rfp_management/create_rfp_project_page.py && git commit -m "feat: implement hotels count, save button, and verification methods"
```

---

### Task 9: 创建测试目录和测试用例文件

**Files:**
- Create: `tests/operate/rfp_management/__init__.py`
- Create: `tests/operate/rfp_management/test_create_rfp_project.py`

- [ ] **Step 1: 创建 tests 目录结构**

```bash
mkdir -p /d/work_dev/GRFP/grfp-ui-test/tests/operate/rfp_management
touch /d/work_dev/GRFP/grfp-ui-test/tests/operate/rfp_management/__init__.py
```

- [ ] **Step 2: 创建测试用例文件**

创建 `tests/operate/rfp_management/test_create_rfp_project.py`：

```python
"""
创建新 RFP 项目 - 功能测试
测试场景: Operate 角色完整创建 RFP 项目流程
"""

import pytest
import allure
from pages.operate.rfp_management.create_rfp_project_page import CreateNewRFPProjectPage


@pytest.mark.asyncio
@allure.title("创建新 RFP 项目 - 完整流程")
@allure.description("""
测试: Operate 角色成功创建新 RFP 项目，填写所有必填字段并保存

测试步骤:
1. 使用 operate 角色账号登录 (fixture 自动完成)
2. 导航至 Create new RFP project 页面
3. 填写项目基本信息 (组织、项目名、联系人、电话)
4. 选择签约方式和通知方式
5. 设置报价报告为 "NO NEED"
6. 选择三个日期范围 (2026-04-10 ~ 2026-05-10)
7. 填写预期酒店数量 (随机)
8. 点击保存
9. 断言成功提示出现

预期结果: 保存成功，显示成功提示信息
""")
async def test_create_rfp_project_success(page, operate_user):
    """
    完整的 RFP 项目创建流程测试
    
    Args:
        page: Playwright Page 对象 (fixture 提供)
        operate_user: Operate 角色登录 fixture (来自 conftest.py)
    """
    # 初始化 POM 类
    create_page = CreateNewRFPProjectPage(page)
    
    # Step 1: 导航至创建页面
    await create_page.navigate_to_create_rfp()
    
    # Step 2: 填写基本信息
    await create_page.fill_organization_name("hyg测试机构")
    project_name = await create_page.fill_project_name()
    await create_page.fill_contact_person("荷叶")
    await create_page.fill_contact_number("010", "12345678")
    
    # Step 3: 选择方式
    await create_page.select_signing_method()
    await create_page.select_notification_method()
    
    # Step 4: 设置报价报告
    await create_page.handle_quotation_reports()
    
    # Step 5: 选择日期范围
    await create_page.select_bidding_dates("2026-04-10", "2026-05-10")
    
    # Step 6: 填写酒店数量
    hotels_count = await create_page.fill_expected_hotels_count()
    
    # Step 7: 点击保存
    await create_page.click_save_button()
    
    # Step 8: 验证成功
    success = await create_page.verify_save_success()
    
    # Assertion
    assert success, "保存成功提示未出现，项目创建失败"
    
    # Allure 最终报告
    allure.attach_text(
        f"项目创建成功\n"
        f"项目名称: {project_name}\n"
        f"预期酒店数: {hotels_count}",
        "测试结果"
    )
```

- [ ] **Step 3: 验证文件创建**

```bash
ls -la /d/work_dev/GRFP/grfp-ui-test/tests/operate/rfp_management/
```

预期输出：
```
__init__.py
test_create_rfp_project.py
```

- [ ] **Step 4: Commit**

```bash
cd /d/work_dev/GRFP/grfp-ui-test && git add tests/operate/rfp_management/ && git commit -m "feat: add test case for RFP project creation"
```

---

### Task 10: 创建报告日志目录

**Files:**
- Create: `reports/logs/` 目录结构

- [ ] **Step 1: 创建日志目录**

```bash
mkdir -p /d/work_dev/GRFP/grfp-ui-test/reports/logs
touch /d/work_dev/GRFP/grfp-ui-test/reports/logs/.gitkeep
```

- [ ] **Step 2: 验证目录创建**

```bash
ls -la /d/work_dev/GRFP/grfp-ui-test/reports/
```

预期输出包含：
```
logs/
```

- [ ] **Step 3: Commit**

```bash
cd /d/work_dev/GRFP/grfp-ui-test && git add reports/logs/ && git commit -m "chore: add reports logs directory structure"
```

---

### Task 11: 验证整体代码完整性

**Files:**
- Reference: 所有已创建的文件

- [ ] **Step 1: 检查 Python 语法**

```bash
cd /d/work_dev/GRFP/grfp-ui-test && python -m py_compile pages/operate/rfp_management/create_rfp_project_page.py tests/operate/rfp_management/test_create_rfp_project.py
```

预期：无错误

- [ ] **Step 2: 检查导入**

```bash
cd /d/work_dev/GRFP/grfp-ui-test && python -c "
from pages.operate.rfp_management.create_rfp_project_page import CreateNewRFPProjectPage
from tests.operate.rfp_management.test_create_rfp_project import test_create_rfp_project_success
print('✓ 所有导入正确')
print('✓ CreateNewRFPProjectPage 可导入')
print('✓ test_create_rfp_project_success 可导入')
"
```

- [ ] **Step 3: 验证 POM 类方法签名**

```bash
cd /d/work_dev/GRFP/grfp-ui-test && python -c "
import inspect
from pages.operate.rfp_management.create_rfp_project_page import CreateNewRFPProjectPage

methods = [
    'navigate_to_create_rfp',
    'fill_organization_name',
    'fill_project_name',
    'fill_contact_person',
    'fill_contact_number',
    'select_signing_method',
    'select_notification_method',
    'handle_quotation_reports',
    'select_bidding_dates',
    'fill_expected_hotels_count',
    'click_save_button',
    'verify_save_success'
]

for method_name in methods:
    if hasattr(CreateNewRFPProjectPage, method_name):
        print(f'✓ {method_name} 已实现')
    else:
        print(f'✗ {method_name} 未实现')
"
```

- [ ] **Step 4: 检查日志和选择器初始化**

```bash
cd /d/work_dev/GRFP/grfp-ui-test && python -c "
from pages.operate.rfp_management.create_rfp_project_page import CreateNewRFPProjectPage
import inspect

# 检查选择器定义
source = inspect.getsource(CreateNewRFPProjectPage)
if 'RFP_MANAGEMENT_MENU' in source:
    print('✓ 选择器定义已包含')
else:
    print('✗ 选择器定义缺失')

# 检查 allure 导入
if 'import allure' in source:
    print('✓ Allure 导入正确')
else:
    print('✗ Allure 导入缺失')

# 检查 logger 导入
if 'get_logger' in source:
    print('✓ Logger 导入正确')
else:
    print('✗ Logger 导入缺失')
"
```

- [ ] **Step 5: 最终 commit**

```bash
cd /d/work_dev/GRFP/grfp-ui-test && git log --oneline -5
```

预期输出：显示近 5 个 commit，包括本次实现的各个步骤

---

## 📝 后续验证和集成步骤

这个实现计划的完成不包括实际运行测试（因为需要真实的浏览器和应用），但以下是后续验证步骤（由执行者在实际环境中完成）：

### 验证清单

- [ ] 运行 pytest 检查测试语法：`pytest tests/operate/rfp_management/test_create_rfp_project.py -v --collect-only`
- [ ] 修正任何未探索到的选择器（根据 playwright-skill 的实际结果）
- [ ] 使用实际应用环境运行测试：`pytest tests/operate/rfp_management/test_create_rfp_project.py -v`
- [ ] 检查生成的日志文件：`reports/logs/test_create_rfp_project_*.log`
- [ ] 查看 Allure 报告：`allure serve reports/allure-results/`

---

## ✅ 计划总结

- **总共 11 个 Task**
- **关键分界点:**
  - Task 1: 元素探索（需要 playwright-skill）
  - Task 3: 选择器回填（依赖 Task 1）
  - Tasks 4-8: POM 方法实现
  - Task 9: 测试用例
  - Tasks 10-11: 验证

**预期代码行数**: ~600 行（POM + 测试 + 注释 + Allure）

**预期提交数**: 7 个 commit（每个实现阶段 1 个）
