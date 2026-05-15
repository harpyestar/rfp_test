# Interactive `run.py` Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rewrite run.py as an interactive CLI with multi-level menus for environment setup and test selection.

**Architecture:** Entry point `run.py` delegates to `utils/interactive_menu.py` which handles all menu rendering, user input, pytest command construction, and `.env` updates.

**Tech Stack:** Python 3, stdlib (`argparse` removed, uses `input()` for interaction, `ast` for test case parsing, `configparser` for pytest.ini parsing)

**Spec:** `docs/superpowers/specs/2026-05-15-interactive-run-py-design.md`

---

### Task 1: Create `utils/interactive_menu.py` — Non-interactive utilities

**Files:**
- Create: `utils/interactive_menu.py`

This task covers all pure-function helpers: directory discovery, file discovery, pytest marker loading, test case parsing, pytest command construction, and `.env` file updates.

- [ ] **Step 1: Write boilerplate and imports**

```python
"""
Interactive menu system for GRFP UI test runner.
Handles all multi-level menu interactions and pytest command building.
"""

import sys
import os
import ast
import re
from pathlib import Path
from configparser import ConfigParser

PROJECT_ROOT = Path(__file__).parent.parent
TESTS_DIR = PROJECT_ROOT / "tests"
PYTEST_INI = PROJECT_ROOT / "pytest.ini"
DOTENV = PROJECT_ROOT / ".env"
```

- [ ] **Step 2: Implement `load_markers()`**

Read markers from `pytest.ini` using `configparser`.

```python
def load_markers():
    """
    从 pytest.ini 读取 markers 列表。
    Returns:
        list[tuple[str, str]]: [(name, description), ...]
    """
    if not PYTEST_INI.exists():
        return []

    config = ConfigParser()
    config.read(str(PYTEST_INI))
    markers_line = config.get("pytest", "markers", fallback="")

    markers = []
    for line in markers_line.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        # 格式: marker_name: description
        if ":" in line:
            name, desc = line.split(":", 1)
            markers.append((name.strip(), desc.strip()))
        else:
            markers.append((line.strip(), ""))
    return markers
```

- [ ] **Step 3: Implement `list_dirs()`**

```python
def list_dirs(base_path):
    """
    返回 base_path 下的一级子目录（排除 __pycache__ 和 __init__ 入口）。
    Returns:
        list[Path]: 排序后的目录列表
    """
    if not base_path.exists():
        return []
    return sorted([d for d in base_path.iterdir() if d.is_dir() and not d.name.startswith("__")])
```

- [ ] **Step 4: Implement `list_files()`**

```python
def list_files(dir_path):
    """
    返回 dir_path 下所有 test_*.py 文件。
    Returns:
        list[Path]: 排序后的文件列表
    """
    if not dir_path.exists():
        return []
    return sorted(dir_path.glob("test_*.py"))
```

- [ ] **Step 5: Implement `list_test_cases()`**

Parse Python file with `ast` to find `test_*` functions and methods inside `Test*` classes.

```python
def list_test_cases(file_path):
    """
    解析 Python 测试文件，返回所有测试用例标识。
    格式: ClassName::test_method_name 或 test_function_name（模块级函数）。
    Returns:
        list[str]: 排序后的用例标识列表
    """
    if not file_path.exists():
        return []

    with open(file_path, encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read())
        except SyntaxError:
            return []

    cases = []

    for node in ast.iter_child_nodes(tree):
        # 模块级 test_ 函数
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
            cases.append(node.name)
        # Test 类中的 test_ 方法
        elif isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
            for item in ast.iter_child_nodes(node):
                if isinstance(item, ast.FunctionDef) and item.name.startswith("test_"):
                    cases.append(f"{node.name}::{item.name}")

    return sorted(cases)
```

- [ ] **Step 6: Implement `update_dotenv_env()`**

Use regex to replace `ACTIVE_ENV=` line in `.env`.

```python
def update_dotenv_env(env_name):
    """
    更新 .env 文件中的 ACTIVE_ENV 值。
    Args:
        env_name: "test" | "pre" | "prod"
    """
    if not DOTENV.exists():
        print(f"[!] .env 文件不存在: {DOTENV}")
        return

    content = DOTENV.read_text(encoding="utf-8")
    new_content = re.sub(
        r"^ACTIVE_ENV=.*",
        f"ACTIVE_ENV={env_name}",
        content,
        count=1,
        flags=re.MULTILINE,
    )
    DOTENV.write_text(new_content, encoding="utf-8")
    print(f"[+] 环境已切换至: {env_name}")
```

- [ ] **Step 7: Implement `build_pytest_cmd()`**

Build the full pytest command list from user selections.

```python
def build_pytest_cmd(selection, env_config):
    """
    构建 pytest 命令。
    Args:
        selection: dict, 包含 mode 和 path/marker 信息
        env_config: dict, 包含 headed 和 allure 配置
    Returns:
        tuple[list[str], dict]: (cmd_list, env_dict)
    """
    cmd = [sys.executable, "-m", "pytest"]

    if selection["mode"] == "all":
        cmd += ["tests/", "-n", "auto"]
    elif selection["mode"] == "marker":
        cmd += ["tests/", "-m", selection["marker"], "-n", "auto"]
    else:  # role / module / file / case
        cmd += [selection["path"]]

    cmd.append("-v")

    if env_config["allure"]:
        cmd += ["--alluredir=reports/allure-results", "--clean-alluredir"]

    # 环境变量
    env = os.environ.copy()
    env["HEADLESS"] = "false" if env_config["headed"] else "true"

    return cmd, env
```

- [ ] **Step 8: Implement `prompt_choice()`**

Generic numbered menu helper with validation.

```python
def prompt_choice(options, title=None, default=1):
    """
    通用数字菜单选择。
    Args:
        options: list[str] — 选项列表
        title: str | None — 可选标题
        default: int — 默认序号（1-based）
    Returns:
        int: 用户选择的索引（0-based）
    """
    if title:
        print(f"\n{title}")

    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")

    while True:
        try:
            raw = input(f"请输入序号 (1-{len(options)}) [默认 {default}]: ").strip()
            if not raw:
                return default - 1
            choice = int(raw)
            if 1 <= choice <= len(options):
                return choice - 1
            print(f"无效输入，请输入 1-{len(options)} 之间的数字")
        except (ValueError, KeyboardInterrupt):
            print("无效输入，请重新输入")
```

- [ ] **Step 9: Implement `prompt_confirm()`**

Simple yes/no prompt.

```python
def prompt_confirm(prompt_text, default=True):
    """
    是/否确认提示。
    Returns:
        bool
    """
    hint = "Y/n" if default else "y/N"
    while True:
        raw = input(f"{prompt_text} ({hint}): ").strip().lower()
        if not raw:
            return default
        if raw in ("y", "yes"):
            return True
        if raw in ("n", "no"):
            return False
        print("请输入 y 或 n")
```

- [ ] **Step 10: Commit Task 1**

```bash
git add utils/interactive_menu.py
git commit -m "feat: add interactive menu utilities for run.py rewrite"
```

---

### Task 2: Add interactive menu functions to `utils/interactive_menu.py`

**Files:**
- Modify: `utils/interactive_menu.py` (add all menu selection functions + orchestrator)

- [ ] **Step 1: Add `select_env()`**

```python
def select_env():
    """选择执行环境（第一层）"""
    envs = ["test  (测试环境)", "pre   (预发布环境)", "prod  (生产环境)"]
    names = ["test", "pre", "prod"]
    idx = prompt_choice(envs, "请选择执行环境:", default=1)
    selected = names[idx]
    update_dotenv_env(selected)
    return selected
```

- [ ] **Step 2: Add `select_browser_mode()`**

```python
def select_browser_mode():
    """选择有头/无头模式（第一层）"""
    modes = ["有头模式 (headed)", "无头模式 (headless)"]
    idx = prompt_choice(modes, "请选择浏览器模式:", default=1)
    return idx == 0  # True = headed
```

- [ ] **Step 3: Add `select_allure()`**

```python
def select_allure():
    """选择是否启用 Allure 报告（第一层）"""
    opts = ["启用", "不启用"]
    idx = prompt_choice(opts, "是否启用 Allure 报告:", default=2)
    return idx == 0  # True = 启用
```

- [ ] **Step 4: Add `select_exec_mode()`**

```python
def select_exec_mode():
    """选择执行方式（第二层）"""
    modes = ["全部用例执行（自动多线程）", "按标记执行", "指定用例执行"]
    idx = prompt_choice(modes, "请选择执行方式:")
    return ["all", "marker", "specific"][idx]
```

- [ ] **Step 5: Add `select_marker()`**

```python
def select_marker():
    """选择 pytest marker（第三层 - 标记执行分支）"""
    markers = load_markers()
    if not markers:
        print("[!] 未找到任何 pytest markers")
        return None

    labels = [f"{name} — {desc}" if desc else name for name, desc in markers]
    idx = prompt_choice(labels, "可用标记:")
    return markers[idx][0]
```

- [ ] **Step 6: Add `select_specific_mode()`**

```python
def select_specific_mode():
    """选择指定方式（第三层 - 指定用例分支）"""
    modes = ["按角色执行", "按模块执行", "按文件执行", "按用例执行"]
    idx = prompt_choice(modes, "请选择指定方式:")
    return ["role", "module", "file", "case"][idx]
```

- [ ] **Step 7: Add directory traversal helpers**

```python
def _select_role_dir():
    """选择角色目录（第四层），返回选中目录的 Path"""
    dirs = list_dirs(TESTS_DIR)
    if not dirs:
        print("[!] tests/ 目录下没有找到任何角色目录")
        return None
    labels = [d.name for d in dirs]
    idx = prompt_choice(labels, "可用角色目录:")
    return dirs[idx]


def _select_module_dir(role_dir):
    """
    选择模块目录（第五层）。
    如果 role_dir 下没有子目录，直接返回 role_dir 自身。
    """
    subdirs = list_dirs(role_dir)
    if not subdirs:
        # 没有子目录，以角色目录作为模块
        return role_dir
    labels = [d.name for d in subdirs]
    idx = prompt_choice(labels, "可用模块:")
    return subdirs[idx]


def _select_test_file(module_dir):
    """选择测试文件（第六层），返回文件路径字符串"""
    files = list_files(module_dir)
    if not files:
        print(f"[!] {module_dir} 下没有找到测试文件")
        return None
    labels = [f.name for f in files]
    idx = prompt_choice(labels, "可用文件:")
    return str(files[idx])


def _select_test_case(file_path_str):
    """选择测试用例（第七层），返回 pytest 路径字符串"""
    cases = list_test_cases(Path(file_path_str))
    if not cases:
        print(f"[!] {file_path_str} 中没有找到测试用例")
        return None
    idx = prompt_choice(cases, "可用测试用例:")
    return f"{file_path_str}::{cases[idx]}"
```

- [ ] **Step 8: Add drill-down logic for "by role"**

```python
def _drill_by_role():
    """按角色执行"""
    role_dir = _select_role_dir()
    if role_dir is None:
        return None
    return {"mode": "role", "path": str(role_dir)}
```

- [ ] **Step 9: Add drill-down logic for "by module"**

```python
def _drill_by_module():
    """按模块执行"""
    role_dir = _select_role_dir()
    if role_dir is None:
        return None
    module_dir = _select_module_dir(role_dir)
    return {"mode": "module", "path": str(module_dir)}
```

- [ ] **Step 10: Add drill-down logic for "by file"**

```python
def _drill_by_file():
    """按文件执行"""
    role_dir = _select_role_dir()
    if role_dir is None:
        return None
    module_dir = _select_module_dir(role_dir)
    file_path = _select_test_file(module_dir)
    if file_path is None:
        return None
    return {"mode": "file", "path": file_path}
```

- [ ] **Step 11: Add drill-down logic for "by test case"**

```python
def _drill_by_case():
    """按用例执行"""
    role_dir = _select_role_dir()
    if role_dir is None:
        return None
    module_dir = _select_module_dir(role_dir)
    file_path = _select_test_file(module_dir)
    if file_path is None:
        return None
    case_path = _select_test_case(file_path)
    if case_path is None:
        return None
    return {"mode": "case", "path": case_path}
```

- [ ] **Step 12: Add the interactive drill-down dispatcher**

```python
def _drill_specific(specific_mode):
    """根据 specific_mode 分发到不同的 drill-down 函数"""
    drill_map = {
        "role": _drill_by_role,
        "module": _drill_by_module,
        "file": _drill_by_file,
        "case": _drill_by_case,
    }
    return drill_map[specific_mode]()
```

- [ ] **Step 13: Add the main orchestrator function**

```python
def run_interactive_menu():
    """
    交互式菜单主流程。
    1. 环境配置（三层选择）
    2. 执行模式选择
    3. 构建并执行 pytest 命令
    """
    print("=" * 60)
    print("     GRFP UI 测试运行器")
    print("=" * 60)

    # 第一层：环境配置
    env_name = select_env()
    headed = select_browser_mode()
    allure = select_allure()

    # 第二层：执行模式
    exec_mode = select_exec_mode()

    # 构建 selection
    if exec_mode == "all":
        selection = {"mode": "all"}
    elif exec_mode == "marker":
        marker = select_marker()
        if marker is None:
            print("[!] 未选择标记，退出")
            sys.exit(1)
        selection = {"mode": "marker", "marker": marker}
    else:  # specific
        specific_mode = select_specific_mode()
        selection = _drill_specific(specific_mode)
        if selection is None:
            print("[!] 未选择有效的测试路径，退出")
            sys.exit(1)

    env_config = {"headed": headed, "allure": allure}

    # 构建与执行
    cmd, env = build_pytest_cmd(selection, env_config)

    print(f"\n{'=' * 60}")
    print(f"执行命令: {' '.join(cmd)}")
    print(f"{'=' * 60}\n")

    try:
        result = subprocess.run(cmd, env=env, cwd=str(PROJECT_ROOT))
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        print("\n[!] 测试中断（Ctrl+C）")
        sys.exit(130)
    except Exception as e:
        print(f"\n[ERROR] 执行失败: {e}")
        sys.exit(1)
```

- [ ] **Step 14: Add missing import**

Add `import subprocess` at the top of `utils/interactive_menu.py`.

- [ ] **Step 15: Commit Task 2**

```bash
git add utils/interactive_menu.py
git commit -m "feat: add all interactive menu functions and orchestrator"
```

---

### Task 3: Rewrite `run.py`

**Files:**
- Modify: `run.py` (simplify to single entry point)

- [ ] **Step 1: Replace entire `run.py`**

```python
#!/usr/bin/env python
"""
GRFP UI 测试交互式运行脚本
执行 python run.py 进入交互式菜单选择测试环境与范围
"""

from utils.interactive_menu import run_interactive_menu

if __name__ == "__main__":
    run_interactive_menu()
```

- [ ] **Step 2: Commit Task 3**

```bash
git add run.py
git commit -m "refactor: simplify run.py to interactive entry point"
```

---

### Task 4: Manual verification

**Files:**
- Run: `python run.py`

- [ ] **Step 1: Quick smoke test**

```bash
cd /d/work_dev/RFP-NEW/rfp-ui-test
python run.py
```

Verify:
- Level 1 menus appear (env, headed/allure)
- After selection, Level 2 menu appears
- Try "全部用例执行" → verify command printed starts with `pytest tests/ -n auto -v`
- Try "按标记执行" → markers are listed
- Try "指定用例执行 → 按角色" → directories listed
- Try "指定用例执行 → 按用例" → full drill-down works to test case level

- [ ] **Step 3: Commit final state**

```bash
git add -A
git commit -m "feat: complete interactive run.py with multi-level menu"
```