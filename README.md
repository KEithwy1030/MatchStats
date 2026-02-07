# MatchStats Core: Enterprise-Grade Football Data Infrastructure
<!-- Trigger Vercel Deploy: v1.0.4 - Fix Supabase Client -->

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-High%20Performance-green.svg)
![Supabase](https://img.shields.io/badge/Database-Supabase%20(PostgreSQL)-emerald.svg)
![Status](https://img.shields.io/badge/Status-Production-orange.svg)

> **为 AI Agent 与专业预测模型设计的实时足球数据中台。**
> *Real-time Football Intelligence Pipeline for Developers & Analysts.*

---

## 🚀 项目简介 (Introduction)

MatchStats 是一套高可用的分布式足球数据采集与分发系统。不同于传统的单源爬虫，MatchStats 创新性地实现了 **混合数据源聚合 (Hybrid Data Aggregation)**，将欧洲官方数据与本地化竞彩数据完美融合，通过 Serverless 架构实现毫秒级查询响应。

**核心使命**：为下游商业应用（预测模型、分析工具、即时比分 App）提供清洗过的、结构化的、永久存储的干净数据。

---

## 💎 核心价值 (Why MatchStats?)

### 1. ⚡ 准实时同步 (5-Min Low Latency)
基于分布式调度系统，实现对全球正在进行的比赛进行 **5 分钟/次** 的高频轮询。告别传统免费接口 1-2 小时的延迟，让您的模型能捕捉到瞬息万变的赛场动态。

### 2. 🛡️ 独家双源聚合 (Dual-Source Aggregation)
我们解决了单一数据源信息匮乏的痛点：
*   **源 A (Football-Data)**：提供首发阵容、红黄牌、进球时间等专业竞技数据。
*   **源 B (Sporttery/China)**：独家集成了**中国竞彩官方**的赔率指数、赛事编号及中文译名。
*   **结果**：您调用一次 API，即可获得一份“中西合璧”的完整数据包。

### 3. 🧠 AI-Ready Data Structure
所有数据入库前均经过严格清洗（ETL），字段定义清晰，完全符合 OpenAI/Grok 等大模型的输入规范。
*   JSON 结构扁平化，无冗余嵌套。
*   自动关联球队 ID，解决不同数据源“队名不一致”的难题。

### 4. 🗄️ 永久云端存储 (Permanent Storage)
依托 **Supabase (PostgreSQL)** 云数据库，不仅记录当下，更完整保留历史赛季数据。您的数据资产不会因为第三方 API 变动而丢失。

---

## 🏗️ 技术架构 (Architecture)

本系统采用 **Serverless + Edge** 架构，确保 99.9% 的可用性。

*   **Ingestion Layer (采集层)**: GitHub Actions 分布式节点集群
    *   `Live Sync`: 5分钟/次 (高频比分流)
    *   `Meta Sync`: 12小时/次 (积分榜/球员库)
*   **Storage Layer (存储层)**: Supabase Enterprise
*   **Access Layer (接入层)**: Vercel Edge Network + FastAPI 安全网关

---

## 🔌 API 接入与商用 (Access & Pricing)

MatchStats 遵循 **“Open Core”** 模式：核心代码完全开源，旨在促进行业技术交流；但生产环境的高频数据 API 接口仅对授权用户开放。

### 接口鉴权机制
为了保障服务质量（QoS），所有 API 调用均需在 Header 中携带密钥：
```bash
curl -H "X-API-KEY: YOUR_SECRET_KEY" ...
```

### 商业合作
如果您需要将 MatchStats 数据集成到您的商业产品中，或需要定制更高频率的数据推送服务，请联系我们获取 **Enterprise Key**。

📧 **商务联络**: [KEithWYong@Gmail.com](mailto:KEithWYong@Gmail.com)

---


## 🛠️ 本地部署 (For Developers)

如果您希望学习或自行部署本系统进行研究，请参考以下步骤：

```bash
# 1. 克隆仓库
git clone https://github.com/your-repo/matchstats.git

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置 .env 环境变量
# 需要自行申请 Supabase 和 Football-Data API Token
```

---

## 📖 API 快速开始 (Quick Start)

### 生产环境 (Production)

**服务地址**: `https://kmatch-stats.vercel.app`

**快速测试** (3分钟上手):

```bash
# 1. 获取今日中文比赛数据
curl -X GET "https://kmatch-stats.vercel.app/api/v1/fd/matches?lang=zh&limit=5" \
     -H "X-API-KEY: mk_live_2024_secure_key_xyz123"

# 2. 获取英超积分榜（英文）
curl -X GET "https://kmatch-stats.vercel.app/api/v1/fd/leagues/PL/standings?lang=en" \
     -H "X-API-KEY: mk_live_2024_secure_key_xyz123"

# 3. 获取射手榜（中文）
curl -X GET "https://kmatch-stats.vercel.app/api/v1/fd/leagues/PL/scorers?lang=zh" \
     -H "X-API-KEY: mk_live_2024_secure_key_xyz123"
```

### 多语言支持

所有主要 API 端点现已支持中英文切换：

| 端点 | 功能 | 多语言 |
|------|------|--------|
| `/api/v1/fd/matches` | 比赛列表 | ✅ |
| `/api/v1/fd/leagues/{code}/standings` | 积分榜 | ✅ |
| `/api/v1/fd/leagues/{code}/scorers` | 射手榜 | ✅ |

**使用方法**: 添加 `lang` 查询参数
- `lang=en` → 英文（默认）
- `lang=zh` → 中文

### 完整文档

📘 **查看完整 API 文档**: [docs/API.md](./docs/API.md)
- 包含所有 API 参数说明
- Python/JavaScript 代码示例
- FAQ、时区处理、错误处理

---

## ❤️ Support the Developer

如果 MatchStats 的源码或架构设计为您节省了开发时间，或者启发了您的灵感，欢迎请作者喝杯咖啡 ☕️

If this project helps you, consider buying me a coffee to keep the server running!

<div align="center">
<div align="center">
  <table>
    <tr>
      <td align="center" width="200">
        <!-- 请确保 alipay_qr.jpg 已放入 docs/images 目录 -->
        <img src="./docs/images/alipay_qr.jpg" alt="Alipay Support" width="180" />
        <br/>
        <b>☕ Support (Alipay)</b><br/>
        <small>请作者喝杯咖啡</small>
      </td>
      <td align="center" width="200">
        <!-- 请确保 wechat_friend_qr.png 已放入 docs/images 目录 -->
        <img src="./docs/images/wechat_friend_qr.png" alt="Business Contact" width="180" />
        <br/>
        <b>🤝 Business (WeChat)</b><br/>
        <small>添加好友 (备注: API)</small>
      </td>
    </tr>
  </table>
  
  <br/>
</div>

