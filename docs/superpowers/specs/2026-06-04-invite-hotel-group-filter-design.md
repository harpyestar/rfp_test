# 邀约酒店集团-集团机构名称筛选 设计文档

**日期**: 2026-06-04
**需求**: 邀约酒店集团集团筛选改为筛选酒店集团机构名称
**迭代标记**: mark_20260604

## 1. 需求概述

"邀约酒店集团" 区域中的筛选控件标签从 "集团名称" 改为 "集团机构名称"，需验证：
1. 筛选控件标签文案正确
2. 精确搜索功能正常
3. 筛选结果列与筛选输入联动正确

## 2. 文件变更

| 文件 | 操作 | 说明 |
|------|------|------|
| `pages/operate/rfp_management/edit_rfp_project_page.py` | 修改 | 新增邀约酒店集团区域定位器和方法 |
| `tests/operate/rfp_management/test_edit_rfp_project_tabs.py` | 修改 | 新增 3 个测试用例 |
| `data/test_cases/rfp_management_params.json` | 修改 | 新增 invite_hotel_group_filter 参数 |

## 3. Page Object 新增 (`edit_rfp_project_page.py`)

### 3.1 新增定位器

```
INVITE_HOTEL_GROUP_BUTTON_TEXT = "邀约酒店集团"
GROUP_ORG_NAME_FILTER_LABEL = "集团机构名称"
FILTER_INPUT_PLACEHOLDER = "请输入集团机构名称"
SEARCH_BUTTON_TEXT = "搜索"
RESULT_ROW_SELECTOR = ".el-table__body-wrapper tbody tr"
```

### 3.2 新增方法

- `click_invite_hotel_group_button()` — 点击 "邀约酒店集团" 按钮展开区域
- `get_group_org_name_filter_label()` — 获取筛选控件标签文本，返回 `str`
- `search_group_org_name(name: str)` — 输入机构名称并触发搜索
- `get_result_group_org_names() -> list[str]` — 获取结果列表中机构名称列的值

## 4. 测试流程

**前置**: 登录平台端 → 签约管理/签约 → 未启动 Tab → 搜索项目 → 修改项目 → 邀请酒店 Tab → 邀约酒店集团

### 用例 1: test_invite_hotel_group_filter_label
- 进入邀约酒店集团区域
- 获取筛选控件标签文本
- 断言: `== "集团机构名称"`

### 用例 2: test_invite_hotel_group_exact_search
- 进入邀约酒店集团区域
- 输入参数化的集团机构名称，触发搜索
- 获取结果列表中所有机构名称
- 断言: 每条记录名称与搜索词一致

### 用例 3: test_invite_hotel_group_filter_linkage
- 进入邀约酒店集团区域
- 记录列表中第一条的机构名称
- 用该名称执行筛选
- 断言: 该记录出现在筛选结果中

## 5. 参数化数据

```json
"invite_hotel_group_filter": [
  {
    "case_id": "group_filter_001",
    "description": "邀约酒店集团-筛选标签和搜索验证",
    "project_name": "自动化测试项目-固定未启动列",
    "group_org_name": "加力协议代录专用"
  }
]
```

3 个用例共用此参数，用例 3 额外从页面动态获取机构名称以验证联动。

## 6. 错误处理

- 所有页面操作使用 `wait_for()` 确保元素可用
- 搜索后等待 `networkidle` 确保结果加载完成
- 异常通过 allure.attach 记录上下文后 re-raise
- 超时值通过 `timeout_config` 获取，不硬编码