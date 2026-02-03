"""
修复 MatchStatts_API_GUIDE.md 中的错误信息
"""
import os

FILE_PATH = "e:/CursorData/MatchStats/docs/MatchStatts_API_GUIDE.md"

# 备份
os.system(f'cp "{FILE_PATH}" "{FILE_PATH}.bak"')

# 读取文件
with open(FILE_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# 替换错误的 API Key
content = content.replace('matchstats_secret_2026', 'mk_live_2024_secure_key_xyz123')

# 修复过时的 API 路由
content = content.replace('/api/matches/today', '/api/v1/fd/matches?lang=zh&limit=10')
content = content.replace('/api/matches/recent', '/api/v1/fd/matches?status=FINISHED')
content = content.replace('/api/standings/', '/api/v1/fd/leagues/')
content = content.replace('/api/sporttery/matches', '/api/v1/sporttery/matches')

# 添加多语言说明（在"3. 核心 API 接口清单"后面）
i18n_section = '''

---

## 3.1 多语言支持

**重要更新**：MatchStats API 现已支持多语言数据返回！

### 支持的语言

| 语言代码 | 说明 |
|---------|------|
| `en` | 英文（默认） |
| `zh` | 中文 |

### 使用方法

在 API 请求中添加 `lang` 查询参数：

```bash
# 获取中文数据
curl -X GET "https://kmatch-stats.vercel.app/api/v1/fd/matches?lang=zh&limit=10" \
     -H "X-API-KEY: mk_live_2024_secure_key_xyz123"

# 获取英文数据
curl -X GET "https://kmatch-stats.vercel.app/api/v1/fd/matches?lang=en&limit=10" \
     -H "X-API-KEY: mk_live_2024_secure_key_xyz123"
```

### 支持多语言的端点

- ✅ `/api/v1/fd/matches` - 比赛列表
- ✅ `/api/v1/fd/leagues/{code}/standings` - 积分榜
- ✅ `/api/v1/fd/leagues/{code}/scorers` - 射手榜

---

'''

# 在"3. 核心 API 接口清单"后面插入多语言说明
if '## 3.1 多语言支持' not in content:
    content = content.replace('---\n\n## 4. 开发者代码示例', i18n_section + '## 4. 开发者代码示例')

# 更新版本号
content = content.replace('`PROD (v0.1.0)`', '`PROD (v1.1.0)`')

# 写回文件
with open(FILE_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ API Guide 已更新:")
print("  1. API Key 已修复")
print("  2. API 路由已更新")
print("  3. 多语言支持已添加")
print("  4. 版本号已更新至 v1.1.0")
