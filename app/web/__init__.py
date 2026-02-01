from fastapi import APIRouter
from fastapi.responses import HTMLResponse, FileResponse
from datetime import datetime
import os

from app.repositories import FDRepository, SportteryRepository, LogRepository
from app.config import settings

web_router = APIRouter(tags=["Web界面"])

fd_repo = FDRepository()
sporttery_repo = SportteryRepository()
log_repo = LogRepository()

# ... (Existing Dicts can stay) ...

@web_router.get("/")
async def index():
    """新版 Dashboard"""
    return FileResponse(os.path.join("app", "static", "index.html"))

# Preserve old routes just in case, or we can deprecate them.


# 联赛映射
LEAGUE_MAP = {
    "PL": "英超",
    "BL1": "德甲",
    "SA": "意甲",
    "PD": "西甲",
    "FL1": "法甲",
    "CL": "欧冠"
}

LEAGUE_FULL_NAMES = {
    "PL": "英超 Premier League",
    "BL1": "德甲 Bundesliga",
    "SA": "意甲 Serie A",
    "PD": "西甲 La Liga",
    "FL1": "法甲 Ligue 1",
    "CL": "欧冠 Champions League"
}


# 基础模板
BASE_TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- SEO 核心标签 -->
    <title>{title} - MatchStats 足球数据中心 | 实时比分、积分榜与预测</title>
    <meta name="description" content="MatchStats 提供全球顶级足球联赛（英超、西甲、意甲、德甲、欧冠）的实时比分、积分榜、射手榜及最新数据预测。数据源自官网，每20分钟自动更新。">
    <meta name="keywords" content="足球比分, 实时比分, 足球积分榜, 英超数据, 足球预测, 竞彩比分, MatchStats">
    <meta name="author" content="MatchStats Team">
    
    <!-- 社交媒体/分享优化 (Open Graph) -->
    <meta property="og:title" content="{title} - MatchStats 足球数据中心">
    <meta property="og:description" content="实时追踪全球顶级足球赛事。英超、西甲、意甲比分一网打尽。">
    <meta property="og:url" content="https://kmatch-stats.vercel.app/">
    <meta property="og:type" content="website">
    <meta property="og:image" content="https://kmatch-stats.vercel.app/static/og-image.jpg">
    
    <!-- 移动端优化 -->
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="theme-color" content="#0a2540">
    <style>
        :root {{
            --primary: #0a2540;
            --primary-light: #1e3a5f;
            --accent: #3b82f6;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --bg: #f8fafc;
            --card: #ffffff;
            --border: #e2e8f0;
            --text: #1e293b;
            --text-muted: #64748b;
            --text-light: #94a3b8;
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display",
                       "Segoe UI", system-ui, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.5;
            min-height: 100vh;
        }}

        /* 导航栏 */
        .navbar {{
            background: var(--card);
            border-bottom: 1px solid var(--border);
            position: sticky;
            top: 0;
            z-index: 100;
        }}

        .nav-inner {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            height: 56px;
        }}

        .logo {{
            font-size: 18px;
            font-weight: 600;
            color: var(--primary);
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .logo span {{
            color: var(--accent);
        }}

        .nav-links {{
            display: flex;
            gap: 4px;
        }}

        .nav-link {{
            padding: 8px 14px;
            color: var(--text-muted);
            text-decoration: none;
            font-size: 14px;
            border-radius: 6px;
            transition: all 0.15s ease;
        }}

        .nav-link:hover {{
            color: var(--text);
            background: var(--bg);
        }}

        .nav-link.active {{
            color: var(--accent);
            background: #eff6ff;
        }}

        /* 主容器 */
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 24px;
        }}

        /* 页面标题 */
        .page-header {{
            margin-bottom: 24px;
        }}

        .page-title {{
            font-size: 24px;
            font-weight: 600;
            color: var(--primary);
        }}

        .page-subtitle {{
            font-size: 14px;
            color: var(--text-muted);
            margin-top: 4px;
        }}

        /* 卡片 */
        .card {{
            background: var(--card);
            border-radius: 12px;
            border: 1px solid var(--border);
            overflow: hidden;
        }}

        .card-header {{
            padding: 16px 20px;
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}

        .card-title {{
            font-size: 15px;
            font-weight: 600;
            color: var(--primary);
        }}

        .card-body {{
            padding: 0;
        }}

        /* 统计网格 */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}

        .stat-card {{
            background: var(--card);
            border-radius: 12px;
            border: 1px solid var(--border);
            padding: 20px;
            display: flex;
            align-items: center;
            gap: 16px;
        }}

        .stat-icon {{
            width: 44px;
            height: 44px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
        }}

        .stat-icon.blue {{ background: #eff6ff; }}
        .stat-icon.green {{ background: #f0fdf4; }}
        .stat-icon.purple {{ background: #faf5ff; }}
        .stat-icon.orange {{ background: #fef3c7; }}

        .stat-content {{
            flex: 1;
        }}

        .stat-value {{
            font-size: 24px;
            font-weight: 700;
            color: var(--primary);
            line-height: 1;
        }}

        .stat-label {{
            font-size: 13px;
            color: var(--text-muted);
            margin-top: 4px;
        }}

        /* 表格 */
        .table-wrapper {{
            overflow-x: auto;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }}

        th {{
            text-align: left;
            padding: 12px 16px;
            background: var(--bg);
            color: var(--text-muted);
            font-weight: 600;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-bottom: 1px solid var(--border);
        }}

        td {{
            padding: 14px 16px;
            border-bottom: 1px solid var(--border);
            color: var(--text);
        }}

        tr:last-child td {{
            border-bottom: none;
        }}

        tr:hover td {{
            background: #f8fafc;
        }}

        /* 状态标签 */
        .badge {{
            display: inline-flex;
            align-items: center;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 500;
        }}

        .badge-success {{ background: #f0fdf4; color: var(--success); }}
        .badge-danger {{ background: #fef2f2; color: var(--danger); }}
        .badge-warning {{ background: #fffbeb; color: var(--warning); }}
        .badge-neutral {{ background: var(--bg); color: var(--text-muted); }}

        /* 筛选器 */
        .filters {{
            display: flex;
            gap: 12px;
            margin-bottom: 16px;
            flex-wrap: wrap;
        }}

        .filter-select, .filter-input {{
            padding: 8px 12px;
            border: 1px solid var(--border);
            border-radius: 6px;
            font-size: 14px;
            background: var(--card);
            color: var(--text);
        }}

        .filter-btn {{
            padding: 8px 16px;
            background: var(--accent);
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            cursor: pointer;
            transition: background 0.15s;
        }}

        .filter-btn:hover {{
            background: #2563eb;
        }}

        .filter-btn.secondary {{
            background: var(--bg);
            color: var(--text-muted);
        }}

        .filter-btn.secondary:hover {{
            background: var(--border);
        }}

        /* 选项卡 */
        .tabs {{
            display: flex;
            gap: 8px;
            padding: 16px 20px;
            border-bottom: 1px solid var(--border);
            background: var(--bg);
        }}

        .tab {{
            padding: 8px 14px;
            border-radius: 6px;
            font-size: 14px;
            color: var(--text-muted);
            text-decoration: none;
            transition: all 0.15s;
        }}

        .tab:hover {{
            color: var(--text);
            background: var(--card);
        }}

        .tab.active {{
            background: var(--card);
            color: var(--accent);
            font-weight: 500;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}

        /* 链接 */
        a {{
            color: var(--accent);
            text-decoration: none;
            transition: color 0.15s;
        }}

        a:hover {{
            color: #2563eb;
        }}

        /* 空状态 */
        .empty-state {{
            text-align: center;
            padding: 60px 20px;
            color: var(--text-muted);
        }}

        /* 积分榜特殊样式 */
        .standings-table th {{
            text-align: center;
        }}

        .standings-table th:first-child,
        .standings-table td:first-child {{
            text-align: left;
        }}

        .standings-table td {{
            text-align: center;
        }}

        .standings-table td:first-child {{
            text-align: left;
        }}

        .position {{
            width: 40px;
            height: 40px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            font-weight: 600;
            font-size: 14px;
        }}

        .position-top {{
            background: #f0fdf4;
            color: var(--success);
        }}

        .position-europa {{
            background: #fef3c7;
            color: var(--warning);
        }}

        .position-normal {{
            background: var(--bg);
            color: var(--text-muted);
        }}

        .points {{
            font-weight: 700;
            color: var(--primary);
        }}

        /* 响应式 */
        @media (max-width: 768px) {{
            .nav-links {{
                display: none;
            }}
            .stats-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="nav-inner">
            <a href="/" class="logo">Match<span>Stats</span></a>
            <div class="nav-links">
                {nav_links}
            </div>
        </div>
    </nav>

    <div class="container">
        {content}
    </div>
</body>
</html>'''


def get_nav_links(active: str = "") -> str:
    """生成导航链接"""
    links = [
        ("index", "📊 首页", "/"),
        ("matches", "🏆 比赛", "/matches"),
        ("standings", "📈 积分榜", "/standings"),
        ("leagues", "🏁 联赛", "/leagues"),
        ("teams", "👥 球队", "/teams"),
        ("logs", "📋 日志", "/logs"),
    ]

    links_html = []
    for name, label, url in links:
        active_class = " active" if name == active else ""
        links_html.append(f'<a class="nav-link{active_class}" href="{url}">{label}</a>')
    return "\n                ".join(links_html)





@web_router.get("/matches", response_class=HTMLResponse)
async def matches_page(
    source: str = "fd",
    date: str = "",
    league: str = "",
    status: str = ""
):
    """比赛列表页面"""
    if source == "fd":
        matches = await fd_repo.get_matches(
            date=date if date else None,
            league=league if league else None,
            status=status if status else None,
            limit=200
        )
        source_name = "欧洲联赛"
    else:
        matches = await sporttery_repo.get_matches(
            date=date if date else None,
            status=status if status else None,
            limit=200
        )
        source_name = "竞彩官网"

    # 构建比赛行
    matches_rows = ""
    for m in matches[:100]:
        if source == "fd":
            league_code = m.get('league_code', '')
            league_name = LEAGUE_MAP.get(league_code, league_code)
            match_info = f"{m.get('home_team_name', '')} vs {m.get('away_team_name', '')}"
            match_time = m.get('match_date', '')[:16] if m.get('match_date') else ''
            score = ""
            if m.get('home_score') is not None:
                score = f"{m.get('home_score')} - {m.get('away_score')}"
        else:
            league_name = m.get('league', '')
            match_info = f"{m.get('home_team', '')} vs {m.get('away_team', '')}"
            match_time = m.get('match_time', '')[:16] if m.get('match_time') else ''
            score = m.get('actual_score') or "-"

        matches_rows += f"""
        <tr>
            <td><span class="badge badge-neutral">{league_name}</span></td>
            <td>{match_info}</td>
            <td style="color:var(--text-muted);font-size:13px;">{match_time}</td>
            <td style="font-weight:600;">{score}</td>
        </tr>"""

    # 联赛筛选选项
    league_options = '<option value="">全部联赛</option>'
    if source == "fd":
        for code, name in LEAGUE_MAP.items():
            selected = 'selected' if league == code else ''
            league_options += f'<option value="{code}" {selected}>{name}</option>'

    content = f'''
    <div class="page-header">
        <h1 class="page-title">比赛列表</h1>
        <p class="page-subtitle">{source_name} · 共 {len(matches)} 场比赛</p>
    </div>

    <div class="card">
        <div class="tabs">
            <a class="tab{' active' if source == 'fd' else ''}" href="/matches?source=fd">欧洲联赛</a>
            <a class="tab{' active' if source == 'sporttery' else ''}" href="/matches?source=sporttery">竞彩官网</a>
        </div>
        <div style="padding:16px 20px;border-bottom:1px solid var(--border);">
            <div class="filters">
                <select class="filter-select" id="leagueFilter">{league_options}</select>
                <input class="filter-input" type="date" id="dateFilter" value="{date}">
                <button class="filter-btn" onclick="applyFilters()">应用筛选</button>
                <button class="filter-btn secondary" onclick="window.location.href='/matches?source={source}'">重置</button>
            </div>
        </div>
        <div class="card-body">
            <div class="table-wrapper">
                <table>
                    <thead><tr><th>联赛</th><th>对阵</th><th>时间</th><th>比分</th></tr></thead>
                    <tbody>{matches_rows}</tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        function applyFilters() {{
            const date = document.getElementById('dateFilter').value;
            const league = document.getElementById('leagueFilter').value;
            let url = '/matches?source={source}';
            if (date) url += '&date=' + date;
            if (league) url += '&league=' + league;
            window.location.href = url;
        }}
    </script>
    '''

    return BASE_TEMPLATE.format(
        title="比赛列表",
        nav_links=get_nav_links("matches"),
        content=content
    )


@web_router.get("/logs", response_class=HTMLResponse)
async def logs_page(source: str = ""):
    """日志查看页面"""
    logs = await log_repo.get_logs(source=source if source else None, limit=100)

    logs_rows = ""
    for log in logs:
        status = log.get('status', '')
        status_badge = f'<span class="badge badge-success">成功</span>' if status == 'success' else f'<span class="badge badge-danger">失败</span>'
        source_name = {'football_data': 'Football-Data', 'sporttery': '竞彩官网'}.get(log.get('source', ''), log.get('source', ''))
        task_name = {'matches': '比赛', 'standings': '积分榜', 'results': '结果', 'teams': '球队'}.get(log.get('task_type', ''), log.get('task_type', ''))
        error_msg = log.get('error_message', '')
        error_html = f'<br><small style="color:var(--danger);font-size:12px;">{error_msg}</small>' if error_msg else ''

        logs_rows += f"""
        <tr>
            <td>{source_name}</td>
            <td>{task_name}</td>
            <td>{status_badge}{error_html}</td>
            <td>{log.get('records_count', 0)}</td>
            <td>{log.get('retry_count', 0)}</td>
            <td style="color:var(--text-muted);font-size:13px;">{(log.get('started_at', '') or '')[:16].replace('T', ' ')}</td>
        </tr>"""

    content = f'''
    <div class="page-header">
        <h1 class="page-title">同步日志</h1>
        <p class="page-subtitle">最近 {len(logs)} 条记录</p>
    </div>

    <div class="card">
        <div class="card-body">
            <div class="table-wrapper">
                <table>
                    <thead><tr><th>数据源</th><th>任务</th><th>状态</th><th>记录数</th><th>重试</th><th>时间</th></tr></thead>
                    <tbody>{logs_rows}</tbody>
                </table>
            </div>
        </div>
    </div>
    '''

    return BASE_TEMPLATE.format(
        title="同步日志",
        nav_links=get_nav_links("logs"),
        content=content
    )


@web_router.get("/standings", response_class=HTMLResponse)
async def standings_page(league: str = "PL"):
    """积分榜页面"""
    standings = await fd_repo.get_standings(league)
    league_name = LEAGUE_MAP.get(league, league)

    # 构建积分榜行
    standings_rows = ""
    for s in standings:
        position = s.get('position', 0)
        team_name = s.get('team_name', '')
        played = s.get('played_games', 0)
        won = s.get('won', 0)
        draw = s.get('draw', 0)
        lost = s.get('lost', 0)
        points = s.get('points', 0)
        goals_for = s.get('goals_for', 0)
        goals_against = s.get('goals_against', 0)

        # 排名样式
        if position <= 4:
            pos_class = "position-top"
        elif position <= 6:
            pos_class = "position-europa"
        else:
            pos_class = "position-normal"

        standings_rows += f"""
        <tr>
            <td><span class="position {pos_class}">{position}</span></td>
            <td style="font-weight:500;">{team_name}</td>
            <td>{played}</td>
            <td style="color:var(--text-muted);">{won}/{draw}/{lost}</td>
            <td style="color:var(--text-muted);">{goals_for}:{goals_against}</td>
            <td style="color:var(--text-muted);">{goals_for - goals_against:+d}</td>
            <td><span class="points">{points}</span></td>
        </tr>"""

    # 联赛选项卡
    tabs = ""
    for code, name in LEAGUE_MAP.items():
        active = 'active' if league == code else ''
        tabs += f'<a class="tab {active}" href="/standings?league={code}">{name}</a>'

    content = f'''
    <div class="page-header">
        <h1 class="page-title">积分榜</h1>
        <p class="page-subtitle">{league_name} · 共 {len(standings)} 队</p>
    </div>

    <div class="card">
        <div class="tabs">{tabs}</div>
        <div class="card-body">
            <div class="table-wrapper">
                <table class="standings-table">
                    <thead>
                        <tr><th>排名</th><th>球队</th><th>场次</th><th>胜/平/负</th><th>进球</th><th>净胜</th><th>积分</th></tr>
                    </thead>
                    <tbody>{standings_rows}</tbody>
                </table>
            </div>
        </div>
    </div>
    '''

    return BASE_TEMPLATE.format(
        title="积分榜",
        nav_links=get_nav_links("standings"),
        content=content
    )


@web_router.get("/leagues", response_class=HTMLResponse)
async def leagues_page():
    """联赛列表页面"""
    conn = await fd_repo.get_connection()
    conn.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))
    cursor = await conn.cursor()
    await cursor.execute("SELECT * FROM fd_leagues ORDER BY code")
    leagues = await cursor.fetchall()
    await conn.close()

    leagues_rows = ""
    for league in leagues:
        code = league.get('code', '')
        name = league.get('name', '')
        display_name = LEAGUE_FULL_NAMES.get(code, name)
        country = league.get('country', '')
        season = league.get('current_season', '')

        leagues_rows += f"""
        <tr>
            <td><span class="badge badge-neutral">{code}</span></td>
            <td style="font-weight:500;"><a href="/standings?league={code}">{display_name}</a></td>
            <td>{country or '-'}</td>
            <td>{season or '-'}</td>
            <td><a href="/matches?source=fd&league={code}">查看比赛 →</a></td>
        </tr>"""

    content = f'''
    <div class="page-header">
        <h1 class="page-title">联赛列表</h1>
        <p class="page-subtitle">共 {len(leagues)} 个监控联赛</p>
    </div>

    <div class="card">
        <div class="card-body">
            <div class="table-wrapper">
                <table>
                    <thead><tr><th>代码</th><th>联赛名称</th><th>国家</th><th>赛季</th><th>操作</th></tr></thead>
                    <tbody>{leagues_rows}</tbody>
                </table>
            </div>
        </div>
    </div>
    '''

    return BASE_TEMPLATE.format(
        title="联赛列表",
        nav_links=get_nav_links("leagues"),
        content=content
    )


@web_router.get("/teams", response_class=HTMLResponse)
async def teams_page(league: str = ""):
    """球队列表页面"""
    conn = await fd_repo.get_connection()
    conn.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))
    cursor = await conn.cursor()

    if league:
        await cursor.execute('''
            SELECT DISTINCT t.* FROM fd_teams t
            INNER JOIN fd_matches m ON (m.home_team_id = t.fd_id OR m.away_team_id = t.fd_id)
            WHERE m.league_code = ?
            ORDER BY t.name
        ''', (league,))
    else:
        await cursor.execute("SELECT * FROM fd_teams ORDER BY name")

    teams = await cursor.fetchall()
    await conn.close()

    teams_rows = ""
    for team in teams:
        fd_id = team.get('fd_id', '')
        name = team.get('name', '')
        short_name = team.get('short_name', '')
        venue = team.get('venue', '')

        teams_rows += f"""
        <tr>
            <td style="color:var(--text-muted);font-size:13px;">{fd_id}</td>
            <td style="font-weight:500;">{name}</td>
            <td>{short_name or '-'}</td>
            <td>{venue or '-'}</td>
        </tr>"""

    # 联赛筛选
    tabs = '<a class="tab' + (' active' if not league else '') + '" href="/teams">全部</a>'
    for league_code in settings.monitored_leagues_list:
        active = 'active' if league == league_code else ''
        tabs += f'<a class="tab {active}" href="/teams?league={league_code}">{league_code}</a>'

    content = f'''
    <div class="page-header">
        <h1 class="page-title">球队列表</h1>
        <p class="page-subtitle">共 {len(teams)} 支球队</p>
    </div>

    <div class="card">
        <div class="tabs">{tabs}</div>
        <div class="card-body">
            <div class="table-wrapper">
                <table>
                    <thead><tr><th>ID</th><th>球队名称</th><th>简称</th><th>主场</th></tr></thead>
                    <tbody>{teams_rows}</tbody>
                </table>
            </div>
        </div>
    </div>
    '''

    return BASE_TEMPLATE.format(
        title="球队列表",
        nav_links=get_nav_links("teams"),
        content=content
    )
