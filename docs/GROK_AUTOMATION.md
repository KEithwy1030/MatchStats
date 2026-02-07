# Grok 自动化预测配置指南

## 🎯 功能说明

使用 Playwright 浏览器自动化工具：
1. 自动访问 Grok.com
2. 发送比赛预测提示词
3. 获取 Grok AI 的预测结果
4. 保存到 Supabase 数据库
5. 前端展示预测数据

---

## ⚙️ 环境要求

### 必须条件
- ✅ **本地电脑**（必须有图形界面）
- ✅ **Windows/Mac/Linux** 都可以
- ✅ **稳定的网络连接**
- ✅ **X/Twitter 账号**（用于登录 Grok）

### 不支持的环境
- ❌ Vercel（服务器无图形界面）
- ❌ GitHub Actions（无浏览器）
- ❌ Docker 容器（需要特殊配置）

---

## 📦 安装步骤

### 1. 安装 Playwright

```bash
# 进入项目目录
cd E:\CursorData\MatchStats

# 激活虚拟环境
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# 安装 Playwright
pip install playwright

# 安装浏览器驱动
playwright install chromium
```

### 2. 创建数据库表

**方法 1：使用 Supabase MCP**
```
（已经自动创建）
```

**方法 2：手动执行 SQL**
1. 打开 Supabase Dashboard
2. 进入 SQL Editor
3. 执行 `supabase/migrations/20260203_create_match_predictions.sql`

---

## 🚀 使用方法

### 第一次使用（需要登录）

```bash
# 运行脚本
python scripts/grok_predictor.py
```

**流程**：
1. 浏览器自动打开
2. 访问 grok.com
3. 提示需要登录
4. **手动完成登录**
5. 登录成功后，按回车键继续
6. 自动开始预测

### 后续使用（Session 已保存）

```bash
# 直接运行，无需重新登录
python scripts/grok_predictor.py
```

---

## ⚙️ 配置选项

### 修改 `scripts/grok_predictor.py`

```python
# 显示浏览器窗口（调试用）
HEADLESS = False  # True = 无头模式（不可见）

# 预测未来的比赛
days_ahead = 1  # 明天的比赛（可改为 2, 3...）

# 每次预测的比赛数量
limit = 3  # 前 3 场（可改为更多）
```

---

## 📋 提示词模板

当前提示词包含：

```python
prompt = f"""你是专业的足球预测分析专家。请分析以下比赛并给出预测：

比赛信息：
- 联赛：{league}
- 主队：{home_team}
- 客队：{away_team}
- 比赛时间：{match_date}

请给出以下预测：
1. 比赛胜平负预测（主胜/平局/客胜）
2. 预测比分
3. 置信度（0-100%）
4. 简要分析理由（2-3 句话）

请以 JSON 格式返回：
{{
    "predicted_winner": "主胜/平局/客胜",
    "predicted_score": "2-1",
    "confidence": 75,
    "reasoning": "分析理由"
}}
"""
```

**自定义提示词**：
- 修改 `build_prompt()` 方法
- 添加更多上下文（历史战绩、伤病情况等）
- 调整输出格式

---

## 🗄️ 数据库结构

```sql
match_predictions
├── match_id          -- 比赛 ID
├── prediction_date   -- 预测时间
├── home_team         -- 主队
├── away_team         -- 客队
├── league            -- 联赛
├── match_date        -- 比赛时间
├── predicted_winner  -- 预测胜者（主胜/平局/客胜）
├── predicted_score   -- 预测比分
├── confidence        -- 置信度（0-100）
├── reasoning         -- AI 推理过程
├── raw_response      -- Grok 完整响应
├── ai_model          -- AI 模型（Grok）
├── actual_winner     -- 实际胜者（赛后填写）
├── actual_score      -- 实际比分（赛后填写）
└── is_correct        -- 预测是否正确
```

---

## ⚠️ 注意事项

### 1. 登录 Session

- Session 保存在 `data/grok_session.json`
- 有效期取决于 X/Twitter（通常 7-30 天）
- 过期后需要重新登录

### 2. 请求频率

- Grok 可能有频率限制
- 建议每场间隔 10-15 秒
- 每次最多预测 10 场比赛

### 3. 资源占用

- 浏览器内存：约 300-500MB
- CPU：中等
- 网络：取决于响应长度

### 4. 稳定性

- ⚠️ Grok 网页结构变化会导致脚本失效
- ⚠️ 需要定期维护和更新选择器
- ⚠️ 网络问题可能导致失败

---

## 🔧 故障排除

### 问题 1：无法找到输入框

**原因**：Grok 更新了 UI

**解决**：
1. 打开 `grok_predictor.py`
2. 找到 `send_prompt()` 方法
3. 更新选择器：
   ```python
   # 尝试不同的选择器
   textarea = await page.query_selector('新的选择器')
   ```

### 问题 2：无法提取响应

**原因**：响应结构变化

**解决**：
1. 查看响应的 HTML 结构
2. 更新选择器：
   ```python
   response_elements = await page.query_selector_all('新的选择器')
   ```

### 问题 3：Session 过期

**解决**：
```bash
# 删除旧的 session
rm data/grok_session.json

# 重新运行脚本
python scripts/grok_predictor.py
```

### 问题 4：Playwright 未安装

```bash
# 重新安装
pip install --force-reinstall playwright
playwright install --force chromium
```

---

## 🔄 定时任务配置

### Windows 计划任务

**创建启动任务**：
1. 打开任务计划程序
2. 创建基本任务
3. 触发器：**当计算机启动时**
4. 延迟：**10 分钟**
5. 操作：
   ```
   程序：E:\CursorData\MatchStats\venv\Scripts\pythonw.exe
   参数：scripts\grok_predictor.py
   起始于：E:\CursorData\MatchStats
   ```

### Cron 任务（Mac/Linux）

```bash
# 编辑 crontab
crontab -e

# 添加任务（每天凌晨 2 点运行）
0 2 * * * cd /path/to/MatchStats && /usr/bin/python3 scripts/grok_predictor.py
```

---

## 📊 预测准确性追踪

### 查看预测历史

```python
# 查询 Supabase
SELECT
    home_team,
    away_team,
    predicted_winner,
    actual_winner,
    is_correct,
    confidence
FROM match_predictions
WHERE actual_winner IS NOT NULL
ORDER BY prediction_date DESC;
```

### 计算准确率

```python
# 总体准确率
SELECT
    COUNT(*) FILTER (WHERE is_correct = TRUE) * 100.0 / COUNT(*) as accuracy
FROM match_predictions
WHERE actual_winner IS NOT NULL;

# 按置信度分组
SELECT
    CASE
        WHEN confidence >= 80 THEN '高'
        WHEN confidence >= 60 THEN '中'
        ELSE '低'
    END as confidence_level,
    COUNT(*) FILTER (WHERE is_correct = TRUE) * 100.0 / COUNT(*) as accuracy
FROM match_predictions
WHERE actual_winner IS NOT NULL
GROUP BY confidence_level;
```

---

## 🎨 前端展示（待开发）

### API 端点

```python
# 获取比赛预测
GET /api/v1/predictions/{match_id}

# 获取所有预测
GET /api/v1/predictions?league=PL&date=2026-02-04

# 获取预测统计
GET /api/v1/predictions/stats?accuracy=true
```

### UI 示例

```
┌────────────────────────────────────────┐
│       阿森纳 vs 切尔西                 │
│       2026-02-04 20:00                 │
├────────────────────────────────────────┤
│  🤖 Grok 预测                          │
│  ─────────────────────                 │
│  预测结果：阿森纳胜                     │
│  预测比分：2-1                         │
│  置信度：75%                           │
│                                        │
│  分析理由：                             │
│  阿森纳主场近 5 场 4 胜 1 平，           │
│  切尔西主力中场坎特缺阵，               │
│  历史对战阿森纳略占优势。               │
│                                        │
│  预测时间：2 小时前                     │
└────────────────────────────────────────┘
```

---

## 📝 开发计划

### Phase 1：基础功能 ✅
- [x] 浏览器自动化
- [x] Grok 登录
- [x] 发送提示词
- [x] 获取响应
- [x] 保存到数据库

### Phase 2：优化
- [ ] 增强提示词（更多上下文）
- [ ] 处理更多比赛
- [ ] 错误重试机制
- [ ] 日志记录

### Phase 3：前端
- [ ] API 端点
- [ ] 前端展示
- [ ] 预测历史
- [ ] 准确率统计

### Phase 4：自动化
- [ ] 定时任务
- [ ] 预测结果验证
- [ ] 自动更新 actual_winner

---

## 🆘 需要帮助？

遇到问题？检查：
1. Playwright 是否正确安装
2. 浏览器驱动是否安装
3. X/Twitter 账号是否有效
4. 网络连接是否稳定

---

**开始使用**：
```bash
cd E:\CursorData\MatchStats
python scripts/grok_predictor.py
```
