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
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    except Exception as e:
        logger.error(f"Supabase init failed: {e}")

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
