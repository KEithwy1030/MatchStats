# MatchStats 项目交接文档

## 项目概述

MatchStats 是一个足球数据同步服务，用于从 Football-Data.org 和竞彩官网获取比赛数据，提供统一的 API 和 Web 界面。

### 技术栈
- **后端**: FastAPI + aiosqlite + APScheduler
- **数据库**: SQLite (可迁移到 PostgreSQL)
- **端口**: 9999
- **Python**: 3.x

### 项目结构
```
E:\CursorData\MatchStats\
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 主程序
│   ├── config.py            # 配置管理 (Pydantic Settings)
│   ├── database/            # 数据库表结构定义
│   ├── repositories/        # 数据访问层 (CRUD)
│   ├── scrapers/           # API 客户端 (Football-Data + 竞彩)
│   ├── scheduler/          # 定时同步任务
│   ├── web/                # Web 界面 (HTML模板)
│   └── api/                # REST API 端点
├── scripts/
│   └── sync_now.py         # 手动触发同步脚本
├── data/                   # 数据库文件目录
├── .env                    # 环境变量配置
├── requirements.txt        # Python 依赖
└── start.ps1               # Windows 启动脚本
```

---

## 本次工作内容 (2025-01-28)

### 1. 数据库表扩展

新增/扩展了以下数据表：

| 表名 | 说明 | 字段数 |
|-----|------|-------|
| fd_leagues | 联赛信息 | 8 |
| fd_teams | 球队基础信息 | 10 |
| fd_team_coaches | 球队教练 | 9 |
| fd_team_squads | 球队阵容 | 10 |
| fd_matches | 比赛(赛程+结果) | 18 |
| fd_match_details | 比赛详情(阵容、红黄牌) | 13 |
| fd_match_goals | 进球记录 | 10 |
| fd_standings | 积分榜 | 14 |
| fd_scorers | 射手榜 | 12 |
| sporttery_matches | 竞彩比赛 | 11 |

### 2. 新增同步任务

实现了以下同步方法：

| 方法 | API端点 | 频率 | 状态 |
|-----|---------|------|------|
| sync_fd_competitions | /competitions, /competitions/{id} | 1天 | ✅ |
| sync_fd_teams | /competitions/{id}/teams | 1天 | ✅ |
| sync_fd_scheduled | /competitions/{id}/matches?status=SCHEDULED | 1天 | ✅ |
| sync_fd_results | /competitions/{id}/matches?status=FINISHED | 5分钟 | ✅ |
| sync_fd_standings | /competitions/{id}/standings | 1小时 | ✅ |
| sync_fd_scorers | /competitions/{id}/scorers | 6小时 | ✅ |
| sync_fd_team_details | /teams/{id} | 1天 | ✅ |
| sync_fd_live_match_details | /matches/{id} | 5分钟 | ✅ |
| sync_sporttery_matches | 竞彩API | 12小时 | ✅ |

### 3. API 覆盖率

Football-Data.org 免费 API 所有端点已全部覆盖：

- ✅ /competitions - 联赛列表
- ✅ /competitions/{id} - 联赛详情
- ✅ /competitions/{id}/matches - 比赛列表
- ✅ /competitions/{id}/standings - 积分榜
- ✅ /competitions/{id}/scorers - 射手榜
- ✅ /competitions/{id}/teams - 球队列表
- ✅ /teams/{id} - 球队详情(教练/阵容)
- ✅ /matches/{id} - 比赛详情(进球/红黄牌)

### 4. 限流策略

遵守 Football-Data.org 免费账户限制：**10次/分钟**

- 每次API调用后 `await asyncio.sleep(6)`
- 高频任务(5分钟)每次只同步10场比赛详情

---

## 遇到的问题及解决方案

### 问题1: SQL 插入列数不匹配

**错误**: `sqlite3.OperationalError: 16 values for 17 columns`

**原因**: `app/repositories/__init__.py` 第39行 VALUES 子句只有16个问号，但定义了17个列

**解决**: 将 `VALUES (?, ?, ..., ?)` 从16个问号改为17个

**位置**: [app/repositories/__init__.py:39](app/repositories/__init__.py#L39)

### 问题2: MONITORED_LEAGUES 配置解析

**错误**: Pydantic 无法将逗号分隔字符串解析为 List[str]

**解决**:
```python
# app/config.py
MONITORED_LEAGUES: str = "PL,BL1,SA,PD,FL1,CL"

@property
def monitored_leagues_list(self) -> List[str]:
    return [s.strip() for s in self.MONITORED_LEAGUES.split(",") if s.strip()]
```

### 问题3: 积分榜 API 返回格式不一致

**错误**: `'list' object has no attribute 'get'`

**原因**: API 有时返回 list，有时返回 dict with "standings" key

**解决**: 在 scraper 中兼容两种格式
```python
if isinstance(data, list):
    return data
return data.get("standings", [])
```

### 问题4: main.py 路径问题

**问题**: 项目根目录没有 main.py

**正确启动方式**: `python -m app.main`

**Windows 启动**: `.\start.ps1`

---

## 当前数据状态 (最新同步)

| 数据类型 | 数量 |
|---------|-----|
| 联赛 | 13 个 |
| 球队 | 110 支 |
| 教练 | 110 名 |
| 球员 | 3630 名 |
| 比赛 | 1941 场 |
| 积分榜 | 132 条 |
| 射手榜 | 60 条 |
| 比赛详情 | 10 场 |
| 竞彩比赛 | 46 场 |

---

## 使用说明

### 启动服务

```powershell
# Windows
cd E:\CursorData\MatchStats
.\start.ps1

# 或手动启动
venv\Scripts\python.exe -m app.main
```

### 手动同步数据

```powershell
venv\Scripts\python.exe scripts\sync_now.py
```

### 访问地址

- **Web 界面**: http://localhost:9999/
- **API 文档**: http://localhost:9999/docs
- **API 根路径**: http://localhost:9999/api/

### 环境变量配置 (.env)

```env
FD_API_TOKEN=your_token_here
DB_PATH=./data/matchstats.db
PORT=9999
HOST=0.0.0.0
MONITORED_LEAGUES=PL,BL1,SA,PD,FL1,CL
```

---

## 待办事项

无 - 所有计划功能已完成。

---

## 注意事项

1. **API 限流**: 严格遵守 10次/分钟 限制，否则会被封禁
2. **数据库路径**: 默认 `./data/matchstats.db`，迁移时注意路径
3. **同步频率**: 球队详情同步较慢(110支球队需约11分钟)，避免频繁手动触发
4. **赛季信息**: API 返回的 season 可能是 dict 或 int，注意处理

---

## 修改历史

| 日期 | 内容 |
|------|------|
| 2025-01-28 | 完成所有 API 数据同步，扩展数据库表结构 |
