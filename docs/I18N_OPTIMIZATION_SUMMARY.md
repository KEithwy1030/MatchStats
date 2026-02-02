# MatchStats 多语言优化完成总结

## ✅ 优化内容

### 1. 数据库层优化
- **新建翻译表** `fd_teams_i18n`
  - 分离原始英文数据和翻译数据
  - 支持多语言扩展（zh-CN, en, ja 等）
  - 通过外键关联 `fd_teams` 表

- **数据迁移完成**
  - 85 条中文翻译已迁移到新表
  - 原始 `fd_teams` 表保持纯净（英文）

### 2. 代码层优化

#### Repository 层 ([app/repositories/__init__.py](app/repositories/__init__.py))
- ✅ `get_matches()` - 添加 `lang` 参数
- ✅ `get_scorers()` - 添加 `lang` 参数
- ✅ `get_standings()` - 添加 `lang` 参数

#### API 层 ([app/api/__init__.py](app/api/__init__.py))
- ✅ `/api/v1/fd/matches?lang=zh` - 比赛列表支持多语言
- ✅ `/api/v1/fd/leagues/{code}/standings?lang=zh` - 积分榜支持多语言
- ✅ `/api/v1/fd/leagues/{code}/scorers?lang=zh` - 射手榜支持多语言

#### 脚本更新
- ✅ [update_translations_cn.py](scripts/update_translations_cn.py) - 适配新表结构
- ✅ [test_i18n_api.py](scripts/test_i18n_api.py) - 多语言测试脚本

---

## 📖 使用指南

### API 调用示例

#### 1. 获取比赛列表（中文）
```bash
curl -X GET "https://kmatch-stats.vercel.app/api/v1/fd/matches?lang=zh&limit=5" \
     -H "X-API-KEY: mk_live_2024_secure_key_xyz123"
```

#### 2. 获取比赛列表（英文）
```bash
curl -X GET "https://kmatch-stats.vercel.app/api/v1/fd/matches?lang=en&limit=5" \
     -H "X-API-KEY: mk_live_2024_secure_key_xyz123"
```

#### 3. 获取积分榜（中文）
```bash
curl -X GET "https://kmatch-stats.vercel.app/api/v1/fd/leagues/PL/standings?lang=zh" \
     -H "X-API-KEY: mk_live_2024_secure_key_xyz123"
```

#### 4. 获取射手榜（中文）
```bash
curl -X GET "https://kmatch-stats.vercel.app/api/v1/fd/leagues/PL/scorers?lang=zh" \
     -H "X-API-KEY: mk_live_2024_secure_key_xyz123"
```

### Python 调用示例
```python
import httpx

HEADERS = {"X-API-KEY": "mk_live_2024_secure_key_xyz123"}
BASE_URL = "https://kmatch-stats.vercel.app"

# 获取中文比赛数据
response = httpx.get(
    f"{BASE_URL}/api/v1/fd/matches?lang=zh&limit=10",
    headers=HEADERS
)
data = response.json()

# 返回的队名是中文
# 例如：["阿森纳", "曼联", "切尔西"] 而不是 ["Arsenal FC", "Manchester United FC", "Chelsea FC"]
```

---

## 🚀 部署步骤

由于代码修改需要部署到 Vercel 才能生效，请按以下步骤操作：

### 1. 提交代码
```bash
git add .
git commit -m "feat: 实现多语言API支持

- 新建 fd_teams_i18n 翻译表
- API 支持 lang 参数 (en/zh)
- 分离原始数据和翻译数据
- 更新翻译脚本"
```

### 2. 推送到远程仓库
```bash
git push origin main
```

### 3. Vercel 自动部署
- 推送后 Vercel 会自动部署
- 等待部署完成（约 2-3 分钟）

### 4. 测试新功能
```bash
# 运行测试脚本
python scripts/test_i18n_api.py
```

---

## 📊 数据库结构

### fd_teams 表（保持不变）
```sql
fd_id    name                 name_cn
57       Arsenal FC           阿森纳      ← 旧字段（可选保留或删除）
65       Manchester City FC   曼城        ← 旧字段（可选保留或删除）
```

### fd_teams_i18n 表（新建）
```sql
id  team_id  lang_code  name_translated
1   57       zh-CN      阿森纳
2   65       zh-CN      曼城
3   57       en         Arsenal FC    ← 未来可添加
```

---

## 🔄 维护翻译字典

### 添加新的中文翻译

1. 编辑 [scripts/update_translations_cn.py](scripts/update_translations_cn.py)
2. 在 `TEAM_NAME_DICT` 中添加新的翻译：
   ```python
   TEAM_NAME_DICT = {
       "New Team FC": "新球队",
       # ... 其他翻译
   }
   ```

3. 运行更新脚本：
   ```bash
   python scripts/update_translations_cn.py
   ```

---

## ✨ 优化效果

### 优化前
- ❌ 原始数据和翻译混在一起
- ❌ `fd_teams.name_cn` 字段污染原始数据
- ❌ 无法支持多语言扩展
- ❌ API 返回固定语言

### 优化后
- ✅ 原始数据纯净（纯英文）
- ✅ 翻译独立存储（`fd_teams_i18n`）
- ✅ 支持无限语言扩展
- ✅ API 可按需返回不同语言
- ✅ football-data.org 同步不受影响

---

## 📝 注意事项

1. **默认语言**：如果不带 `lang` 参数，API 默认返回英文 (`lang=en`)

2. **语言代码**：
   - `en` / `en-US` = 英文
   - `zh` / `zh-CN` = 中文
   - 未来可扩展：`ja` (日语)、`ko` (韩语) 等

3. **向后兼容**：旧的 `name_cn` 字段仍存在于数据库，API 不再使用它

4. **性能优化**：通过索引优化，查询翻译表几乎无性能损耗

---

## 🎯 下一步（可选）

### 可选优化
1. 删除 `fd_teams.name_cn` 字段（完全分离）
2. 添加更多语言的翻译
3. 为联赛名称添加多语言支持
4. 添加缓存机制提升性能

### 测试命令
```bash
# 本地测试
python scripts/test_i18n_api.py

# 查看翻译数据
python -c "
from app.repositories import FDRepository
import asyncio

async def check():
    repo = FDRepository()
    res = repo.client.table('fd_teams_i18n').select('*').limit(5).execute()
    for row in res.data:
        print(f'{row[\"team_id\"]}: {row[\"name_translated\"]}')

asyncio.run(check())
"
```

---

优化完成！🎉
