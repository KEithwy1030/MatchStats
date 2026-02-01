"""
数据库初始化 (Supabase Agent版)
"""
from supabase import create_client, Client
from app.config import settings
import logging
import os

logger = logging.getLogger(__name__)

supabase: Client = None

# 初始化 Supabase 客户端
if settings.SUPABASE_URL and settings.SUPABASE_KEY:
    try:
        url = settings.SUPABASE_URL.strip().strip("'").strip('"')
        key = settings.SUPABASE_KEY.strip().strip("'").strip('"')
        supabase = create_client(url, key)
        logger.info("Supabase 客户端初始化成功")
    except Exception as e:
        logger.error(f"Supabase init failed: {e}")
else:
    logger.warning("SUPABASE_URL or SUPABASE_KEY is missing in settings")

async def init_db():
    """
    Supabase 模式下的初始化
    """
    if not supabase:
        logger.warning("Supabase client not initialized! API calls will fail.")
        return

    logger.info("Using Supabase Cloud Database.")
    
    # 检测连接
    # try:
    #     supabase.table('fd_matches').select("count", count="exact").limit(1).execute()
    #     logger.info("Supabase connected successfully.")
    # except Exception as e:
    #     logger.error(f"Supabase connection check failed: {e}")

async def get_db():
    """保留兼容接口"""
    return supabase
