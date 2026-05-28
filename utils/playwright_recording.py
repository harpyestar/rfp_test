import subprocess
import sys


def start_playwright_recorder():
    """
    启动 Playwright 浏览器 + 自动开启录制功能
    会打开浏览器 + 录制控制面板，你操作浏览器即可自动生成代码
    """
    try:
        # Windows / macOS / Linux 通用命令
        # 启动 chromium 浏览器 + 录制模式
        subprocess.run(
            [sys.executable, "-m", "playwright", "codegen"],
            check=True
        )

    except subprocess.CalledProcessError:
        print("启动失败，请先安装 Playwright：")
        print("1. pip install playwright")
        print("2. playwright install chromium")


if __name__ == "__main__":
    print("正在启动 Playwright 浏览器 + 录制功能...")
    start_playwright_recorder()