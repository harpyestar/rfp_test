# 创建新 RFP 项目功能测试 - 设计文档

**日期**: 2026-04-10  
**作者**: Claude Code  
**版本**: 1.0  
**状态**: 设计确认

---

## 📋 需求概述

在 `operate/rfp_management/` 目录下实现 RFP 项目创建功能的自动化测试，验证 operate 角色能够成功创建新的招标项目并保存成功。

### 核心场景
- 登录 operate 角色账号
- 导航至 RFP Management > Create new RFP project
- 填写所有必填字段（标准有效值）
- 点击保存
- 验证保存成功提示

### 测试数据规范
| 字段 | 值 |
|-----|-----|
| Organization Name | hyg测试机构 |
| Project Name | hyg-自动化项目-{timestamp} |
| Contact Person | 荷叶 |
| Contact Number | 区号 + 电话（两个字段） |
| Method of Signing | Private RFP (单选) |
| Signing Status Notification | Manual Notification |
| GROUP/Enterprise Quotation Status | NO NEED (两个都不需要) |
| Bidding Date Range | 2026-04-10 ~ 2026-05-10 |
| Registration Period | 2026-04-10 ~ 2026-05-10 |
| First Round Bidding Period | 2026-04-10 ~ 2026-05-10 |
| Expected Hotels Count | 随机生成 |

---

## 🏗️ 架构设计

### 目录结构

```
pages/operate/rfp_management/
├── __init__.py
└── create_rfp_project_page.py    # CreateNewRFPProjectPage - POM 类

tests/operate/rfp_management/
├── __init__.py
└── test_create_rfp_project.py    # 测试用例

reports/
├── logs/                         # 操作日志（新增）
│   └── test_create_rfp_project_{timestamp}.log
└── allure-results/               # Allure 报告数据
```

### Page Object Model 设计

**类名**: `CreateNewRFPProjectPage(BasePage)`

**继承关系**: 继承 `BasePage`，复用超时管理、元素查找、填充等通用方法

**方法列表** (细粒度设计)：

| 方法 | 职责 | 返回值 |
|-----|------|--------|
| `navigate_to_create_rfp()` | 导航至创建页面 (RFP Management > Create new RFP project) | None |
| `fill_organization_name(org_name="hyg测试机构")` | 填写组织名称 | None |
| `fill_project_name()` | 填写项目名称 (自动生成 timestamp) | str (项目名称) |
| `fill_contact_person(person="荷叶")` | 填写联系人 | None |
| `fill_contact_number(area_code, phone)` | 分别填写区号和电话 | None |
| `select_signing_method()` | 选择 "Private RFP" 单选框 | None |
| `select_notification_method()` | 选择 "Manual Notification" | None |
| `handle_quotation_reports()` | 设置两个报价报告为 "NO NEED" | None |
| `select_bidding_dates(start_date, end_date)` | 设置三个日期范围 (日历选择) | None |
| `fill_expected_hotels_count()` | 填写随机酒店数量 | int (数量) |
| `click_save_button()` | 点击保存按钮 | None |
| `verify_save_success()` | 验证成功提示出现 | bool |

---

## 📊 数据流与交互流程

```
初始状态: Operate 用户已登录，位于 /home 页面
  ↓
navigate_to_create_rfp()
  → 点击导航菜单 RFP Management
  → 选择下拉菜单 Create new RFP project
  → 等待表单加载完成
  ↓
fill_organization_name()
  → 查找 Organization Name 输入框
  → 填写 "hyg测试机构"
  ↓
fill_project_name()
  → 查找 Project Name 输入框
  → 生成项目名称: "hyg-自动化项目-{YYYYMMDD-HHMMSS}"
  → 填写并返回生成的名称
  ↓
fill_contact_person()
  → 查找 Contact Person 输入框
  → 填写 "荷叶"
  ↓
fill_contact_number(area_code, phone)
  → 查找 Area Code 输入框，填写
  → 查找 Phone Number 输入框，填写
  ↓
select_signing_method()
  → 查找 "Private RFP" 单选框
  → 点击选中
  ↓
select_notification_method()
  → 查找 "Manual Notification" 单选框/下拉选项
  → 选中
  ↓
handle_quotation_reports()
  → 查找 GROUP QUOTATION STATUS REPORT
  → 选择 "NO NEED"
  → 查找 Enterprise Quotation Status Report
  → 选择 "NO NEED"
  ↓
select_bidding_dates(start_date="2026-04-10", end_date="2026-05-10")
  → Bidding Date Range: 打开日历，选择 2026-04-10 ~ 2026-05-10
  → Registration Period: 打开日历，选择 2026-04-10 ~ 2026-05-10
  → First Round Bidding Period: 打开日历，选择 2026-04-10 ~ 2026-05-10
  ↓
fill_expected_hotels_count()
  → 查找 Expected number of contracted hotels 输入框
  → 生成随机数 (1-50)
  → 填写并返回数量
  ↓
click_save_button()
  → 查找保存按钮
  → 点击
  → 等待页面响应
  ↓
verify_save_success()
  → 查找成功提示信息 (如 "Success!", "保存成功" 等)
  → 验证提示文本存在且可见
  → 返回 bool
  ↓
最终状态: 测试断言 verify_save_success() 返回 True
```

---

## 🔍 元素定位策略

所有选择器需要通过 **playwright-skill 实际页面探索**获得，包括：

- 导航菜单元素
- 所有表单输入框 (Organization, Project Name, Contact 等)
- 单选框和下拉菜单
- 日期选择器组件 (Element UI Calendar)
- 保存按钮
- 成功提示信息容器

**定位规则** (遵循 CLAUDE.md):
- 禁止硬编码选择器
- 所有选择器定义为类变量，便于后续调整
- 优先使用 CSS selector，其次考虑 data-* 属性

---

## 📝 日志与报告集成

### 1. 操作日志文件
- **位置**: `reports/logs/test_create_rfp_project_{timestamp}.log`
- **内容**: 每个测试执行的完整操作日志
  - 时间戳、操作名称、输入值、结果状态
  - 例: `[2026-04-10 10:30:45.123] fill_organization_name: hyg测试机构 ✓`
- **生成**: 通过 `utils/logger.py` Logger 单例自动记录

### 2. Allure 报告集成
- **Step 装饰**: 每个主要操作用 `@allure.step()` 标记
- **Attachment**: 关键步骤用 `allure.attach_text()` 附加日志
  - 例: 附加填写的项目名称、选中的日期范围等
- **Title & Description**: 测试用例添加 `@allure.title()` 和 `@allure.description()`

### 3. 代码示例
```python
import allure
from utils.logger import get_logger

class CreateNewRFPProjectPage(BasePage):
    
    async def fill_project_name(self):
        """填写项目名称"""
        self.logger.info("开始填写项目名称")
        
        with allure.step("填写项目名称"):
            project_name = f"hyg-自动化项目-{self._generate_timestamp()}"
            await self.fill(self.PROJECT_NAME_SELECTOR, project_name)
            allure.attach_text(f"生成的项目名称: {project_name}", "项目名称")
            self.logger.info(f"项目名称填写成功: {project_name}")
            return project_name
```

---

## ✅ 测试用例设计

### 测试用例：创建新 RFP 项目 - 完整流程

```python
@pytest.mark.asyncio
@allure.title("创建新 RFP 项目 - 完整流程")
@allure.description("测试: Operate 角色成功创建新 RFP 项目，填写所有必填字段并保存")
async def test_create_rfp_project_success(page, operate_user):
    """
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
    """
    create_page = CreateNewRFPProjectPage(page)
    
    await create_page.navigate_to_create_rfp()
    await create_page.fill_organization_name()
    project_name = await create_page.fill_project_name()
    await create_page.fill_contact_person()
    await create_page.fill_contact_number("010", "12345678")
    await create_page.select_signing_method()
    await create_page.select_notification_method()
    await create_page.handle_quotation_reports()
    await create_page.select_bidding_dates("2026-04-10", "2026-05-10")
    hotels_count = await create_page.fill_expected_hotels_count()
    await create_page.click_save_button()
    
    # 断言: 成功提示出现
    success = await create_page.verify_save_success()
    assert success, "保存成功提示未出现"
```

---

## 🔧 超时与错误处理

- **超时值**: 全部来自 `utils/timeout_config.py`
  - `element_timeout`: 元素查找超时
  - `navigation_timeout`: 页面导航超时
- **重试机制**: 日期选择失败时自动重试 1 次
- **异常日志**: 所有异常捕获并记录详细信息到日志和 Allure

---

## 📦 依赖与集成

- **框架**: pytest + pytest-asyncio + Playwright
- **日志**: `utils/logger.py` Logger 单例
- **超时管理**: `utils/timeout_config.py`
- **报告**: Allure (1.2.8+)
- **POM 基类**: `pages/common/base_page.py`

---

## ✨ 设计特点

✅ **细粒度 POM 方法** - 便于维护和扩展  
✅ **双层日志** - 文件日志 + Allure 报告  
✅ **完整数据验证** - 所有必填字段覆盖  
✅ **统一超时管理** - 无硬编码超时值  
✅ **清晰的错误信息** - 便于调试  

---

## 📌 后续扩展方向

- [ ] 异常场景测试 (必填字段缺失、无效日期等) - 后续补充
- [ ] 多角色对比 (Operate vs Enterprise vs Hotel) - 权限验证
- [ ] 项目编辑功能 - 基于此 POM 扩展
- [ ] 项目发布流程 - 依赖此功能完成