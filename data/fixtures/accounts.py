"""
账号相关的 fixture
提供各角色账号信息的便捷 fixture
"""

import pytest
from utils.config import config


@pytest.fixture
def operate_account():
    """
    运营平台账号 fixture
    返回运营端（Operate 角色）的账号信息
    """
    return config.get_account("operate")


@pytest.fixture
def hotel_account():
    """
    单体酒店账号 fixture
    返回酒店端（Hotel 角色）的账号信息
    """
    return config.get_account("hotel")


@pytest.fixture
def hotelgroup_account():
    """
    酒店集团账号 fixture
    返回酒店集团端（HotelGroup 角色）的账号信息
    """
    return config.get_account("hotelgroup")


@pytest.fixture(params=["operate", "hotel", "hotelgroup"])
def any_account(request):
    """
    任意账号 fixture（参数化）
    返回三个角色中任意一个的账号信息
    适用于需要测试多个角色相同功能的场景

    Args:
        request: pytest request 对象，提供参数化的角色名

    Returns:
        dict: 账号信息 {mobile, password, role_name}
    """
    return config.get_account(request.param)
