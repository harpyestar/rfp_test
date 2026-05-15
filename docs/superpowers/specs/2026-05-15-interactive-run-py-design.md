# Interactive `run.py` — Design Spec

## 概述

重写 `run.py`，将原有 argparse 命令行参数模式改为纯交互式 CLI，通过多级菜单引导用户选择测试执行环境和范围。

## 架构

```
run.py (入口, ~30 行)
  └── utils/interactive_menu.py (菜单引擎, ~250 行)
        ├── select_env()           → "test" | "pre" | "prod"
        ├── select_headless()      → True | False
        ├── select_allure()        → True | False
        ├── select_exec_mode()     → "all" | "marker" | "specific"
        ├── select_marker()        → marker 名称
        ├── select_specific_mode() → "role" | "module" | "file" | "case"
        ├── list_dirs(path)        → 列举目录（跳过 __pycache__）
        ├── list_files(path)       → 列举 test_*.py 文件
        └── list_test_cases(path)  → 解析文件中的 test_ 方法
```

## 交互流程

### Level 1 — 环境配置（三连问）

```
===== GRFP UI 测试运行器 =====

请选择执行环境:
  1. test  (测试环境)
  2. pre   (预发布环境)
  3. prod  (生产环境)
请输入序号 (1-3) [默认 1]:
→ 选择后写入 .env 的 ACTIVE_ENV

请选择浏览器模式:
  1. 有头模式 (headed)
  2. 无头模式 (headless)
请输入序号 (1-2) [默认 1]:
→ env_config["headed"] = True (有头) → env HEADLESS=false
→ env_config["headed"] = False (无头) → env HEADLESS=true

是否启用 Allure 报告:
  1. 启用
  2. 不启用
请输入序号 (1-2) [默认 2]:
```

### Level 2 — 执行模式

```
请选择执行方式:
  1. 全部用例执行（自动多线程）
  2. 按标记执行
  3. 指定用例执行
请输入序号 (1-3):
```

### Level 2 → 全部用例

```
→ 构建命令: pytest tests/ -n auto -v
→ 直接运行，无需后续交互
```

### Level 2 → 标记执行

```
可用标记:
  1. auth        — 认证相关测试
  2. operate     — 运营端测试
  3. hotel       — 酒店端测试
  4. hotelgroup  — 酒店集团端测试
  5. e2e         — 端到端测试
  6. smoke       — 冒烟测试
  7. regression  — 回归测试
  8. mark_20260507 — 20260507迭代需求
请输入序号:

→ 构建命令: pytest tests/ -m <marker_name> -n auto -v
```

### Level 2 → 指定用例

```
请选择指定方式:
  1. 按角色执行
  2. 按模块执行
  3. 按文件执行
  4. 按用例执行
请输入序号 (1-4):
```

#### 按角色执行

```
可用角色目录:
  1. auth
  2. e2e
  3. hotel
  4. hotel_group
  5. operate
请输入序号:

→ 构建命令: pytest tests/<dir>/ -v
```

#### 按模块执行

```
可用角色目录:
  1. auth
  2. e2e
  ...
  5. operate
请输入序号: 5

可用模块:
  1. admin
  2. evaluation
  3. organization
  4. project_management
  5. rfp_management
请输入序号: 5

→ 构建命令: pytest tests/operate/rfp_management/ -v
```

**边界处理：** 如果角色目录下没有子目录（如 `auth/`），跳过模块选择，直接以角色目录为模块运行。

#### 按文件执行

```
可用角色: ... → 选角色
可用模块: ... → 选模块
可用文件:
  1. test_create_rfp_project.py
  2. test_edit_rfp_project_tabs.py
  3. test_rfp_contract_price_status.py
  4. test_rfp_detailPage_project.py
请输入序号: 1

→ 构建命令: pytest tests/operate/rfp_management/test_create_rfp_project.py -v
```

**边界处理：** 如果某一层没有目录，自动降级为文件选择逻辑。

#### 按用例执行

```
可用角色: ... → 选角色
可用模块: ... → 选模块
可用文件: ... → 选文件
可用测试用例:
  1. test_create_project_success
  2. test_create_project_with_invalid_data
  3. ...
请输入序号: 1

→ 构建命令: pytest tests/operate/rfp_management/test_create_rfp_project.py::TestCreateRFP::test_create_project_success -v
```

## 关键实现细节

### 目录发现逻辑（`list_dirs`）

```python
def list_dirs(base_path):
    """返回 base_path 下的一级子目录（排除 __pycache__、__init__.py 目录）"""
    return [d for d in base_path.iterdir()
            if d.is_dir() and not d.name.startswith('__')]
```

### 文件发现逻辑（`list_files`）

```python
def list_files(dir_path):
    """返回 dir_path 下所有 test_*.py 文件（排除 __init__.py）"""
    return sorted(dir_path.glob("test_*.py"))
```

### 测试用例解析逻辑（`list_test_cases`）

```python
def list_test_cases(file_path):
    """解析 Python 文件，返回所有 test_ 开头的方法名"""
    # 使用 ast 模块解析，不 import 文件
    # 格式: ClassName::test_method_name（参数化用例展开为完整名）
```

### 构建 pytest 命令

```python
def build_pytest_cmd(selection, env_config):
    """env_config: {"headed": bool, "allure": bool}"""
    cmd = [sys.executable, '-m', 'pytest']
    
    if selection["mode"] == "all":
        cmd += ["tests/", "-n", "auto"]
    elif selection["mode"] == "marker":
        cmd += ["tests/", "-m", selection["marker"], "-n", "auto"]
    else:  # role / module / file / case
        cmd += [selection["path"]]
    
    cmd.append("-v")
    if env_config["allure"]:
        cmd += ["--alluredir=reports/allure-results", "--clean-alluredir"]
    
    return cmd
```

### `.env` 更新

- 使用 `configparser` 或正则替换 `ACTIVE_ENV` 的值
- headless/allure 不写入 `.env`，仅作为运行时环境变量传递

### 环境变量传递

`config.headless` 读取 `HEADLESS` 环境变量，默认 `false`（有头模式）。

```python
env = os.environ.copy()
# HEADLESS: config.headless 读取此 env var
env['HEADLESS'] = 'false' if env_config["headed"] else 'true'
# ACTIVE_ENV 已通过修改 .env 文件持久化
```

## pytest markers 读取

从 `pytest.ini` 的 `markers =` 段解析，格式为 `marker_name: 描述`。

```python
def load_markers():
    """从 pytest.ini 读取 markers 列表"""
    # 使用 configparser 解析 pytest.ini 的 markers 字段
    # 返回 [(name, description), ...]
```

## 错误处理

- 无效输入：重新提示，不崩溃
- Ctrl+C：友好退出，不显示 traceback
- 测试执行失败：显示 pytest 返回码，不自动退出

## 测试策略

- `utils/interactive_menu.py` 中的非交互函数（目录发现、文件解析、命令构建等）可单测
- 交互部分通过手动验证
