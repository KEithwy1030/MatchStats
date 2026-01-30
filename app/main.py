"""
MatchStats - 比赛数据API服务
主应用入口
"""
import sys
import io
import logging

# 修复 Windows 控制台编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn

from app.config import settings, ensure_data_dir, ensure_logs_dir
from app.database import init_db
from app.api import fd_router, sporttery_router, system_router
from app.scheduler import scheduler
from app.web import web_router
from fastapi.staticfiles import StaticFiles
import os

# 配置日志
log_dir = ensure_logs_dir()
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'{log_dir}/matchstats.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动
    logger.info("=" * 50)
    logger.info("MatchStats 服务启动中...")
    logger.info(f"数据库: {settings.DB_PATH}")
    logger.info(f"端口: {settings.PORT}")
    logger.info(f"监控联赛: {', '.join(settings.monitored_leagues_list)}")

    # 初始化数据库
    await init_db()

    # 启动调度器
    scheduler.start()

    logger.info("MatchStats 服务已启动")
    logger.info("=" * 50)

    yield

    # 关闭
    logger.info("MatchStats 服务关闭中...")
    scheduler.stop()
    logger.info("MatchStats 服务已关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title="MatchStats API",
    description="比赛数据API服务 - 为Agent提供实时比赛数据",
    version="0.1.0",
    lifespan=lifespan
)

# 注册路由
app.include_router(web_router)      # Web界面路由（包含首页）
app.include_router(fd_router)       # Football-Data API
app.include_router(sporttery_router)  # 竞彩 API
app.include_router(system_router)   # 系统 API

# 静态文件
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


def main():
    """主函数"""
    ensure_data_dir()
    ensure_logs_dir()

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )


if __name__ == "__main__":
    main()
