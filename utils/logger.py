"""
日志工具模块
提供统一的日志记录接口
"""

import logging
import sys
from typing import Optional


class Logger:
    """日志管理类"""

    _loggers = {}

    @staticmethod
    def get_logger(name: str, level: str = "INFO") -> logging.Logger:
        """
        获取或创建日志记录器

        Args:
            name: 日志记录器名称（通常为模块名）
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)

        Returns:
            logging.Logger 实例
        """
        if name in Logger._loggers:
            return Logger._loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))

        # 避免重复添加处理器
        if not logger.handlers:
            # 控制台处理器
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, level.upper(), logging.INFO))

            # 格式化
            formatter = logging.Formatter(
                fmt="%(asctime)s [%(name)s] [%(levelname)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            console_handler.setFormatter(formatter)

            logger.addHandler(console_handler)

        Logger._loggers[name] = logger
        return logger


# 便捷函数
def get_logger(name: str, level: str = "INFO") -> logging.Logger:
    """获取日志记录器"""
    return Logger.get_logger(name, level)
