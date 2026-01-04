@echo off
chcp 65001 > nul
REM Database export script - Auto fix collation and DEFINER issues
REM Usage: export_database.bat [username] [database] [output_file]

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
    set OUTPUT_FILE=webproject.sql
) else (
    set OUTPUT_FILE=%3
)

echo ========================================
echo Database Export Tool
echo ========================================
echo Username: %DB_USER%
echo Database: %DB_NAME%
echo Output File: %OUTPUT_FILE%
echo ========================================
echo.

REM Temporary SQL file
set TEMP_FILE=%OUTPUT_FILE%.tmp

REM Step 1: Export database structure with UTF-8 encoding (without DROP TABLE)
echo [1/3] Exporting database structure...
mysqldump -u %DB_USER% -p --no-data --skip-add-drop-table --default-character-set=utf8mb4 --set-charset --single-transaction %DB_NAME% > "%TEMP_FILE%"

if errorlevel 1 (
    echo Error: Database export failed!
    pause
    exit /b 1
)

REM Step 2: Fix collation_connection to utf8mb4_unicode_ci
echo [2/3] Fixing collation settings...
powershell -NoProfile -Command "$content = Get-Content '%TEMP_FILE%' -Raw -Encoding UTF8; $content = $content -replace 'utf8mb4_0900_ai_ci', 'utf8mb4_unicode_ci'; [System.IO.File]::WriteAllText('%OUTPUT_FILE%', $content, [System.Text.Encoding]::UTF8)"

REM Step 3: Fix DEFINER to admin@localhost
echo [3/3] Fixing DEFINER settings...
powershell -NoProfile -Command "$content = Get-Content '%OUTPUT_FILE%' -Raw -Encoding UTF8; $content = $content -replace 'DEFINER=`root`@`localhost`', 'DEFINER=`admin`@`localhost`'; [System.IO.File]::WriteAllText('%OUTPUT_FILE%', $content, [System.Text.Encoding]::UTF8)"

REM Delete temporary file
del "%TEMP_FILE%"

echo.
echo ========================================
echo Export completed!
echo Output File: %OUTPUT_FILE%
echo ========================================
echo.
echo Verify export file:
echo - collation_connection should be utf8mb4_unicode_ci
echo - DEFINER should be admin@localhost
echo.

pause

