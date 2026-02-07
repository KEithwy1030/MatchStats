# Grok 自动化预测 - 快速开始

## 🚀 5 分钟快速配置

### 步骤 1：安装依赖（2 分钟）

```bash
cd E:\CursorData\MatchStats
venv\Scripts\activate
pip install playwright
playwright install chromium
```

### 步骤 2：创建数据库表（1 分钟）

**自动执行**（推荐）：
```bash
# Supabase MCP 已自动创建表
```

**手动执行**（备选）：
1. 打开 Supabase Dashboard
2. SQL Editor
3. 执行 `supabase/migrations/20260203_create_match_predictions.sql`

### 步骤 3：测试环境（30 秒）

```bash
# 双击运行
scripts\test_grok_env.bat

# 或命令行
python scripts/test_grok_setup.py
```

### 步骤 4：首次运行（2 分钟）

```bash
python scripts/grok_predictor.py
```

**首次运行流程**：
1. 浏览器自动打开
2. 访问 grok.com
3. **手动登录** X/Twitter 账号
4. 登录成功后，按回车继续
5. 自动预测前 3 场比赛
6. 保存到数据库

---

## 📋 完整工作流程

```
┌─────────────────────┐
│  1. 运行脚本         │
│  python grok_       │
│  predictor.py       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  2. 启动浏览器       │
│  (Chromium)         │
│  自动访问 grok.com  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  3. 检查登录         │
│  - 已登录？继续      │
│  - 未登录？等待手动  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  4. 获取比赛         │
│  从 Supabase 读取    │
│  未来 1 天的比赛     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  5. 逐场预测         │
│  - 构建提示词        │
│  - 发送到 Grok      │
│  - 等待响应 (15s)    │
│  - 提取结果         │
│  - 保存到数据库      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  6. 完成            │
│  关闭浏览器          │
│  显示统计信息        │
└─────────────────────┘
```

---

## ⚙️ 配置选项

### 修改预测范围

**文件**：`scripts/grok_predictor.py`

```python
# 第 20 行附近
async def get_upcoming_matches(self, days_ahead: int = 1):
    # days_ahead = 1  # 明天
    # days_ahead = 2  # 后天
    # days_ahead = 3  # 未来 3 天
```

```python
# 第 180 行附近
for i, match in enumerate(matches[:3], 1):
    # [:3]  = 预测前 3 场
    # [:5]  = 预测前 5 场
    # [:10] = 预测前 10 场
```

### 修改提示词

**文件**：`scripts/grok_predictor.py`

```python
# 第 50 行
def build_prompt(self, match: Dict) -> str:
    # 自定义你的提示词
    prompt = f"""..."""
    return prompt
```

---

## 🎯 使用场景

### 场景 1：手动预测（测试）

```bash
# 随时运行
python scripts/grok_predictor.py
```

### 场景 2：定时预测（每天）

**Windows 任务计划**：
```cmd
schtasks /create /tn "MatchStats Grok预测" /tr "E:\CursorData\MatchStats\venv\Scripts\pythonw.exe scripts\grok_predictor.py" /sc daily /st 02:00 /ru "SYSTEM"
```

**每天凌晨 2 点自动运行**

---

## 📊 查看预测结果

### 方法 1：查询数据库

```sql
SELECT
    home_team,
    away_team,
    predicted_winner,
    predicted_score,
    confidence,
    prediction_date
FROM match_predictions
ORDER BY prediction_date DESC
LIMIT 10;
```

### 方法 2：访问网站（待开发）

```
https://kmatch-stats.vercel.app/predictions
（功能开发中）
```

---

## ⚠️ 重要提示

### 1. 必须本地运行
- ✅ 可以在电脑上运行
- ❌ 不能在 Vercel/GitHub Actions 运行（需要图形界面）

### 2. Session 有效期
- 保存在 `data/grok_session.json`
- 通常 7-30 天有效
- 过期后重新登录

### 3. 网络要求
- 需要能访问 grok.com
- 稳定的网络连接
- 建议在网络良好时运行

### 4. 资源占用
- 内存：300-500MB
- 时间：每场约 20-30 秒
- 10 场比赛约 5-10 分钟

---

## 🔧 故障排除

### 问题：Playwright 未安装

```bash
pip install playwright
playwright install chromium
```

### 问题：浏览器驱动失败

```bash
# 重新安装
playwright install --force chromium
```

### 问题：无法找到输入框

1. Grok UI 可能已更新
2. 打开 `grok_predictor.py`
3. 更新 `send_prompt()` 方法的选择器
4. 需要定期维护

### 问题：登录过期

```bash
# 删除 session
rm data/grok_session.json

# 重新运行
python scripts/grok_predictor.py
```

---

## 📝 开发状态

### 已完成 ✅
- [x] Playwright 浏览器自动化
- [x] Grok 登录和 Session 管理
- [x] 发送提示词
- [x] 提取响应
- [x] 保存到数据库
- [x] 环境测试脚本

### 待开发 🚧
- [ ] 前端 API 端点
- [ ] 前端展示页面
- [ ] 预测准确性追踪
- [ ] 自动验证预测结果
- [ ] 增强提示词（更多上下文）

---

## 🆘 需要帮助？

查看详细文档：[docs/GROK_AUTOMATION.md](docs/GROK_AUTOMATION.md)

---

**立即开始**：
```bash
# 1. 测试环境
scripts\test_grok_env.bat

# 2. 运行预测
python scripts\grok_predictor.py
```
