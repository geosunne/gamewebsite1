# 游戏数据增量抓取使用说明

## 🎯 功能特性

- ✅ **增量添加**: 自动跳过已存在的游戏
- ✅ **批量处理**: 最多处理100个游戏
- ✅ **去重机制**: 基于游戏URL进行去重
- ✅ **进度跟踪**: 显示新增和跳过的游戏数量

## 🚀 使用方法

### 方法1: 使用修改后的主脚本
```bash
source venv/bin/activate
python analyze_onlinegames_structure.py
```

### 方法2: 使用包装脚本 (推荐)
```bash
source venv/bin/activate
python run_incremental_scraping.py
```

### 方法3: 指定游戏数量
```bash
source venv/bin/activate
python run_incremental_scraping.py 50  # 最多处理50个游戏
```

## 📊 输出示例

```
🚀 Starting incremental game scraping (max: 100 games)...
📊 Current games in database: 50

🔍 Starting to analyze games from OnlineGames.io...
[1/100] Processing: New Game Title
  ✅ Found 1 iframe(s), description: 150 chars, thumbnail: ✅

[2/100] Processing: Existing Game
  ⏭️  Skipping existing game: Existing Game

💾 Saving games with deduplication...

📊 Summary:
  📁 File: games_data.json
  🆕 New games added: 25
  ⏭️  Existing games skipped: 25
  📈 Total games in file: 75
```

## 🔧 主要修改

1. **max_games 设置为 100**: 每次运行最多处理100个游戏
2. **增量添加**: 检查现有的 games_data.json，只添加新游戏
3. **URL去重**: 基于游戏URL判断是否已存在
4. **统计报告**: 显示新增、跳过和总数量

## 📝 注意事项

- 脚本会自动加载现有的 `games_data.json` 文件
- 如果文件不存在，将创建新文件
- 每次运行会更新时间戳
- 游戏按照抓取顺序添加到数组末尾