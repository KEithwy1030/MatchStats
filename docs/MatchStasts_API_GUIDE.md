# MatchStats 足球数据商业 API 指南 (Commercial API Guide)

欢迎使用 MatchStats 足球数据中心。本平台提供实时更新的全球顶级足球赛事数据，旨在为 AI Agent、专业分析工具及博彩预测模型提供稳定的底层支撑。

**当前服务状态**：`PROD (v0.1.0)`
**主页地址**：[https://kmatch-stats.vercel.app/](https://kmatch-stats.vercel.app/)

---

## 1. 访问策略 (Access Policy)

为了保障数据资产安全及系统稳定性，MatchStats 采用“**前台公开，接口鉴权**”的保护策略：

*   **HTML 页面**：完全公开。欢迎搜索引擎爬虫及普通用户访问进行数据预览。
*   **JSON 接口 (API)**：**受限访问**。所有以 `/api/` 开头的底层数据接口均需通过身份验证。未经授权的直接请求将返回 `401 Unauthorized` 错误。

---

## 2. 身份验证 (Authentication)

商业用户需在 HTTP 请求头 (Header) 中携带唯一的 API 密钥才能成功获取数据。

*   **Header 名称**：`X-API-KEY`
*   **默认演示密钥**：`matchstats_secret_2026` *(注：正式商用版本将为每个用户分配独立密钥)*

### 调用示例 (cURL):
```bash
curl -X GET "https://kmatch-stats.vercel.app/api/matches/today" \
     -H "X-API-KEY: matchstats_secret_2026"
```

---

## 3. 核心 API 接口清单

| 功能 | 请求路径 | 关键参数 | 数据说明 |
| :--- | :--- | :--- | :--- |
| **实时比分** | `/api/matches/today` | 无 | 获取今日所有比赛的动态比分、红黄牌及状态。 |
| **赛果快报** | `/api/matches/recent` | `days`: 天数 (1-7) | 获取过去几天的历史比分，用于模型复盘。 |
| **顶级积分榜**| `/api/standings/{code}` | `PL`(英超), `BL1`(德甲)等 | 包含胜平负、净胜球、总排名。 |
| **金靴数据** | `/api/scorers/{code}` | 联赛代码 | 球员进球、点球、助攻统计。 |
| **竞彩深度数据**| `/api/sporttery/matches`| 无 | 包含官方对阵编号及中文本化队名。 |

---

## 4. 开发者代码示例

### Python (使用 httpx)
```python
import httpx

API_URL = "https://kmatch-stats.vercel.app/api/matches/today"
HEADERS = {"X-API-KEY": "matchstats_secret_2026"}

def fetch_live_data():
    with httpx.Client() as client:
        response = client.get(API_URL, headers=HEADERS)
        if response.status_code == 200:
            return response.json()
        print(f"Error: {response.status_code} - {response.text}")

# 运行获取
data = fetch_live_data()
```

---

## 5. 数据库底层架构 (内部参考)

MatchStats 采用 **Supabase (PostgreSQL)** 云端数据库支撑千万级数据存储。

*   **存储位置**：South Asia (Singapore)
*   **同步频率**：
    *   **比分数据**：每 20 分钟同步一次 (Fast Sync)
    *   **元数据**：每 12 小时全量同步一次 (Full Sync)
*   **字段类型**：严格的 JSONB 格式，支持全文检索及复杂逻辑分析。

---

## 6. 商用合作与 Key 申请

如果您希望将 MatchStats 数据集成到您的生产环境，或需要更高的请求频率限额，请通过以下方式联系管理员：

1.  **提交申请**：在 [GitHub Issues](https://github.com/KEithwy1030/MatchStats/issues) 提交 Key 申请。
2.  **获取专属授权**：我们将为您生成独立的专属 Key，并提供流量监控面板。

---

*© 2026 MatchStats Team. All Rights Reserved.*
