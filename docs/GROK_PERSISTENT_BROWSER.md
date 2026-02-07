# Grok 持久化浏览器配置方案

## 🎯 问题分析

你提到的问题非常关键：

### 问题：每次启动新浏览器会被反爬
- ✅ 新浏览器 = 新指纹 = 容易被识别为机器人
- ❌ 需要保持真实的浏览器身份

## 🔧 解决方案：持久化浏览器 Profile

### 方案对比

| 方案 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| **新建 Chrome Profile** | 完全隔离，稳定 | 需要专门维护 | ⭐⭐⭐⭐ |
| **使用现有浏览器** | 无需额外配置 | 可能干扰正常使用 | ⭐⭐⭐ |
| **Playwright 持久化 Context** | 专为自动化设计，灵活 | 需要自己管理 | ⭐⭐⭐⭐⭐ |

### ✅ 推荐方案：Playwright 持久化 Context

我们采用这个方案，因为它：
1. ✅ **专门为自动化设计**
2. ✅ **保持登录状态**
3. ✅ **复用共享浏览器**（E:\CursorData\MCP\playwright-mcp\）
4. ✅ **独立配置目录**（data/grok_profile/）
5. ✅ **保存 Cookies 和 Session**

---

## 🏗️ 技术实现

### 1. 目录结构

```
E:\CursorData\MatchStats\
├── data\
│   └── grok_profile\          ← 持久化数据（专门用于 Grok）
│       ├── cookies.json      ← 保存的登录 Cookies
│       ├── error_*.png        ← 错误截图
│       └── ...
│
└── E:\CursorData\MCP\
    └── playwright-mcp\
        └── browser_data\      ← 共享 Playwright 浏览器
            └── chromium-1208\
                └── chrome-win\
                    └── chrome.exe
```

### 2. 关键配置

#### A. 使用共享浏览器（节省空间）

```python
# 指向共享的 Chromium
SHARED_BROWSER_PATH = Path(r"E:\CursorData\MCP\playwright-mcp\browser_data")
chromium_path = SHARED_BROWSER_PATH / "chromium-1208" / "chrome-win" / "chrome.exe"

executable_path = str(chromium_path) if chromium_path.exists() else None
```

**好处**：
- 不需要重复下载浏览器（节省 300MB+ 空间）
- 复用已有的浏览器二进制文件

#### B. 持久化用户数据

```python
# 专门的配置目录
GROK_USER_DATA = Path("data/grok_profile")

# 每次运行时复用同一目录
# 保存：Cookies, Local Storage, Session Storage, Cache
```

**持久化的内容**：
- ✅ Cookies（登录状态）
- ✅ Local Storage
- ✅ Session Storage
- ✅ 缓存
- ✅ 浏览器历史

#### C. 反检测措施

```python
# 1. 禁用自动化特征
args=[
    '--disable-blink-features=AutomationControlled',
]

# 2. 注入反检测脚本
await context.add_init_script("""
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    });

    window.chrome = { runtime: {} };
""")

# 3. 真实 User Agent
user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...'
```

---

## 🔄 工作流程

```
第一次运行：
    ↓
创建 data/grok_profile/ 目录
    ↓
启动浏览器（使用共享二进制）
    ↓
访问 Grok.com
    ↓
检测未登录 → 提示手动登录
    ↓
保存 Cookies 到 data/grok_profile/cookies.json
    ↓
开始预测
    ↓
关闭浏览器

---

后续运行：
    ↓
复用 data/grok_profile/ 目录
    ↓
启动浏览器（使用共享二进制）
    ↓
加载保存的 Cookies
    ↓
访问 Grok.com（已登录）
    ↓
直接开始预测
    ↓
关闭浏览器
```

---

## 📊 持久化效果

### 对比：持久化 vs 非持久化

| 特性 | 非持久化（每次新建） | 持久化（复用） |
|------|---------------------|--------------|
| **Cookies** | ❌ 每次清空 | ✅ 保留 |
| **登录状态** | ❌ 每次需登录 | ✅ 保持登录 |
| **浏览器指纹** | ❌ 每次不同 | ✅ 一致 |
| **Cache** | ❌ 每次清空 | ✅ 保留 |
| **被检测风险** | ⚠️ 较高 | ✅ 较低 |

---

## 🎛️ 高级配置（可选）

### 选项 1：完全独立的 Chrome Profile

如果担心干扰，创建完全独立的 Profile：

```python
# 使用 Chrome 用户数据目录
context = await browser.new_context(
    user_data_dir=str(GROK_USER_DATA)  # 指定完整用户数据目录
)
```

**效果**：
- ✅ 完全隔离
- ✅ 所有浏览器数据都保存
- ⚠️ 目录更大（100MB+）

### 选项 2：使用现有 Chrome Profile

使用你日常使用的 Chrome：

```python
# 使用你的 Chrome Profile
context = await browser.new_context(
    channel="chrome",  # 使用系统 Chrome
    user_data_dir=r"C:\Users\YourName\AppData\Local\Google\Chrome\User Data"
)
```

**⚠️ 不推荐**：
- 可能干扰正常使用
- 需要关闭 Chrome 才能运行脚本

---

## 📝 配置文件位置

所有配置在 `scripts/grok_predictor.py` 中：

```python
# 第 35-39 行：路径配置
SHARED_PLAYWRIGHT_PATH = Path(r"E:\CursorData\MCP\playwright-mcp")
SHARED_BROWSER_PATH = SHARED_PLAYWRIGHT_PATH / "browser_data"
GROK_USER_DATA = Path("data/grok_profile")

# 第 98-166 行：浏览器启动逻辑
async def create_persistent_browser(self):
    # ... 持久化配置
```

---

## ✅ 优势总结

### 使用此方案的好处

1. **✅ 避免反爬**：保持一致的浏览器指纹
2. **✅ 无需重复登录**：Cookies 保存 7-30 天
3. **✅ 节省空间**：复用共享浏览器（不重复下载）
4. **✅ 稳定可靠**：专门为自动化优化
5. **✅ 易于维护**：独立配置，互不干扰

### 与你的要求完全匹配

- ✅ **实例浏览器**：复用真实浏览器二进制
- ✅ **持久化**：保持登录状态和指纹
- ✅ **共享路径**：使用 E:\CursorData\MCP\playwright-mcp\
- ✅ **独立配置**：data/grok_profile/ 专门用于 Grok

---

## 🚀 使用方法

### 首次运行

```bash
cd E:\CursorData\MatchStats
python scripts/grok_predictor.py
```

**流程**：
1. 自动创建 `data/grok_profile/` 目录
2. 启动持久化浏览器
3. 提示手动登录
4. 保存 Cookies
5. 开始预测

### 后续运行

```bash
python scripts/grok_predictor.py
```

**流程**：
1. 加载保存的 Cookies
2. 直接访问 Grok（已登录状态）
3. 开始预测

---

## 🗂️ 目录管理

### 持久化数据位置

```
data/grok_profile/
├── cookies.json           ← 登录 Cookies
├── error_20260203_120000.png  ← 错误截图
└── ...
```

### 清理方法

如果需要重置（清除所有保存的数据）：

```bash
# 删除持久化目录
rm -rf data/grok_profile/

# 下次运行会重新创建
```

---

## 🎯 总结

这个方案完美解决了你提到的两个关键问题：

1. **✅ 使用共享 Playwright**：从 `E:\CursorData\MCP\playwright-mcp\` 获取
2. **✅ 持久化浏览器**：使用独立的 `data/grok_profile/` 配置

**效果**：
- ✅ 避免被反爬（保持浏览器指纹一致）
- ✅ 保持登录状态（无需重复登录）
- ✅ 节省磁盘空间（复用共享浏览器）
- ✅ 易于维护（独立配置）

---

**立即开始使用**：
```bash
python scripts/grok_predictor.py
```
