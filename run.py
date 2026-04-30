#!/usr/bin/env python
"""
PyCharm 测试运行脚本

== PyCharm 配置方式 ==
  1. 右键 run.py → Modify Run Configuration
  2. Script path 选择 run.py
  3. Working directory 设置为项目根目录（grfp-ui-test/）
  4. Python interpreter 选择 venv 解释器
  5. Parameters 填写以下参数之一：

== 常用运行场景 ==
  全部测试：            (不填参数)
  指定测试文件：        -f tests/auth/test_login.py
  指定测试类：          -f tests/auth/test_login.py::TestLogin
  指定单个用例：        -f tests/auth/test_login.py::TestLogin::test_login_success
  指定参数化用例：      -f tests/auth/test_login.py::TestLogin::test_login_success[operate]
  按关键字过滤：        -k test_login_success
  无头模式（CI）：      --headless
  失败立即停止：        -x
  生成 Allure 报告：    --allure
  组合使用：            -f tests/auth/test_login.py -x --headless
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent


def build_command(args):
    """构建 pytest 命令，使用当前 Python 解释器确保 venv 生效"""
    # 使用 sys.executable 而非 'python'，确保 PyCharm 的 venv 解释器被使用
    cmd = [sys.executable, '-m', 'pytest']

    # 测试范围
    if args.file:
        # 支持：文件 / 文件::类 / 文件::类::用例 / 文件::类::用例[参数]
        cmd.append(args.file)
    elif args.keyword:
        # 按关键字过滤，搜索范围为整个 tests/ 目录
        cmd.extend(['tests/', '-k', args.keyword])
    else:
        # 默认运行所有测试
        cmd.append('tests/')

    # 详细输出（默认开启）
    cmd.append('-v')

    # 失败立即停止
    if args.exitfirst:
        cmd.append('-x')

    # Allure 报告
    if args.allure:
        cmd.extend(['--alluredir=reports/allure-results', '--clean-alluredir'])

    return cmd


def main():
    parser = argparse.ArgumentParser(
        description='GRFP UI 测试运行脚本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '-f', '--file',
        help='测试路径：文件、类、用例（支持 :: 分隔）\n'
             '例：tests/auth/test_login.py::TestLogin::test_login_success[operate]'
    )
    parser.add_argument(
        '-k', '--keyword',
        help='按测试名关键字过滤（支持 and/or）\n例：-k test_login_success'
    )
    parser.add_argument(
        '-x', '--exitfirst',
        action='store_true',
        help='第一个失败时立即停止'
    )
    parser.add_argument(
        '--headless',
        action='store_true',
        default=False,
        help='无头模式运行（默认有头，便于 PyCharm 调试）'
    )
    parser.add_argument(
        '--allure',
        action='store_true',
        help='生成 Allure 报告到 reports/allure-results'
    )

    args = parser.parse_args()

    cmd = build_command(args)

    # 设置环境变量（继承当前环境，覆盖 HEADLESS）
    env = os.environ.copy()
    env['HEADLESS'] = 'true' if args.headless else 'false'

    print(f'\n{"=" * 60}')
    print(f'Command: {" ".join(cmd)}')
    print(f'{"=" * 60}\n')

    try:
        result = subprocess.run(cmd, env=env, cwd=str(PROJECT_ROOT))
        exit_code = result.returncode
    except KeyboardInterrupt:
        print('\n[!] 测试中断（Ctrl+C）')
        exit_code = 130
    except Exception as e:
        print(f'\n[ERROR] 执行失败: {e}')
        exit_code = 1

    if args.allure and exit_code == 0:
        print(f'\n[+] 报告已生成，查看：allure serve reports/allure-results')

    sys.exit(exit_code)


if __name__ == '__main__':
    main()