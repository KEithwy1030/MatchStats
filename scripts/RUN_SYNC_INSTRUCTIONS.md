# 竞彩数据同步指南

## 方法 1：命令行运行（推荐）

在项目根目录下打开命令提示符（CMD）或 PowerShell，执行：

```bash
# Windows CMD
cd E:\CursorData\MatchStats
venv\Scripts\activate.bat
python scripts\sync_sporttery_now.py
```

或使用批处理文件：
```bash
cd E:\CursorData\MatchStats
scripts\test_sporttery_sync.bat
```

## 方法 2：直接运行批处理文件

双击运行：`E:\CursorData\MatchStats\scripts\test_sporttery_sync.bat`

## 方法 3：等待自动同步

竞彩同步任务每 12 小时自动运行一次，无需手动操作。

---

## 验证同步结果

运行后访问：https://kmatch-stats.vercel.app/

切换到"竞彩"标签页，查看是否有比赛数据显示。

## 常见问题

### Q: 运行脚本后没有数据？
A: 竞彩官网可能暂时没有可用的比赛数据，或者 API 请求失败。请稍后再试。

### Q: 出现网络错误？
A: 竞彩官网 API (webapi.sporttery.cn) 需要从中国大陆访问，如果在海外运行可能无法连接。

### Q: 如何查看同步日志？
A: 登录 Supabase Dashboard，查看 `sync_logs` 表，筛选 `source='sporttery'`。
