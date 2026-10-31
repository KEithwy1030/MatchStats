# MatchStats API 文档

> Base URL（生产推荐）：`https://kmatch-stats.vercel.app`
> Base URL（分支预览）：`https://match-stats-git-main-keithwys-projects.vercel.app`
> Base URL（生产别名）：`https://match-stats-keithwys-projects.vercel.app`
> 本地开发：`http://localhost:8000`（见 README）

> [!NOTE]
> 若访问 `https://match-stats-keithwys-projects.vercel.app` 遇到 Vercel 历史 Instant Rollback 导致的未自动滚动现象，管理员在 Vercel 控制台该项目主页点击 "Undo Rollback" 或对最新 Deployment 点击 "Promote to Production" 即可同步生效；同时全站数据与看板在 `https://kmatch-stats.vercel.app/dashboard` 及分支预览域名均保持实时高可用运行。

## 认证

- 公开接口（如 `/api/v1/health`）无需认证。
- 数据接口需要在请求头中携带 API Key：
  `X-API-Key: YOUR_API_KEY`
- 生产环境 API 为**只读策略**：只允许 `GET` 请求；非公开路径需要管理员 Key 或可信来源（Referer/Origin 为本站域名）。

API Key 获取：📧 KEithWYong@Gmail.com，或 TG 群 https://t.me/oldkclub 私聊群主。

## 接口

### 系统

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | `/api/v1/health` | 健康检查 | 公开 |

### Football-Data（欧洲联赛）

前缀：`/api/v1/fd`

欧洲主流联赛（英超、西甲、意甲、德甲、法甲、欧冠等）的比分、赛程、积分榜、射手榜。数据约每 20 分钟自动更新。

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/fd/matches` | 比赛列表 |
| GET | `/api/v1/fd/matches/{match_id}` | 单场比赛 |
| GET | `/api/v1/fd/matches/{match_id}/details` | 比赛详情 |
| GET | `/api/v1/fd/leagues` | 联赛列表 |
| GET | `/api/v1/fd/leagues/{code}/standings` | 积分榜 |
| GET | `/api/v1/fd/leagues/{code}/scorers` | 射手榜 |
| GET | `/api/v1/fd/teams` | 球队列表 |

### 中国竞彩

前缀：`/api/v1/sporttery`

竞彩官方比赛编号、赔率、中文队名。

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/sporttery/matches` | 竞彩比赛列表 |
| GET | `/api/v1/sporttery/matches/{match_code}` | 单场竞彩比赛 |

### Web 页面

| 路径 | 说明 |
|------|------|
| `/` | to B 落地页（本站） |
| `/app/static/index.html` | 实时数据看板（演示） |
| `/predictions` | Grok 比赛深度预测列表 |

## 调用示例

```bash
# 健康检查（公开）
curl https://match-stats-keithwys-projects.vercel.app/api/v1/health

# 授权接口（需 API Key）
curl -H "X-API-Key: YOUR_API_KEY" \
  https://match-stats-keithwys-projects.vercel.app/api/v1/fd/matches
```

## 开源说明

MatchStats 遵循 Open Core 模式：核心代码完全开源（见本仓库），生产环境数据 API 仅对授权用户开放。
