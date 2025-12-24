# 网盘文件定时清理命令

## 功能说明

`cleanup_old_files` 命令用于清理网盘 `files` 文件夹下超过指定天数未修改的文件和文件夹。

### 清理规则

1. **文件**：如果文件的最后修改时间超过指定天数（默认7天），直接删除
2. **文件夹**：
   - 如果文件夹的最后修改时间超过指定天数（默认7天）
   - 且文件夹为空（内部没有文件或子文件夹）
   - 则删除该文件夹
   - 如果文件夹不为空，会先检查内部文件，删除超过天数的文件后，再检查文件夹是否变空

## 使用方法

### 基本用法

```bash
# 使用默认7天清理
python manage.py cleanup_old_files

# 指定清理天数（例如30天）
python manage.py cleanup_old_files --days 30

# 预览模式（仅显示将要删除的文件，不实际删除）
python manage.py cleanup_old_files --dry-run
```

### 参数说明

- `--days`: 指定删除多少天前修改的文件（默认7天）
- `--dry-run`: 预览模式，仅显示将要删除的文件，不实际删除
- `--no-log`: 不写入日志文件，仅输出到控制台（默认情况下会同时输出到控制台和日志文件）

## 设置定时任务

### Linux/Unix 系统（使用 Cron）

编辑 crontab：
```bash
crontab -e
```

添加以下行（每天0:00执行）：
```bash
0 0 * * * cd /path/to/your/project/back && /path/to/python manage.py cleanup_old_files >> /path/to/log/cleanup.log 2>&1
```

示例（假设项目路径为 `/var/www/webproject/back`，Python路径为 `/usr/bin/python3`）：
```bash
0 0 * * * cd /var/www/webproject/back && /usr/bin/python3 manage.py cleanup_old_files >> /var/www/webproject/log/cleanup.log 2>&1
```

### Windows 系统（使用任务计划程序）

1. 打开"任务计划程序"（Task Scheduler）
2. 创建基本任务
3. 设置触发器：每天，时间 00:00
4. 设置操作：启动程序
   - 程序：`python.exe` 的完整路径
   - 参数：`manage.py cleanup_old_files`
   - 起始于：项目 `back` 目录的完整路径

### 使用 Django 的定时任务（推荐使用 APScheduler 或 Celery）

如果需要更灵活的定时任务管理，可以考虑使用：
- **APScheduler**: 轻量级，适合简单定时任务
- **Celery**: 功能强大，适合复杂的异步任务和分布式系统

## 日志功能

### 日志文件位置

默认情况下，所有日志信息会同时输出到：
- **控制台**：标准输出
- **日志文件**：`/webproject/my-blog/log/back.log`

### 日志管理

- **自动日志轮转**：当日志文件大小达到 **50MB** 时，会自动删除前50%的行，保留最新的50%内容
- **日志格式**：`时间戳 - 模块名 - 级别 - 消息内容`
- **日志级别**：INFO（信息）、WARNING（警告）、ERROR（错误）

### 禁用日志

如果只想输出到控制台，可以使用 `--no-log` 参数：

```bash
python manage.py cleanup_old_files --no-log
```

## 注意事项

1. **备份**：在生产环境使用前，建议先使用 `--dry-run` 参数预览将要删除的文件
2. **权限**：确保运行命令的用户有足够的权限删除文件和文件夹，以及写入日志文件的权限
3. **日志目录**：确保日志目录 `/webproject/my-blog/log/` 存在，或确保运行用户有创建该目录的权限
4. **日志文件路径**：如果需要在不同环境下使用不同的日志路径，可以修改 `cleanup_old_files.py` 中的 `log_file_path` 变量
5. **测试**：建议先在测试环境验证命令功能正常后再部署到生产环境

## 示例输出

```
开始清理 7 天前修改的文件...
截止时间: 2024-01-15 00:00:00
第一步：删除超过指定天数的文件...
删除文件: 1/old_file.txt
删除文件: 2/subfolder/old_file2.jpg

第二步：删除超过指定天数且为空的文件夹...
删除空文件夹: 1/empty_folder
删除空文件夹: 2/subfolder

==================================================
清理完成
删除文件数: 2
删除文件夹数: 2
==================================================
```
