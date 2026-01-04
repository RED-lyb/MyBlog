@echo off
chcp 65001 > nul
REM Database import script
REM Supports both full backup (with DROP TABLE) and safe backup (without DROP TABLE)
REM Usage: import_database.bat [username] [database] [sql_file] [mode]
REM Note: For SQL files with functions/triggers, use root user or ensure log_bin_trust_function_creators=1

setlocal enabledelayedexpansion

REM Set default values
if "%1"=="" (
    goto :show_usage
)

set DB_USER=%1

if "%2"=="" (
    goto :show_usage
)

set DB_NAME=%2

if "%3"=="" (
    goto :show_usage
)

set SQL_FILE=%3

if "%4"=="" (
    set IMPORT_MODE=safe
) else (
    set IMPORT_MODE=%4
)

goto :start_import

:show_usage
echo ========================================
echo Database Import Tool
echo ========================================
echo Usage: import_database.bat [username] [database] [sql_file] [mode]
echo.
echo Parameters:
echo   username  - MySQL username (default: admin)
echo   database  - Database name (default: webproject)
echo   sql_file  - SQL file to import (required)
echo   mode      - Import mode: safe, force, or drop (default: safe)
echo.
echo Modes:
echo   safe  - Add IF NOT EXISTS to CREATE TABLE (recommended)
echo   force - Skip errors and continue (use --force flag)
echo   drop  - Use file as-is (may include DROP TABLE)
echo.
echo Examples:
echo   import_database.bat root webproject backup.sql safe
echo   import_database.bat root webproject backup.sql force
echo   import_database.bat root webproject backup.sql drop
echo.
echo Note: For SQL files with functions/triggers, use root user
echo       or ensure log_bin_trust_function_creators=1 is set
echo.
pause
exit /b 1

:start_import
echo ========================================
echo Database Import Tool
echo ========================================
echo Username: %DB_USER%
echo Database: %DB_NAME%
echo SQL File: %SQL_FILE%
echo Import Mode: %IMPORT_MODE%
echo ========================================
echo.

REM Check if SQL file exists
if not exist "%SQL_FILE%" (
    echo Error: SQL file not found: %SQL_FILE%
    pause
    exit /b 1
)

REM Process based on mode
if /i "%IMPORT_MODE%"=="safe" goto :mode_safe
if /i "%IMPORT_MODE%"=="force" goto :mode_force
if /i "%IMPORT_MODE%"=="drop" goto :mode_drop

echo Error: Invalid import mode: %IMPORT_MODE%
echo Valid modes: safe, force, drop
pause
exit /b 1

:mode_safe
echo [Safe Mode] Adding IF NOT EXISTS to CREATE TABLE statements...
set SAFE_FILE=%SQL_FILE%.safe
powershell -NoProfile -Command "$content = Get-Content '%SQL_FILE%' -Raw -Encoding UTF8; $content = $content -replace 'CREATE TABLE `', 'CREATE TABLE IF NOT EXISTS `'; [System.IO.File]::WriteAllText('%SAFE_FILE%', $content, [System.Text.Encoding]::UTF8)"

if errorlevel 1 (
    echo Error: Failed to process SQL file!
    pause
    exit /b 1
)

echo Importing database...
mysql -u %DB_USER% -p %DB_NAME% < "%SAFE_FILE%"

if errorlevel 1 (
    echo Error: Database import failed!
    echo Temporary file: %SAFE_FILE%
    echo.
    echo If you see permission errors related to functions/triggers:
    echo   - Use root user: import_database.bat root webproject %SQL_FILE% safe
    echo   - Or set: SET GLOBAL log_bin_trust_function_creators=1;
    pause
    exit /b 1
)

echo.
echo Temporary file created: %SAFE_FILE%
echo You can delete it after verifying the import.
goto :end_import

:mode_force
echo [Force Mode] Importing with --force flag (skips errors)...
mysql -u %DB_USER% -p --force %DB_NAME% < "%SQL_FILE%"

if errorlevel 1 (
    echo Warning: Some errors occurred but import continued.
    echo Please check the output above for details.
)
goto :end_import

:mode_drop
echo [Drop Mode] Importing file as-is (may include DROP TABLE)...
echo WARNING: This will execute DROP TABLE statements if present!
echo.
set /p confirm=Are you sure you want to continue? (Y/N): 

if /i not "!confirm!"=="Y" (
    echo Import cancelled.
    pause
    exit /b 0
)

mysql -u %DB_USER% -p %DB_NAME% < "%SQL_FILE%"

if errorlevel 1 (
    echo Error: Database import failed!
    echo.
    echo If you see permission errors related to functions/triggers:
    echo   - Use root user: import_database.bat root webproject %SQL_FILE% drop
    echo   - Or set: SET GLOBAL log_bin_trust_function_creators=1;
    pause
    exit /b 1
)
goto :end_import

:end_import

echo.
echo ========================================
echo Import completed!
echo ========================================
echo.
echo Please verify the import was successful.
echo.

pause
