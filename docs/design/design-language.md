# MatchStats 设计语言规范 (Design Language)

> **版本**：v2.0 Terminal Precision Edition  
> **状态**：当前生产落地版本，严格基于 K-design SOP 体系推导。

---

## 一、气质定位 (Tone & Trade-offs)

### 1. 核心气质一句话
> **"Opta Analyst 与 Bloomberg Terminal 级别的专业量化赛事数据工作台：高密度但不逼仄拥挤，严谨克制但不死板冰冷，数字化锐利但不刺眼眩目。"**

### 2. 两组明确取舍 (Trade-offs)
- **取舍一**：坚决舍弃消费级泛娱乐 App 的华而不实（大圆角、紫粉霓虹光晕、装饰性空洞留白）；坚决选取专业金融终端的严谨栅格、等宽基线与精密刻线，通过深石板冷灰（Slate/Obsidian）微色阶提供沉浸式工作台纵深感。
- **取舍二**：坚决舍弃垂直堆叠的臃肿指标卡，坚决选取紧凑高效的 HUD 控制条与行级高通量比赛条目，在有限的首屏视口内实现最大密度的量化信息吞吐。

---

## 二、设计规则系统 (Rules by Four Layers)

### 1. 色彩角色系统 (Color Role System)
| 角色 Token | 色值 | 设计理由与场景 |
| :--- | :--- | :--- |
| `--bg-app` | `#0b0f17` | 深邃炭黑底色，消除纯黑死板，降低长期盯盘视觉疲劳 |
| `--bg-panel` | `#111827` | 次级容器与侧边栏底色，建立 1 级海拔 |
| `--bg-card` | `#151e2e` | 核心卡片底色，与底色形成清晰反差 |
| `--bg-card-hover` | `#1c283d` | 鼠标悬停微高亮状态 |
| `--border-subtle` | `rgba(255, 255, 255, 0.07)` | 极细内部分隔线 |
| `--border-strong` | `rgba(255, 255, 255, 0.15)` | 外轮廓与强调边线 |
| `--text-primary` | `#f8fafc` | 主标题、队伍名、关键比分 |
| `--text-secondary` | `#94a3b8` | 时间、联赛标签、副标题 |
| `--text-muted` | `#64748b` | 次级元数据、表头、已结束标签 |
| `--accent-opta-home` | `#38bdf8` | Opta 主胜概率：冷蓝科技色，代表主队倾向 |
| `--accent-opta-draw` | `#94a3b8` | Opta 平局概率：冷灰中性色，代表平衡胶着 |
| `--accent-opta-away` | `#f43f5e` | Opta 客胜概率：珊瑚玫瑰红，代表客队进攻倾向 |
| `--status-live` | `#10b981` | 正在比赛：高对比亮翡翠绿，配柔和呼吸微光 |
| `--status-scheduled` | `#38bdf8` | 未开赛：专业天青蓝 |
| `--status-finished` | `#64748b` | 完场：克制沉静灰 |

### 2. 字体与排版层级 (Typography & Baseline)
- **数字与计量**：强制使用 `JetBrains Mono`，开启表格等宽数字特性（`font-variant-numeric: tabular-nums`）。用于：比分牌、开赛时间、积分、进球数、Opta 百分比。杜绝字符抖动。
- **正文与界面**：`Inter, -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif`。
- **字号阶梯**：
  - Display (比分): `32px / 700 / Mono`
  - Title (模块标题/球队名): `14px / 600`
  - Body (常规数据/状态): `12px / 500`
  - Caption (微型胜率/时间戳): `11px / 600 / Mono`

### 3. 形状、质感与边线 (Surfaces & Outlines)
- **微倒角**：`border-radius: 4px` 作为全局基准，既去除尖锐刺目，又杜绝 AI 常见的大胶囊软绵感。
- **精密刻线 (Chiseled Borders)**：所有面板采用 `border: 1px solid var(--border-subtle)`，结合 `box-shadow: inset 0 1px 0 0 rgba(255, 255, 255, 0.04)` 形成精密硬件仪表面板切面。

---

## 三、招牌设计决定 (Brand Signatures)

1. **招牌一：Opta AI 胜率全景微条 (Opta Tri-Bar Component)**
   - 放弃原来仅仅在角标下方塞 3 像素小线的做法，在每条比赛卡片的主客队比分下方，构建一体化的双端主客胜率量化条。
   - 左侧亮蓝标示主胜 %，中间标示平局 %，右侧珊瑚红标示客胜 %，比例条宽度自适应并带有微型渐变切口。
   - 点击进入弹窗后，Opta AI 胜率升级为横向全景三轨对比卡，并附带量化优势推导与数据置信度标识。

2. **招牌二：金融级 HUD 监控顶栏 (Terminal HUD Bar)**
   - 将原来垂直占用大量空白的 3 个大卡片，收拢重构为嵌入顶部的 HUD 实时量化看板。
   - 比赛总数、当前视口、数据库健康度、最后同步时间集成在一行极度紧凑的仪表条中，大幅释放垂直空间，让用户首屏即可浏览 8~10 场赛事。

3. **招牌三：球场战术战位可视化 (Pitch Tactics Formation)**
   - 弹窗内首发阵容不仅有列表，更通过程序化 SVG 绿茵草地网格，将球员按守门员、后卫、后腰、前锋真实战术位阶层级渲染，展现专业赛事分析工具深度。

---

## 四、禁区 (Prohibitions)

- ❌ 严禁出现粉紫/渐变霓虹光（Cyberpunk AI 模板通病）。
- ❌ 严禁使用 Emoji 代替专业图标（统一使用 Phosphor 精细线条图标）。
- ❌ 严禁在移动端出现横向拉伸导致文字纵向拆分换行（如“比\n赛\n日\n程”）。
- ❌ 严禁任何导致比分牌宽度跳动的不等宽字体。
- ❌ 严禁破坏现有后端 API 契约和数据结构。
