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

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import uvicorn
from supabase import create_client, Client

from app.config import settings, ensure_data_dir, ensure_logs_dir
from app.database import init_db
from app.api import fd_router, sporttery_router, system_router
from app.scheduler import scheduler
from app.web import web_router
from fastapi.staticfiles import StaticFiles
import os

# 初始化 Supabase 客户端
supabase: Client = None
if settings.SUPABASE_URL and settings.SUPABASE_KEY:
    # Vercel Deployment Trigger: 2026-01-31 00:30 - PREDICTIONS ERROR DEBUG
    # Added detailed traceback to /predictions to find source of [Errno 16]
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

# 配置日志：默认仅输出到控制台
# 只有在环境变量中明确指定了匹配的路径时才尝试写文件
handlers = [logging.StreamHandler()]

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=handlers
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    import shutil
    # 启动
    logger.info("=" * 50)
    logger.info("MatchStats 服务启动中...")
    
    # Vercel 环境处理：将只读 DB 拷贝到可写的 /tmp 目录
    if os.environ.get("VERCEL"):
        temp_db = "/tmp/matchstats.db"
        source_db = os.path.abspath(settings.DB_PATH)
        logger.info(f"Vercel: 准备迁移数据库. 源路径: {source_db}, 目标路径: {temp_db}")
        
        if os.path.exists(source_db):
            try:
                # 拷贝前先确保目录存在并打印大小
                size = os.path.getsize(source_db)
                logger.info(f"Vercel: 发现源数据库, 大小: {size} bytes")
                shutil.copy(source_db, temp_db)
                settings.DB_PATH = temp_db
                logger.info(f"Vercel: 数据库迁移成功 -> {settings.DB_PATH}")
            except Exception as e:
                logger.error(f"Vercel: 拷贝数据库失败: {e}")
        else:
            # 探测当前目录
            logger.error(f"Vercel: 源数据库文件不存在: {source_db}")
            logger.info(f"Vercel: 当前工作目录: {os.getcwd()}")
            try:
                logger.info(f"Vercel: 根目录内容: {os.listdir('.')}")
                if os.path.exists('data'):
                    logger.info(f"Vercel: data 目录内容: {os.listdir('data')}")
            except:
                pass

    # 初始化数据库
    await init_db()

    # 启动调度器 (Vercel 环境下禁用)
    if not os.environ.get("VERCEL"):
        logger.info(f"数据库: {settings.DB_PATH}")
        logger.info(f"端口: {settings.PORT}")
        scheduler.start()
        logger.info("MatchStats 服务已启动")
    else:
        logger.info("Vercel 环境：跳过调度器启动")

    logger.info("=" * 50)

    yield

    # 关闭
    if not os.environ.get("VERCEL"):
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

@app.get("/predictions", response_class=HTMLResponse)
async def get_predictions(request: Request):
    """获取云端博彩预测列表"""
    try:
        import traceback
        if not supabase:
            return "<h1>Supabase 未配置</h1>"
        
        response = supabase.table("match_predictions").select("*").order("created_at", desc=True).limit(20).execute()
        predictions = response.data
        
        html_content = "<html><head><meta charset='utf-8'><title>比赛预测</title><style>body{font-family:sans-serif;max-width:800px;margin:20px auto;line-height:1.6;background:#f4f7f6;padding:0 15px;} .card{background:#fff;border-radius:12px;box-shadow:0 4px 6px rgba(0,0,0,0.1);padding:20px;margin-bottom:25px;border-left:5px solid #2ecc71;} h2{color:#2c3e50;margin-top:0;} pre{white-space:pre-wrap;background:#fafafa;padding:15px;border-radius:6px;border:1px solid #eee;font-size:14px;color:#34495e;}</style></head><body>"
        html_content += "<h1>⚽ 比赛深度预测 (Grok)</h1>"
        
        if not predictions:
            html_content += "<p>暂无预测数据，请运行抓取脚本。</p>"
        
        for p in predictions:
            html_content += f"""
            <div class='card'>
                <h2>{p['home_team_name']} vs {p['away_team_name']}</h2>
                <p><small style='color:#7f8c8d;'>时间: {p.get('created_at', '未知')}</small></p>
                <hr style='border:none;border-top:1px solid #eee;margin:15px 0;'>
                <pre>{p['raw_prediction_text']}</pre>
            </div>
            """
        
        html_content += "</body></html>"
        return html_content
    except Exception as e:
        import traceback
        return f"<h1>页面错误: {str(e)}</h1><pre>{traceback.format_exc()}</pre>"

# 注册路由
app.include_router(web_router)      # Web界面路由（包含首页）
app.include_router(fd_router)       # Football-Data API
app.include_router(sporttery_router)  # 竞彩 API
app.include_router(system_router)   # 系统 API

# 静态文件
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.environ.get("VERCEL") and not os.path.exists(static_dir):
    os.makedirs(static_dir)

# 即使文件夹不存在，在 Vercel 上也要挂载，否则容易报错
if os.path.exists(static_dir):
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
