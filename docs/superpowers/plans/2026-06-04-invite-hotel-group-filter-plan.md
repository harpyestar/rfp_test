# 邀约酒店集团-集团机构名称筛选 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 验证邀约酒店集团区域筛选控件标签从"集团名称"变更为"集团机构名称"，并验证筛选功能正常。

**Architecture:** 在现有 `EditRFPProjectPage` POM 中新增邀约酒店集团区域的定位器和方法（3 个定位器 + 4 个方法），在 `TestEditRFPProjectTabs` 中新增 3 个参数化测试用例，测试数据通过 `rfp_management_params.json` 参数化。

**Tech Stack:** Python + Playwright (pytest-playwright) + allure + POM

---

### Task 1: 新增参数化测试数据

**Files:**
- Modify: `data/test_cases/rfp_management_params.json`

- [ ] **Step 1: 在 JSON 文件末尾新增 invite_hotel_group_filter 数据**

在 `rfp_management_params.json` 最后一行（`}`之前）添加：

```json
,
  "invite_hotel_group_filter": [
    {
      "case_id": "group_filter_001",
      "description": "邀约酒店集团-筛选标签和搜索验证",
      "project_name": "自动化测试项目-固定未启动列",
      "group_org_name": "加力协议代录专用"
    }
  ]
```

- [ ] **Step 2: 验证 JSON 格式**

```powershell
python -c "import json; json.load(open('data/test_cases/rfp_management_params.json', 'r', encoding='utf-8')); print('JSON valid')"
```

- [ ] **Step 3: Commit**

```bash
git add data/test_cases/rfp_management_params.json
git commit -m "feat: add invite_hotel_group_filter test data for mark_20260604"
```

---

### Task 2: Page Object — 新增邀约酒店集团定位器和方法

**Files:**
- Modify: `pages/operate/rfp_management/edit_rfp_project_page.py`

- [ ] **Step 1: 在类顶部新增定位器常量**

在 `ADD_GROUP_INTENT_HOTEL_TEXT` 定位器之后（约第 41 行），`# ========== URL 项目 ID 提取 ==========` 注释之前插入：

```python
    # ========== 邀约酒店集团区域元素 ==========
    INVITE_HOTEL_GROUP_BUTTON_TEXT = "邀约酒店集团"
    GROUP_ORG_NAME_FILTER_LABEL_TEXT = "集团机构名称"
    FILTER_INPUT_PLACEHOLDER = "请输入集团机构名称"
    SEARCH_BUTTON_TEXT = "搜索"
```

- [ ] **Step 2: 新增方法 `click_invite_hotel_group_button`**

在 `click_add_group_intent_hotel_button` 方法之后插入：

```python
    async def click_invite_hotel_group_button(self) -> None:
        """点击 邀约酒店集团 按钮展开区域"""
        self.logger.info("开始点击邀约酒店集团按钮")

        with allure.step("点击邀约酒店集团按钮"):
            try:
                btn = self.page.get_by_text(self.INVITE_HOTEL_GROUP_BUTTON_TEXT)
                await btn.wait_for(timeout=timeout_config.get_element_timeout())
                await btn.click()
                await self.page.wait_for_timeout(500)
                self.logger.info("[OK] 已点击邀约酒店集团按钮")
            except Exception as e:
                error_msg = f"点击邀约酒店集团按钮失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "点击错误")
                raise
```

- [ ] **Step 3: 新增方法 `get_group_org_name_filter_label`**

```python
    async def get_group_org_name_filter_label(self) -> str:
        """获取集团机构名称筛选控件的标签文本"""
        self.logger.info("开始获取集团机构名称筛选控件标签")

        with allure.step("获取筛选控件标签文本"):
            try:
                label = self.page.get_by_text(self.GROUP_ORG_NAME_FILTER_LABEL_TEXT)
                await label.wait_for(timeout=timeout_config.get_element_timeout())
                label_text = await label.text_content()
                self.logger.info(f"筛选标签文本: {label_text}")
                allure.attach(f"筛选标签: {label_text}", "标签验证")
                return label_text or ""
            except Exception as e:
                error_msg = f"获取筛选控件标签失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "标签获取错误")
                raise
```

- [ ] **Step 4: 新增方法 `search_group_org_name`**

```python
    async def search_group_org_name(self, group_name: str) -> None:
        """在集团机构名称筛选输入框中输入名称并触发搜索

        Args:
            group_name: 集团机构名称
        """
        self.logger.info(f"开始搜索集团机构名称: {group_name}")

        with allure.step(f"搜索集团机构名称: {group_name}"):
            try:
                filter_input = self.page.get_by_placeholder(self.FILTER_INPUT_PLACEHOLDER)
                await filter_input.wait_for(timeout=timeout_config.get_element_timeout())
                await filter_input.click()
                await filter_input.fill(group_name)
                await self.page.wait_for_timeout(200)
                self.logger.info(f"集团机构名称已输入: {group_name}")

                search_btn = self.page.get_by_text(self.SEARCH_BUTTON_TEXT)
                await search_btn.wait_for(timeout=timeout_config.get_element_timeout())
                await search_btn.click()
                await self.page.wait_for_load_state("networkidle")
                self.logger.info("[OK] 集团机构名称搜索完成")
            except Exception as e:
                error_msg = f"搜索集团机构名称失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "搜索错误")
                raise
```

- [ ] **Step 5: 新增方法 `get_result_group_org_names`**

```python
    async def get_result_group_org_names(self) -> list:
        """获取搜索结果列表中集团机构名称列的所有值

        Returns:
            list: 集团机构名称列表
        """
        self.logger.info("开始获取结果列表中的集团机构名称")

        with allure.step("获取结果列表中集团机构名称列的值"):
            try:
                # 定位表头中"集团机构名称"列的索引
                headers = self.page.locator(".el-table__header-wrapper th").all()
                col_index = -1
                for i, header in enumerate(headers):
                    text = await header.text_content()
                    if self.GROUP_ORG_NAME_FILTER_LABEL_TEXT in (text or ""):
                        col_index = i
                        break

                if col_index == -1:
                    self.logger.warning("未找到集团机构名称列，返回空列表")
                    return []

                # 获取数据行中该列的值
                rows = self.page.locator(".el-table__body-wrapper tbody tr").all()
                names = []
                for row in rows:
                    cells = await row.locator("td").all()
                    if col_index < len(cells):
                        name = await cells[col_index].text_content()
                        names.append((name or "").strip())

                self.logger.info(f"获取到 {len(names)} 条集团机构名称")
                allure.attach(f"结果: {names}", "机构名称列表")
                return names
            except Exception as e:
                error_msg = f"获取集团机构名称列表失败: {str(e)}"
                self.logger.error(error_msg)
                allure.attach(error_msg, "列表获取错误")
                raise
```

- [ ] **Step 6: Commit**

```bash
git add pages/operate/rfp_management/edit_rfp_project_page.py
git commit -m "feat: add invite hotel group filter locators and methods for mark_20260604"
```

---

### Task 3: 测试用例 1 — 筛选控件标签文案校验

**Files:**
- Modify: `tests/operate/rfp_management/test_edit_rfp_project_tabs.py`

- [ ] **Step 1: 新增测试方法 `test_invite_hotel_group_filter_label`**

在 `TestEditRFPProjectTabs` 类中（在最后一个已有测试方法之后，`test_export_hotel_list_includes_hotel_id` 方法之后）插入：

```python
    # ======================== 邀约酒店集团 - 集团机构名称筛选 ========================

    @pytest.mark.asyncio
    @pytest.mark.mark_20260604
    @allure.title("邀约酒店集团-筛选控件标签文案校验: {test_data[description]}")
    @allure.description("""
    测试: 验证邀约酒店集团区域筛选控件的标签显示为"集团机构名称"（不再显示"集团名称"）。

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
```

- [ ] **Step 2: Commit**

```bash
git add tests/operate/rfp_management/test_edit_rfp_project_tabs.py
git commit -m "feat: add test_invite_hotel_group_filter_label for mark_20260604"
```

---

### Task 4: 测试用例 2 — 集团机构名称精确搜索

**Files:**
- Modify: `tests/operate/rfp_management/test_edit_rfp_project_tabs.py`

- [ ] **Step 1: 新增测试方法 `test_invite_hotel_group_exact_search`**

在 `test_invite_hotel_group_filter_label` 方法之后插入：

```python
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
            for i, name in enumerate(names):
                assert name == test_data["group_org_name"], \
                    f"第{i + 1}条记录的机构名称'{name}'与搜索词'{test_data['group_org_name']}'不一致"
```

- [ ] **Step 2: Commit**

```bash
git add tests/operate/rfp_management/test_edit_rfp_project_tabs.py
git commit -m "feat: add test_invite_hotel_group_exact_search for mark_20260604"
```

---

### Task 5: 测试用例 3 — 筛选结果与筛选输入联动校验

**Files:**
- Modify: `tests/operate/rfp_management/test_edit_rfp_project_tabs.py`

- [ ] **Step 1: 新增测试方法 `test_invite_hotel_group_filter_linkage`**

在 `test_invite_hotel_group_exact_search` 方法之后插入：

```python
    @pytest.mark.asyncio
    @pytest.mark.mark_20260604
    @allure.title("邀约酒店集团-筛选联动校验: {test_data[description]}")
    @allure.description("""
    测试: 从列表中取一条机构名称，用该名称执行筛选，验证该记录出现在筛选结果中且完全匹配。

    流程: 同上进入邀约酒店集团 → 记录列表中第一条机构名称 → 用该名称筛选 → 验证结果匹配
    """)
    @pytest.mark.parametrize("test_data", TestDataLoader.load_params(
        "rfp_management_params.json", "invite_hotel_group_filter"
    ))
    async def test_invite_hotel_group_filter_linkage(self, page_module, operate_user, test_data):
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

        with allure.step("【步骤 6】获取列表中第一条集团机构名称"):
            initial_names = await edit_page.get_result_group_org_names()
            assert len(initial_names) > 0, "列表中无集团机构名称记录"
            first_org_name = initial_names[0]
            allure.attach(f"记录的名称: {first_org_name}", "待筛选名称")

        with allure.step(f"【步骤 7】用该名称执行筛选: {first_org_name}"):
            await edit_page.search_group_org_name(first_org_name)

        with allure.step("【步骤 8】验证筛选结果"):
            filtered_names = await edit_page.get_result_group_org_names()
            assert len(filtered_names) > 0, "筛选结果为空"
            assert first_org_name in filtered_names, \
                f"机构名称'{first_org_name}'未出现在筛选结果中"
            for i, name in enumerate(filtered_names):
                assert name == first_org_name, \
                    f"第{i + 1}条记录'{name}'与筛选输入'{first_org_name}'不一致"
```

- [ ] **Step 2: Commit**

```bash
git add tests/operate/rfp_management/test_edit_rfp_project_tabs.py
git commit -m "feat: add test_invite_hotel_group_filter_linkage for mark_20260604"
```

---

### Task 6: 运行测试并验证

- [ ] **Step 1: 运行 mark_20260604 标记的全部用例**

```powershell
pytest -m mark_20260604 -v --tb=long
```

**预期结果**: 3 个新增用例全部 PASS

- [ ] **Step 2: 如用例失败，停止并根据错误信息排查**

按照 CLAUDE.md 规范：测试失败时立即停止，把失败原因报告用户，等待指示。