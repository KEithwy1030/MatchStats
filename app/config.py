"""
应用配置
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List
import os


class Settings(BaseSettings):
    """应用配置"""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        env_file_encoding="utf-8"
    )

    # API Token
    FD_API_TOKEN: str = ""

    # Supabase (Cloud Database)
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""

    # 数据库
    DB_PATH: str = "./data/matchstats.db"

    # 服务
    PORT: int = 9999
    HOST: str = "0.0.0.0"
    DEBUG: bool = False

    # 日志
    LOG_LEVEL: str = "INFO"

    # 监控的联赛 (从逗号分隔字符串解析)
    MONITORED_LEAGUES: str = "PL,BL1,SA,PD,FL1,CL"

    @property
    def monitored_leagues_list(self) -> List[str]:
        """获取联赛列表"""
        return [s.strip() for s in self.MONITORED_LEAGUES.split(",") if s.strip()]

    # Football-Data.org 限流
    FD_RATE_LIMIT: int = 10  # 每分钟10次
    FD_RATE_WINDOW: int = 60  # 60秒窗口

    # 更新频率（分钟）
    # SCHEDULED 比赛是完整赛季赛程，变化少，低频更新即可
    UPDATE_FD_SCHEDULED: int = 1440  # 1天（赛程很少变化）
    # FINISHED 比赛结果需要高频更新，获取最新比分
    UPDATE_FD_RESULTS: int = 5  # 5分钟
    UPDATE_FD_STANDINGS: int = 60  # 1小时（积分榜比赛后更新）
    UPDATE_FD_SCORERS: int = 360  # 6小时（射手榜）
    UPDATE_FD_TEAMS: int = 1440  # 1天
    UPDATE_SPORTTERY: int = 720  # 12小时


# 全局配置实例
settings = Settings()


def ensure_data_dir():
    """确保数据目录存在"""
    data_dir = os.path.dirname(settings.DB_PATH)
    if data_dir and not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)


def ensure_logs_dir():
    """确保日志目录存在"""
    logs_dir = "./logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir, exist_ok=True)
    return logs_dir
