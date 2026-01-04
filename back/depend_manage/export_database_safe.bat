@echo off
chcp 65001 > nul
REM 安全数据库导出脚本 - 不包含 DROP TABLE 语句，用于服务器更新
REM Usage: export_database_safe.bat [username] [database] [output_file]
REM 此脚本导出的 SQL 文件不包含 DROP TABLE 语句，可以安全地在生产环境导入
REM 如果表已存在，CREATE TABLE 语句会失败，但不会删除现有数据

setlocal enabledelayedexpansion

REM Set default values
if "%1"=="" (
    set DB_USER=admin
) else (
    set DB_USER=%1
)

if "%2"=="" (
    set DB_NAME=webproject
) else (
    set DB_NAME=%2
)

if "%3"=="" (
    set OUTPUT_FILE=webproject_safe.sql
) else (
    set OUTPUT_FILE=%3
)

echo ========================================
echo 安全数据库导出工具 (Safe Database Export)
echo ========================================
echo 用户名: %DB_USER%
echo 数据库: %DB_NAME%
echo 输出文件: %OUTPUT_FILE%
echo ========================================
echo.
echo 注意: 此脚本导出的 SQL 文件不包含 DROP TABLE 语句
echo 可以安全地在生产环境导入，不会删除现有数据
echo ========================================
echo.

REM Temporary SQL file
set TEMP_FILE=%OUTPUT_FILE%.tmp

REM Step 1: Export database structure with UTF-8 encoding (without DROP TABLE)
echo [1/4] 正在导出数据库结构（不包含 DROP TABLE）...
mysqldump -u %DB_USER% -p --no-data --skip-add-drop-table --default-character-set=utf8mb4 --set-charset --single-transaction %DB_NAME% > "%TEMP_FILE%"

if errorlevel 1 (
    echo 错误: 数据库导出失败!
    pause
    exit /b 1
)

REM Step 2: Remove DROP TABLE statements (if any remain)
echo [2/4] 移除 DROP TABLE 语句...
powershell -NoProfile -Command "$content = Get-Content '%TEMP_FILE%' -Raw -Encoding UTF8; $content = $content -replace '(?m)^DROP TABLE IF EXISTS.*?;[\r\n]*', ''; [System.IO.File]::WriteAllText('%TEMP_FILE%', $content, [System.Text.Encoding]::UTF8)"

REM Step 3: Fix collation_connection to utf8mb4_unicode_ci
echo [3/4] 修复字符集设置...
powershell -NoProfile -Command "$content = Get-Content '%TEMP_FILE%' -Raw -Encoding UTF8; $content = $content -replace 'utf8mb4_0900_ai_ci', 'utf8mb4_unicode_ci'; [System.IO.File]::WriteAllText('%OUTPUT_FILE%', $content, [System.Text.Encoding]::UTF8)"

REM Step 4: Fix DEFINER to admin@localhost
echo [4/4] 修复 DEFINER 设置...
powershell -NoProfile -Command "$content = Get-Content '%OUTPUT_FILE%' -Raw -Encoding UTF8; $content = $content -replace 'DEFINER=`root`@`localhost`', 'DEFINER=`admin`@`localhost`'; [System.IO.File]::WriteAllText('%OUTPUT_FILE%', $content, [System.Text.Encoding]::UTF8)"

REM Delete temporary file
del "%TEMP_FILE%"

echo.
echo ========================================
echo 导出完成！
echo 输出文件: %OUTPUT_FILE%
echo ========================================
echo.
echo 验证导出文件:
echo - 不包含 DROP TABLE 语句
echo - collation_connection 应为 utf8mb4_unicode_ci
echo - DEFINER 应为 admin@localhost
echo.
echo 使用方法:
echo 在服务器上导入: mysql -u admin -p webproject < %OUTPUT_FILE%
echo 注意: 如果表已存在，CREATE TABLE 会失败，但不会影响现有数据
echo 如果需要更新表结构，请使用 ALTER TABLE 语句
echo.

pause

