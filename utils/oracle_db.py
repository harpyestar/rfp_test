"""
Oracle 数据库连接工具
提供 RFP 项目相关的酒店数据查询功能

使用方法:
    # 方式一：上下文管理器
    with OracleDB() as db:
        hotels = db.query_normal_hotels(project_id)

    # 方式二：便捷函数（自动连接/关闭）
    hotels = get_normal_hotels(project_id)

# 关于 Oracle Instant Client（thick 模式）
# 此数据库服务器需要 thick 模式连接，请下载 Oracle Instant Client：
# https://www.oracle.com/database/technologies/instant-client/download.html
# 下载 Basic 包并解压后，在 .env 中配置 ORACLE_CLIENT_PATH=解压路径
# 例如：ORACLE_CLIENT_PATH=D:/soft/instantclient_21_14
"""

import os
import oracledb
from typing import List, Dict
from utils.logger import get_logger

logger = get_logger(__name__)

# Oracle 数据库连接配置
ORACLE_CONFIG = {
    "host": "172.16.88.72",
    "port": 1521,
    "service_name": "fangcangdb",
    "user": "htl_rfp",
    "password": "hf84brfp",
}

# Thick 模式初始化状态
_ORACLE_CLIENT_INITIALIZED = False


def _ensure_oracle_client() -> bool:
    """
    尝试初始化 Oracle Client（thick 模式）
    若 ORACLE_CLIENT_PATH 环境变量已配置则使用该路径，否则自动查找

    Returns:
        True  thick 模式初始化成功
        False  thick 模式不可用，后续将使用 thin 模式
    """
    global _ORACLE_CLIENT_INITIALIZED
    if _ORACLE_CLIENT_INITIALIZED:
        return True

    client_path = os.getenv("ORACLE_CLIENT_PATH")
    try:
        if client_path:
            oracledb.init_oracle_client(lib_dir=client_path)
            logger.info(f"Oracle Client 初始化成功（thick 模式），路径: {client_path}")
        else:
            oracledb.init_oracle_client()
            logger.info("Oracle Client 初始化成功（thick 模式，自动查找路径）")
        _ORACLE_CLIENT_INITIALIZED = True
        return True
    except Exception as e:
        logger.warning(f"Oracle Client 不可用，将尝试 thin 模式: {e}")
        return False


class OracleDB:
    """Oracle 数据库操作类"""

    def __init__(self):
        self.connection = None

    def connect(self) -> None:
        """
        建立 Oracle 数据库连接

        优先尝试 thick 模式（需要 Oracle Instant Client），
        若不可用则回退到 thin 模式（部分数据库版本不支持）。
        若 thin 模式也失败，会给出配置提示。
        """
        logger.info("正在连接 Oracle 数据库 ...")
        dsn = oracledb.makedsn(
            ORACLE_CONFIG["host"],
            ORACLE_CONFIG["port"],
            service_name=ORACLE_CONFIG["service_name"],
        )

        # 先尝试 thick 模式
        thick_available = _ensure_oracle_client()

        try:
            self.connection = oracledb.connect(
                user=ORACLE_CONFIG["user"],
                password=ORACLE_CONFIG["password"],
                dsn=dsn,
            )
            mode = "thick" if thick_available else "thin"
            logger.info(f"Oracle 数据库连接成功（{mode} 模式）")
        except oracledb.Error as e:
            error_msg = str(e)
            # 如果 thin 模式失败且提示版本不支持，引导用户配置 Instant Client
            if "DPY-3010" in error_msg:
                raise RuntimeError(
                    "Oracle 数据库连接失败：该数据库版本不支持 thin 模式。\n"
                    "请下载 Oracle Instant Client 并配置 ORACLE_CLIENT_PATH：\n"
                    "1. 下载地址：https://www.oracle.com/database/technologies/instant-client/download.html\n"
                    "2. 选择 Windows → Basic 包下载并解压\n"
                    "3. 在 .env 文件中添加：ORACLE_CLIENT_PATH=解压后的目录路径\n"
                    "   例如：ORACLE_CLIENT_PATH=D:/soft/instantclient_21_14"
                ) from e
            raise

    def close(self) -> None:
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            logger.info("Oracle 数据库连接已关闭")

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def query_normal_hotels(self, project_id: str) -> List[Dict]:
        """
        查询普通酒店名单（T_PROJECT_INTENT_HOTEL）
        根据 PROJECT_ID 和 INVITE_STATUE=1 过滤

        Args:
            project_id: 项目 ID

        Returns:
            List[Dict]: [{hotel_id, hotel_name}, ...]
        """
        sql = """
        SELECT t.HOTEL_ID, h.CHN_NAME
        FROM T_PROJECT_INTENT_HOTEL t
        JOIN HTL_INFO.T_HOTEL h ON t.HOTEL_ID = h.HOTELID
        WHERE t.PROJECT_ID = :project_id AND t.INVITE_STATUS = 1
        ORDER BY t.HOTEL_ID
        """
        cursor = self.connection.cursor()
        cursor.execute(sql, project_id=project_id)
        rows = cursor.fetchall()
        cursor.close()
        logger.info(f"查询到 {len(rows)} 条普通酒店记录")
        return [{"hotel_id": str(row[0]), "hotel_name": row[1]} for row in rows]

    def query_group_hotels(self, project_id: str) -> List[Dict]:
        """
        查询集团意向单店酒店名单（T_PROJECT_INVITE_HOTEL）
        根据 PROJECT_ID 过滤

        Args:
            project_id: 项目 ID

        Returns:
            List[Dict]: [{hotel_id, hotel_name}, ...]
        """
        sql = """
        SELECT t.HOTEL_ID, h.CHN_NAME
        FROM T_PROJECT_INVITE_HOTEL t
        JOIN HTL_INFO.T_HOTEL h ON t.HOTEL_ID = h.HOTELID
        WHERE t.PROJECT_ID = :project_id
        ORDER BY t.HOTEL_ID
        """
        cursor = self.connection.cursor()
        cursor.execute(sql, project_id=project_id)
        rows = cursor.fetchall()
        cursor.close()
        logger.info(f"查询到 {len(rows)} 条集团酒店记录")
        return [{"hotel_id": str(row[0]), "hotel_name": row[1]} for row in rows]


# ======================== 便捷查询函数（自动连接/关闭）=======================

def get_normal_hotels(project_id: str) -> List[Dict]:
    """查询普通酒店名单，自动连接和关闭数据库"""
    with OracleDB() as db:
        return db.query_normal_hotels(project_id)


def get_group_hotels(project_id: str) -> List[Dict]:
    """查询集团酒店名单，自动连接和关闭数据库"""
    with OracleDB() as db:
        return db.query_group_hotels(project_id)


# ======================== 数据库连接测试 ========================

def test_connection() -> bool:
    """
    测试 Oracle 数据库连接是否正常（独立运行，不需外部依赖）

    Returns:
        True  连接成功
        False 连接失败

    使用方式:
        python -c "from utils.oracle_db import test_connection; test_connection()"
    """
    print("=" * 60)
    print("Oracle 数据库连接测试")
    print("=" * 60)
    print(f"目标: {ORACLE_CONFIG['host']}:{ORACLE_CONFIG['port']}/{ORACLE_CONFIG['service_name']}")
    print(f"用户: {ORACLE_CONFIG['user']}")
    print()

    try:
        with OracleDB() as db:
            # 执行简单查询验证
            cursor = db.connection.cursor()
            cursor.execute("SELECT 1 FROM DUAL")
            result = cursor.fetchone()
            cursor.close()

            if result and result[0] == 1:
                print("[OK] 数据库连接正常")
                print(f"[OK] 基础查询验证通过: SELECT 1 FROM DUAL = {result[0]}")

            # 查询表是否存在
            tables_to_check = [
                ("HTL_INFO.T_PROJECT_INTENT_HOTEL", "普通酒店意向表"),
                ("T_PROJECT_INVITE_HOTEL", "集团邀请酒店表"),
                ("HTL_INFO.T_HOTEL", "酒店信息表"),
            ]
            for full_name, desc in tables_to_check:
                short = full_name.split(".")[-1]
                cursor = db.connection.cursor()
                cursor.execute(
                    "SELECT COUNT(*) FROM ALL_TABLES WHERE TABLE_NAME = :name",
                    name=short,
                )
                count = cursor.fetchone()[0]
                cursor.close()
                if count > 0:
                    print(f"[OK] 表 {full_name}（{desc}）可访问")
                else:
                    print(f"[WARN] 表 {full_name}（{desc}）不可访问")

            # 验证实际 SQL 查询
            print()
            print("--- 验证实际 SQL ---")
            sql_checks = [
                "SELECT COUNT(*) FROM T_PROJECT_INTENT_HOTEL",
                "SELECT COUNT(*) FROM T_PROJECT_INVITE_HOTEL",
                "SELECT COUNT(*) FROM HTL_INFO.T_HOTEL",
            ]
            for sql in sql_checks:
                cursor = db.connection.cursor()
                try:
                    cursor.execute(sql)
                    print(f"[OK] {sql}")
                except oracledb.Error as e:
                    print(f"[FAIL] {sql} -> {e}")
                finally:
                    cursor.close()

        print()
        print("[OK] 数据库连接测试通过")
        print("=" * 60)
        return True

    except Exception as e:
        print()
        print(f"[FAIL] 数据库连接失败: {e}")
        print("=" * 60)
        return False

if __name__ == '__main__':
    test_connection()