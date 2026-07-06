"""
Interactive menu system for GRFP UI test runner.
Handles all multi-level menu interactions and pytest command building.
"""

import sys
import os
import ast
import re
import subprocess
from pathlib import Path
from configparser import ConfigParser

PROJECT_ROOT = Path(__file__).parent.parent
TESTS_DIR = PROJECT_ROOT / "tests"
PYTEST_INI = PROJECT_ROOT / "pytest.ini"
DOTENV = PROJECT_ROOT / ".env"


def load_markers():
    """
    从 pytest.ini 读取 marker 定义。

    Returns:
        list[tuple[str, str]]: [(name, description), ...]
    """
    if not PYTEST_INI.exists():
        return []

    config = ConfigParser()
    with open(str(PYTEST_INI), encoding="utf-8") as f:
        config.read_file(f)
    markers_line = config.get("pytest", "markers", fallback="")

    markers = []
    for line in markers_line.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        if ":" in line:
            name, desc = line.split(":", 1)
            markers.append((name.strip(), desc.strip()))
        else:
            markers.append((line.strip(), ""))
    return markers


def list_dirs(base_path):
    """
    列出指定路径下的子目录，排除 __pycache__ 和 __init__ 目录。

    Args:
        base_path: Path 对象

    Returns:
        list[Path]: 排序后的子目录列表
    """
    if not base_path.exists():
        return []
    return sorted([d for d in base_path.iterdir() if d.is_dir() and not d.name.startswith("__")])


def list_files(dir_path):
    """
    列出指定目录下的 test_*.py 测试文件。

    Args:
        dir_path: Path 对象

    Returns:
        list[Path]: 排序后的测试文件列表
    """
    if not dir_path.exists():
        return []
    return sorted(dir_path.glob("test_*.py"))


def list_test_cases(file_path):
    """
    解析 Python 测试文件，提取所有测试用例。

    使用 ast 模块静态解析，查找 test_ 开头的函数和 Test* 类中的 test_ 方法。

    Args:
        file_path: Path 对象或字符串路径

    Returns:
        list[str]: 排序后的用例标识符，格式为 "test_func" 或 "TestClass::test_method"
    """
    if not file_path.exists():
        return []

    with open(file_path, encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read())
        except SyntaxError:
            return []

    # Python 3.12+ 中 AsyncFunctionDef 不再继承自 FunctionDef
    _FUNC_TYPES = (ast.FunctionDef, ast.AsyncFunctionDef)

    cases = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, _FUNC_TYPES) and node.name.startswith("test_"):
            cases.append(node.name)
        elif isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
            for item in ast.iter_child_nodes(node):
                if isinstance(item, _FUNC_TYPES) and item.name.startswith("test_"):
                    cases.append(f"{node.name}::{item.name}")

    return sorted(cases)


def update_dotenv_env(env_name):
    """
    更新 .env 文件中的 ACTIVE_ENV 值。

    使用正则表达式替换 ACTIVE_ENV= 所在行，保留文件其余内容不变。

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
    if new_content == content:
        print(f"[-] ACTIVE_ENV 已经是 {env_name}，无需修改")
        return
    DOTENV.write_text(new_content, encoding="utf-8")
    print(f"[+] 环境已切换至: {env_name}")


def build_pytest_cmd(selection, env_config):
    """
    根据用户选择构建 pytest 命令和环境变量。

    Args:
        selection: dict，包含键 mode（必选），根据 mode 不同还包含 path 或 marker
        env_config: dict，包含 headed（bool）和 allure（bool）

    Returns:
        tuple[list[str], dict]: (cmd_list, env_dict)
    """
    mode = selection.get("mode")
    if mode not in ("all", "marker", "role", "module", "file", "case"):
        raise ValueError(f"未知的 execution mode: {mode}")

    cmd = [sys.executable, "-m", "pytest"]

    if mode == "all":
        cmd += ["tests/", "-n", str(selection["threads"]), "--dist", "loadgroup"]
    elif mode == "marker":
        cmd += ["tests/", "-m", selection["marker"], "-n", str(selection["threads"]), "--dist", "loadgroup"]
    else:  # role / module / file / case
        path = selection.get("path")
        if not path:
            raise ValueError(f"mode '{mode}' 需要 path 参数")
        cmd += [path]

    cmd.append("-v")

    if env_config.get("allure"):
        cmd += ["--alluredir=reports/allure-results", "--clean-alluredir"]

    env = os.environ.copy()
    env["HEADLESS"] = "false" if env_config.get("headed") else "true"

    return cmd, env


def prompt_choice(options, title=None, default=1):
    """
    通用编号菜单选择提示，带输入验证。

    Args:
        options: list[str] — 选项标签列表
        title: str | None — 可选的区块标题
        default: int — 默认选项序号（从 1 开始）

    Returns:
        int: 用户选择的 0-based 索引
    """
    if not options:
        print("[!] 没有可用选项")
        return -1

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
        except ValueError:
            print("无效输入，请重新输入")
        except KeyboardInterrupt:
            print("\n[!] 已取消")
            sys.exit(130)


def prompt_confirm(prompt_text, default=True):
    """
    是/否确认提示。

    Args:
        prompt_text: str — 提示文本
        default: bool — 默认值（True 对应 Y/n，False 对应 y/N）

    Returns:
        bool
    """
    hint = "Y/n" if default else "y/N"
    while True:
        try:
            raw = input(f"{prompt_text} ({hint}): ").strip().lower()
            if not raw:
                return default
            if raw in ("y", "yes"):
                return True
            if raw in ("n", "no"):
                return False
            print("请输入 y 或 n")
        except KeyboardInterrupt:
            print("\n[!] 已取消")
            sys.exit(130)


def select_env():
    """选择执行环境（第一层）"""
    envs = ["test  (测试环境)", "pre   (预发布环境)", "prod  (生产环境)"]
    names = ["test", "pre", "prod"]
    idx = prompt_choice(envs, "请选择执行环境:", default=1)
    selected = names[idx]
    update_dotenv_env(selected)
    return selected


def select_browser_mode():
    """选择有头/无头模式（第一层）"""
    modes = ["有头模式 (headed)", "无头模式 (headless)"]
    idx = prompt_choice(modes, "请选择浏览器模式:", default=1)
    return idx == 0  # True = headed


def select_allure():
    """选择是否启用 Allure 报告（第一层）"""
    opts = ["启用", "不启用"]
    idx = prompt_choice(opts, "是否启用 Allure 报告:", default=2)
    return idx == 0  # True = 启用


def select_thread_count():
    """选择线程数（1-9），用于全部用例执行和按标记执行"""
    opts = [str(i) for i in range(1, 10)]
    idx = prompt_choice(opts, "请选择并发线程数:", default=4)
    return idx + 1  # 返回 1-9


def select_exec_mode():
    """选择执行方式（第二层）"""
    modes = ["全部用例执行", "按标记执行", "指定用例执行"]
    idx = prompt_choice(modes, "请选择执行方式:")
    return ["all", "marker", "specific"][idx]


def select_marker():
    """选择 pytest marker（第三层 - 标记执行分支）"""
    markers = load_markers()
    if not markers:
        print("[!] 未找到任何 pytest markers")
        return None
    labels = [f"{name} — {desc}" if desc else name for name, desc in markers]
    idx = prompt_choice(labels, "可用标记:")
    return markers[idx][0]


def select_specific_mode():
    """选择指定方式（第三层 - 指定用例分支）"""
    modes = ["按角色执行", "按模块执行", "按文件执行", "按用例执行"]
    idx = prompt_choice(modes, "请选择指定方式:")
    return ["role", "module", "file", "case"][idx]


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
    如果 role_dir 下没有子目录，直接返回 role_dir 自身（降级处理）。
    """
    subdirs = list_dirs(role_dir)
    if not subdirs:
        print(f"[i] {role_dir.name} 下无模块子目录，直接使用该目录")
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


def _drill_by_role():
    """按角色执行"""
    role_dir = _select_role_dir()
    if role_dir is None:
        return None
    return {"mode": "role", "path": str(role_dir)}


def _drill_by_module():
    """按模块执行"""
    role_dir = _select_role_dir()
    if role_dir is None:
        return None
    module_dir = _select_module_dir(role_dir)
    return {"mode": "module", "path": str(module_dir)}


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


def _drill_specific(specific_mode):
    """根据 specific_mode 分发到不同的 drill-down 函数"""
    drill_map = {
        "role": _drill_by_role,
        "module": _drill_by_module,
        "file": _drill_by_file,
        "case": _drill_by_case,
    }
    return drill_map[specific_mode]()


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
        threads = select_thread_count()
        selection = {"mode": "all", "threads": threads}
    elif exec_mode == "marker":
        marker = select_marker()
        if marker is None:
            print("[!] 未选择标记，退出")
            sys.exit(1)
        threads = select_thread_count()
        selection = {"mode": "marker", "marker": marker, "threads": threads}
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