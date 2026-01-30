# MatchStats - 比赛数据API服务

为 Agent 提供实时比赛数据的统一服务。

## 功能

- 数据抓取：Football-Data.org + 竞彩官网（分开存储）
- API 查询：只读，支持按日期/球队/联赛查询
- 定时更新：自动后台同步
- Web 管理界面：比赛列表、数据统计、日志查看

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python -m app.main

# 访问
# API 文档: http://localhost:9999/docs
# Web 界面: http://localhost:9999/
```

## 端口

9999
