"""
超时配置管理模块
统一管理所有涉及超时的配置，避免在代码中硬编码超时值
所有超时值从 .env 文件中读取，确保可配置性
"""

from utils.config import config


class TimeoutConfig:
    """统一的超时配置管理类"""

    @staticmethod
    def get_page_load_timeout() -> int:
        """获取页面加载超时（毫秒）"""
        return config.timeout_page_load

    @staticmethod
    def get_element_timeout() -> int:
        """获取元素查询超时（毫秒）"""
        return config.timeout_element

    @staticmethod
    def get_navigation_timeout() -> int:
        """获取导航超时（毫秒）"""
        return config.timeout_navigation


# 创建全局超时配置实例
timeout_config = TimeoutConfig()