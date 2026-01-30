# MatchStats API 调用文档

## 基本信息

| 项目 | 值 |
|------|-----|
| 服务地址 | `http://localhost:9999` |
| API 前缀 | `/api/v1` |
| API 文档 | `http://localhost:9999/docs` (Swagger UI) |
| 数据格式 | JSON |
| 编码 | UTF-8 |

---

## 统一响应格式

所有 API 响应都遵循统一格式：

```json
{
  "success": true,
  "data": { ... },
  "total": 100,
  "error": null,
  "timestamp": "2025-01-28T12:00:00"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| success | boolean | 请求是否成功 |
| data | any | 返回的数据 |
| total | int | 数据总数（分页时使用） |
| error | string | 错误信息（失败时返回） |
| timestamp | string | 响应时间 (ISO 8601) |

---

## API 端点列表

### 1. Football-Data API (欧洲足球数据)

前缀: `/api/v1/fd`

#### 1.1 获取比赛列表

```
GET /api/v1/fd/matches
```

**查询参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| date | string | 否 | 日期 YYYY-MM-DD |
| league | string | 否 | 联赛代码 (PL, BL1, SA, PD, FL1, CL) |
| status | string | 否 | 状态: SCHEDULED/LIVE/FINISHED |
| limit | int | 否 | 返回数量 1-500，默认100 |

**请求示例:**
```bash
# 获取即将进行的比赛
curl "http://localhost:9999/api/v1/fd/matches?status=SCHEDULED&limit=10"

# 获取英超比赛
curl "http://localhost:9999/api/v1/fd/matches?league=PL"

# 获取指定日期比赛
curl "http://localhost:9999/api/v1/fd/matches?date=2025-01-28"
```

**响应示例:**
```json
{
  "success": true,
  "data": [
    {
      "fd_id": 537785,
      "league_code": "PL",
      "home_team_id": 64,
      "away_team_id": 71,
      "home_team_name": "Arsenal FC",
      "away_team_name": "Manchester United FC",
      "match_date": "2025-02-01T15:00:00",
      "status": "SCHEDULED",
      "home_score": null,
      "away_score": null
    }
  ],
  "total": 815,
  "timestamp": "2025-01-28T12:00:00"
}
```

#### 1.2 获取单场比赛

```
GET /api/v1/fd/matches/{match_id}
```

**路径参数:**
- `match_id`: 比赛 ID (整数)

**请求示例:**
```bash
curl "http://localhost:9999/api/v1/fd/matches/537785"
```

#### 1.3 获取联赛列表

```
GET /api/v1/fd/leagues
```

**请求示例:**
```bash
curl "http://localhost:9999/api/v1/fd/leagues"
```

**响应示例:**
```json
{
  "success": true,
  "data": [
    {
      "code": "PL",
      "name": "Premier League",
      "country": "England",
      "current_season": 2024
    },
    {
      "code": "BL1",
      "name": "Bundesliga",
      "country": "Germany",
      "current_season": 2024
    }
  ],
  "total": 13
}
```

#### 1.4 获取积分榜

```
GET /api/v1/fd/leagues/{code}/standings
```

**路径参数:**
- `code`: 联赛代码

**查询参数:**
- `season`: 赛季 (可选)

**请求示例:**
```bash
curl "http://localhost:9999/api/v1/fd/leagues/PL/standings"
curl "http://localhost:9999/api/v1/fd/leagues/PL/standings?season=2024"
```

**响应示例:**
```json
{
  "success": true,
  "data": [
    {
      "league_code": "PL",
      "team_id": 64,
      "team_name": "Arsenal FC",
      "position": 1,
      "played_games": 22,
      "won": 15,
      "draw": 4,
      "lost": 3,
      "points": 49,
      "goals_for": 45,
      "goals_against": 18,
      "goal_diff": 27
    }
  ],
  "total": 20
}
```

#### 1.5 获取球队列表

```
GET /api/v1/fd/teams
```

**查询参数:**
- `league`: 联赛代码 (可选，筛选该联赛的球队)

**请求示例:**
```bash
# 获取所有球队
curl "http://localhost:9999/api/v1/fd/teams"

# 获取英超球队
curl "http://localhost:9999/api/v1/fd/teams?league=PL"
```

---

### 2. 竞彩 API

前缀: `/api/v1/sporttery`

#### 2.1 获取竞彩比赛列表

```
GET /api/v1/sporttery/matches
```

**查询参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| date | string | 否 | 日期 YYYY-MM-DD |
| status | string | 否 | 状态: pending/finished |
| limit | int | 否 | 返回数量 1-500，默认100 |

**请求示例:**
```bash
curl "http://localhost:9999/api/v1/sporttery/matches"
curl "http://localhost:9999/api/v1/sporttery/matches?status=pending"
```

**响应示例:**
```json
{
  "success": true,
  "data": [
    {
      "match_code": "20250128001",
      "group_date": "2025-01-28",
      "home_team": "阿森纳",
      "away_team": "曼联",
      "league": "英超",
      "match_time": "20:30",
      "status": "pending",
      "actual_score": null,
      "half_score": null
    }
  ],
  "total": 46
}
```

#### 2.2 获取单场竞彩比赛

```
GET /api/v1/sporttery/matches/{match_code}
```

---

### 3. 系统 API

前缀: `/api/v1`

#### 3.1 健康检查

```
GET /api/v1/health
```

**响应示例:**
```json
{
  "status": "ok",
  "timestamp": "2025-01-28T12:00:00"
}
```

#### 3.2 获取统计信息

```
GET /api/v1/stats
```

**响应示例:**
```json
{
  "fd_matches": 1941,
  "sporttery_matches": 46,
  "last_sync": "2025-01-28T19:30:00",
  "sync_status": "ok"
}
```

#### 3.3 获取同步日志

```
GET /api/v1/logs
```

**查询参数:**
- `source`: 数据源 (fd/sporttery)
- `limit`: 返回数量 1-200，默认50

---

## 联赛代码对照表

| 代码 | 联赛名称 | 国家 |
|------|---------|------|
| PL | Premier League | 英格兰 |
| BL1 | Bundesliga | 德国 |
| SA | Serie A | 意大利 |
| PD | La Liga | 西班牙 |
| FL1 | Ligue 1 | 法国 |
| CL | Champions League | 欧洲 |

---

## Python 调用示例

```python
import requests

BASE_URL = "http://localhost:9999/api/v1"

# 获取即将进行的比赛
def get_scheduled_matches():
    response = requests.get(f"{BASE_URL}/fd/matches", params={
        "status": "SCHEDULED",
        "limit": 10
    })
    return response.json()

# 获取积分榜
def get_standings(league_code="PL"):
    response = requests.get(f"{BASE_URL}/fd/leagues/{league_code}/standings")
    return response.json()

# 获取竞彩比赛
def get_sporttery_matches():
    response = requests.get(f"{BASE_URL}/sporttery/matches")
    return response.json()

# 使用示例
if __name__ == "__main__":
    matches = get_scheduled_matches()
    print(f"即将进行的比赛: {matches['total']} 场")

    for match in matches['data']:
        print(f"{match['home_team_name']} vs {match['away_team_name']}")
```

---

## JavaScript/Node.js 调用示例

```javascript
const BASE_URL = 'http://localhost:9999/api/v1';

// 获取即将进行的比赛
async function getScheduledMatches() {
  const response = await fetch(`${BASE_URL}/fd/matches?status=SCHEDULED&limit=10`);
  return await response.json();
}

// 获取积分榜
async function getStandings(leagueCode = 'PL') {
  const response = await fetch(`${BASE_URL}/fd/leagues/${leagueCode}/standings`);
  return await response.json();
}

// 使用示例
(async () => {
  const matches = await getScheduledMatches();
  console.log(`即将进行的比赛: ${matches.total} 场`);

  matches.data.forEach(match => {
    console.log(`${match.home_team_name} vs ${match.away_team_name}`);
  });
})();
```

---

## 注意事项

### 1. 数据更新频率

| 数据类型 | 更新频率 | 说明 |
|---------|---------|------|
| 赛程 (SCHEDULED) | 1天 | 完整赛季赛程，很少变化 |
| 比赛结果 (FINISHED) | 5分钟 | 获取最新比分 |
| 积分榜 | 1小时 | 比赛后更新 |
| 射手榜 | 6小时 | 进球统计 |
| 球队详情 | 1天 | 教练、阵容 |
| 比赛详情 | 5分钟 | 进行中比赛 |

### 2. 数据状态说明

比赛状态 (status):
- `SCHEDULED` - 未开始
- `IN_PLAY` - 进行中
- `PAUSED` - 中断
- `FINISHED` - 已结束
- `POSTPONED` - 延期
- `CANCELED` - 取消
- `AWARDED` - 流赛/判罚

### 3. 限流说明

- 服务本身无限流，可随意调用
- 数据源同步受 Football-Data.org 限制 (10次/分钟)
- 建议客户端实现缓存，避免重复请求

### 4. 时区说明

- 所有时间使用 UTC 格式 (ISO 8601)
- 中国时区需 +8 小时

### 5. 错误处理

当 `success=false` 时，检查 `error` 字段：

```json
{
  "success": false,
  "data": null,
  "error": "比赛不存在",
  "timestamp": "2025-01-28T12:00:00"
}
```

---

## 更新日志

| 日期 | 版本 | 变更 |
|------|------|------|
| 2025-01-28 | v1.0 | 初始版本，支持所有基础API |
