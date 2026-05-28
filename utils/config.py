"""
配置管理模块
从 .env 文件读取配置，根据 ACTIVE_ENV 自动选择对应环境的 URL 和账号
切换环境只需修改 .env 中的 ACTIVE_ENV=test|pre|prod
"""

import os
import json
from pathlib import Path
from typing import Dict
from dotenv import load_dotenv


class Config:
    """项目配置类"""

    PROJECT_ROOT = Path(__file__).parent.parent
    DATA_DIR = PROJECT_ROOT / "data"
    ACCOUNTS_FILE = DATA_DIR / "test_accounts.json"

    def __init__(self, env_file: str = ".env"):
        self.env_path = self.PROJECT_ROOT / env_file

        if self.env_path.exists():
            load_dotenv(self.env_path)
        else:
            print(f"Warning: {self.env_path} not found, using system environment variables")

        self.accounts = self._load_accounts()

    def _load_accounts(self) -> Dict:
        if not self.ACCOUNTS_FILE.exists():
            raise FileNotFoundError(f"Accounts file not found: {self.ACCOUNTS_FILE}")
        with open(self.ACCOUNTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    @property
    def active_env(self) -> str:
        """当前激活的环境: test | pre | prod"""
        return os.getenv("ACTIVE_ENV", "test").lower()

    # 兼容旧代码中使用 config.test_env 的地方
    @property
    def test_env(self) -> str:
        return self.active_env

    @property
    def base_url(self) -> str:
        """根据当前环境自动选择对应 BASE URL"""
        key = f"{self.active_env.upper()}_BASE_URL"
        return os.getenv(key, "https://grfp-test.fangcang.com/")

    @property
    def browser_channel(self) -> str:
        return os.getenv("BROWSER_CHANNEL", "")

    @property
    def headless(self) -> bool:
        return os.getenv("HEADLESS", "false").lower() == "true"

    @property
    def slow_mo(self) -> int:
        return int(os.getenv("SLOW_MO", "100"))

    @property
    def log_level(self) -> str:
        return os.getenv("LOG_LEVEL", "INFO")

    @property
    def timeout_page_load(self) -> int:
        return int(os.getenv("TIMEOUT_PAGE_LOAD", "10000"))

    @property
    def timeout_element(self) -> int:
        return int(os.getenv("TIMEOUT_ELEMENT", "10000"))

    @property
    def timeout_navigation(self) -> int:
        return int(os.getenv("TIMEOUT_NAVIGATION", "10000"))

    @property
    def allure_results_dir(self) -> str:
        return os.getenv("ALLURE_RESULTS_DIR", "reports/allure-results")

    @property
    def rerun_failures_count(self) -> int:
        return int(os.getenv("RERUN_FAILURES_COUNT", "0"))

    @property
    def rerun_failures_delay_min(self) -> float:
        delay_str = os.getenv("RERUN_FAILURES_DELAY", "0")
        try:
            return float(delay_str.split("-")[0].strip())
        except (ValueError, IndexError):
            return 0.0

    @property
    def rerun_failures_delay_max(self) -> float:
        delay_str = os.getenv("RERUN_FAILURES_DELAY", "0")
        try:
            parts = delay_str.split("-")
            if len(parts) >= 2:
                return float(parts[1].strip())
            return float(parts[0].strip())
        except (ValueError, IndexError):
            return 0.0

    def get_account(self, account_type: str) -> Dict[str, str]:
        """
        获取当前环境下指定角色的账号

        Args:
            account_type: operate | hotel | hotelgroup

        Returns:
            {mobile, password, role_name}
        """
        env_accounts = self.accounts.get(self.active_env)
        if env_accounts is None:
            raise KeyError(f"No accounts configured for env '{self.active_env}'")
        if account_type not in env_accounts:
            raise KeyError(f"Account type '{account_type}' not found for env '{self.active_env}'")
        return env_accounts[account_type]


# 全局配置实例
config = Config()
