"""
测试数据加载工具
用于加载 JSON 格式的参数化测试数据
"""

import json
from pathlib import Path
from utils.logger import get_logger

logger = get_logger(__name__)


class TestDataLoader:
    """测试数据加载器"""

    DATA_DIR = Path(__file__).parent.parent / "data" / "test_cases"

    @staticmethod
    def load_params(filename: str, key: str = None):
        """
        加载测试参数数据

        Args:
            filename: 参数文件名（无路径，e.g., "rfp_management_params.json"）
            key: 可选，指定 JSON 中的顶级 key（e.g., "create_rfp_project"）

        Returns:
            list 或 dict：参数数据

        Examples:
            # 加载整个文件
            data = TestDataLoader.load_params("rfp_management_params.json")

            # 加载指定 key
            cases = TestDataLoader.load_params("rfp_management_params.json", "create_rfp_project")
        """
        file_path = TestDataLoader.DATA_DIR / filename

        if not file_path.exists():
            raise FileNotFoundError(f"参数文件不存在: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            logger.info(f"成功加载参数文件: {filename}")

            if key:
                if key not in data:
                    raise KeyError(f"参数文件中不存在 key: {key}")
                return data[key]

            return data

        except json.JSONDecodeError as e:
            raise ValueError(f"参数文件 JSON 格式错误: {str(e)}")
