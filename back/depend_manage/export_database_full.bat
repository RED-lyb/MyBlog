@echo off
chcp 65001 > nul
REM Database full export script - Includes DROP TABLE, structure and data
REM Auto fix collation and DEFINER issues
REM Usage: export_database_full.bat [username] [database] [output_file]

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
    set OUTPUT_FILE=webproject_full.sql
) else (
    set OUTPUT_FILE=%3
)

echo ========================================
echo Database Full Export Tool
echo ========================================
echo Username: %DB_USER%
echo Database: %DB_NAME%
echo Output File: %OUTPUT_FILE%
echo ========================================
echo.
echo WARNING: This will include DROP TABLE statements!
echo This script exports both structure and data.
echo.

REM Temporary SQL file
set TEMP_FILE=%OUTPUT_FILE%.tmp

REM Step 1: Export database with structure and data (includes DROP TABLE)
echo [1/4] Exporting database structure and data...
mysqldump -u %DB_USER% -p --default-character-set=utf8mb4 --set-charset --single-transaction --lock-tables=false %DB_NAME% > "%TEMP_FILE%"

if errorlevel 1 (
    echo Error: Database export failed!
    pause
    exit /b 1
)

REM Step 2: Fix collation_connection to utf8mb4_unicode_ci
echo [2/4] Fixing collation settings...
powershell -NoProfile -Command "$content = Get-Content '%TEMP_FILE%' -Raw -Encoding UTF8; $content = $content -replace 'utf8mb4_0900_ai_ci', 'utf8mb4_unicode_ci'; [System.IO.File]::WriteAllText('%OUTPUT_FILE%.tmp2', $content, [System.Text.Encoding]::UTF8)"

REM Step 3: Fix DEFINER to admin@localhost
echo [3/4] Fixing DEFINER settings...
powershell -NoProfile -Command "$content = Get-Content '%OUTPUT_FILE%.tmp2' -Raw -Encoding UTF8; $content = $content -replace 'DEFINER=`root`@`localhost`', 'DEFINER=`admin`@`localhost`'; [System.IO.File]::WriteAllText('%OUTPUT_FILE%', $content, [System.Text.Encoding]::UTF8)"

REM Step 4: Clean up temporary files
echo [4/4] Cleaning up temporary files...
del "%TEMP_FILE%"
del "%OUTPUT_FILE%.tmp2"

echo.
echo ========================================
echo Export completed!
echo Output File: %OUTPUT_FILE%
echo ========================================
echo.
echo Verify export file:
echo - Contains DROP TABLE statements
echo - Contains CREATE TABLE statements
echo - Contains INSERT statements (data)
echo - collation_connection should be utf8mb4_unicode_ci
echo - DEFINER should be admin@localhost
echo.
echo WARNING: This file will DROP existing tables when imported!
echo Use this file only for full database restoration or initial setup.
echo.

pause

