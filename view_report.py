#!/usr/bin/env python
"""
查看 Allure 测试报告
在浏览器中打开可视化的测试报告页面
"""

import subprocess
import sys
import shutil
from pathlib import Path

REPORTS_DIR = Path(__file__).parent / "reports" / "allure-results"
ALLURE_CMD = str(
    Path.home() / "scoop" / "apps" / "allure" / "current" / "bin" / "allure.bat"
)
# fallback: 手动安装路径
if not Path(ALLURE_CMD).exists():
    ALLURE_CMD = "D:/tools/allure-2.36.0/bin/allure.bat"


def main():
    if not REPORTS_DIR.exists():
        print(f"[!] 报告目录不存在: {REPORTS_DIR}")
        print("[!] 请先运行测试并启用 Allure 报告")
        sys.exit(1)

    result_files = list(REPORTS_DIR.glob("*-result.json"))
    if not result_files:
        print(f"[!] {REPORTS_DIR} 中没有找到 Allure 结果数据")
        print("[!] 请先运行测试并启用 Allure 报告")
        sys.exit(1)

    print(f"[+] 共 {len(result_files)} 个测试结果")
    print(f"[+] 启动 Allure 报告服务...")
    print(f"[+] 浏览器打开后可关闭终端\n")

    try:
        subprocess.run(
            [ALLURE_CMD, "serve", str(REPORTS_DIR)],
            cwd=str(Path(__file__).parent),
        )
    except FileNotFoundError:
        print("[!] 未找到 allure 命令，请先安装:")
        print("   scoop install allure")
        print("   或: npm install -g allure-commandline")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[!] 已关闭报告服务")
        sys.exit(0)


if __name__ == "__main__":
    main()