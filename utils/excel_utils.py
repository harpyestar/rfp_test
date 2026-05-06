"""
Excel 文件生成工具
用于生成签约状态导入 Excel 文件
"""

import openpyxl
from pathlib import Path
from utils.config import config
from utils.logger import get_logger

logger = get_logger(__name__)

# 默认表头
DEFAULT_HEADER = ["房仓酒店id", "签约状态枚举值", "留言（文本最大500字符）"]


def generate_signing_status_excel(
    header: list = None,
    data_rows: list = None,
    file_name: str = "RFP_import_signing_status_file.xlsx",
) -> str:
    """
    生成签约状态导入 Excel 文件

    Args:
        header: 表头列表，默认 ["房仓酒店id", "签约状态枚举值", "留言（文本最大500字符）"]
        data_rows: 数据行列表，每行是一个列表，如 [["10086", "新标", ""]]
        file_name: 文件名，默认 "RFP_import_signing_status_file.xlsx"

    Returns:
        str: Excel 文件的绝对路径
    """
    if header is None:
        header = DEFAULT_HEADER
    if data_rows is None:
        data_rows = []

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(header)
    for row in data_rows:
        ws.append(row)

    temp_dir: Path = config.DATA_DIR / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    file_path = temp_dir / file_name

    # 如果文件已存在且被锁定，先尝试删除
    if file_path.exists():
        try:
            file_path.unlink()
        except PermissionError:
            logger.warning(f"旧文件被占用，无法删除: {file_path}")

    wb.save(str(file_path))
    logger.info(f"签约状态导入文件已生成: {file_path}")
    return str(file_path)