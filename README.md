# MatchStats Core: Enterprise-Grade Football Data Infrastructure
<!-- Trigger Vercel Deploy: v1.1.0 - AI Intelligence & Robustness Fix -->

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-High%20Performance-green.svg)
![Supabase](https://img.shields.io/badge/Database-Supabase%20(PostgreSQL)-emerald.svg)
![Grok AI](https://img.shields.io/badge/Intelligence-Grok--1-purple.svg)
![Status](https://img.shields.io/badge/Status-Production-orange.svg)

> **为 AI Agent 与专业预测模型设计的实时足球数据中台。**
> *Real-time Football Intelligence Pipeline for Developers & Analysts.*

---

## 🚀 项目简介 (Introduction)

MatchStats 是一套高可用的分布式足球数据采集与分发系统。不同于传统的单源爬虫，MatchStats 创新性地实现了 **混合数据源聚合 (Hybrid Data Aggregation)**，将全球竞技数据与本地化竞彩情报深度融合，并集成了基于 Grok 的 **AI 专家智能分析层**。

**核心使命**：为 AI 模型和专业分析工具提供清洗过的、具备深度情报价值的结构化足球数据。

---

## 💎 核心价值 (Why MatchStats?)

### 1. 🧠 AI 专家智能情报 (AI Intelligence)
集成了 **Grok-1** 深度搜索能力，每个比赛日自动生成高保真情报：
*   **深层数据挖掘**：自动检索 X (Twitter) 验证记者、地方媒体及球队官方训练动态。
*   **多维度分析**：涵盖伤停情报、主客物流、天气影响、裁判倾向及机构（Bet365/Pinnacle）赔率异动。
*   **Chinese-First Output**：情报自动翻译并结构化，完美适配中文应用场景。

### 2. ⚡ 准实时同步 (Low Latency Score Sync)
*   **赛程采集**：自动同步最新竞彩赛程。
*   **比分回溯**：特有的补账机制，自动回溯过去 3 天的所有比赛，确保比分（全场/半场）零遗漏。
*   **自动化自愈**：后端 API 具备强大的数据校验与容错能力，屏蔽任何数据库脏数据对前端的影响。

### 3. 🛡️ 独家数据聚合 (Data Aggregation)
*   **源 A (Football-Data)**：提供首发阵容、历史战绩、专业竞技统计。
*   **源 B (Sporttery/China)**：集成中国竞彩官方编号、赔率指数及精准中文队名映射。

### 4. 🗄️ 永久云端存储 (Supabase Cloud)
依托 **Supabase (PostgreSQL)**，实现数据资产化，历史赛季数据永久可查，不依赖单次抓取。

---

## 🏗️ 技术架构 (Architecture)

*   **Ingestion Layer**: Playwright/CDP 自动化抓取集群（Grok 专家模式）
*   **Sync Logic**: 增强型 `sync_sporttery_now` 异步补账系统
*   **Storage Layer**: Supabase Enterprise (PostgreSQL)
*   **API Layer**: FastAPI 高性能网关（带 API Key 权限控制）

---

## �️ 管理与维护 (Management)

项目脚本已精简至生产级状态：
*   `scripts/sync_sporttery_now.py`: 同步赛程与所有缺失比分。
*   `scripts/grok_automated_runner.py`: 启动 AI 专家情报采集任务。
*   `scripts/inspect_sporttery_data.py`: 数据覆盖率与完整性审计。
*   `scripts/generate_review_md.py`: 导出今日深度情报报告。

---

## 🔌 API 接入与商用 (Access & Pricing)

MatchStats 遵循 **“Open Core”** 模式：核心代码完全开源；生产环境数据 API 仅对授权用户开放。

📘 **查看 API 文档**: [docs/API.md](./docs/API.md)

📧 **商务联络**: [KEithWYong@Gmail.com](mailto:KEithWYong@Gmail.com)

---

## ❤️ Support the Developer

如果本项目为您节省了开发时间或提供了灵感，欢迎支持作者维护服务器。

<div align="center">
  <table>
    <tr>
      <td align="center" width="200">
        <img src="./docs/images/alipay_qr.jpg" alt="Alipay Support" width="180" />
        <br/>
        <b>☕ Support (Alipay)</b>
      </td>
      <td align="center" width="200">
        <img src="./docs/images/wechat_friend_qr.png" alt="Business Contact" width="180" />
        <br/>
        <b>🤝 Business (WeChat)</b>
      </td>
    </tr>
  </table>
</div>

