@echo off
REM DBPF Explorer Launcher for Windows
REM
REM This batch file provides a convenient way to launch the DBPF Explorer
REM application on Windows systems.

setlocal enabledelayedexpansion

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"

REM Remove trailing backslash if present
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

REM Check if Python 3 is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3 from https://python.org and try again
    pause
    exit /b 1
)

REM Check if required files exist
if not exist "%SCRIPT_DIR%\dbpf_explorer.py" (
    echo Error: dbpf_explorer.py not found in %SCRIPT_DIR%
    pause
    exit /b 1
)

if not exist "%SCRIPT_DIR%\dbpf_interface.py" (
    echo Error: dbpf_interface.py not found in %SCRIPT_DIR%
    pause
    exit /b 1
)

if not exist "%SCRIPT_DIR%\dbpf_unpacker.py" (
    echo Error: dbpf_unpacker.py not found in %SCRIPT_DIR%
    pause
    exit /b 1
)

REM Launch the application
echo Starting DBPF Explorer...
cd /d "%SCRIPT_DIR%"
python dbpf_explorer.py

REM Check exit code
if errorlevel 1 (
    echo.
    echo DBPF Explorer exited with error code %errorlevel%
    pause
)

exit /b %errorlevel%</content>
<parameter name="filePath">/workspaces/SporeModder-FX/launch_dbpf_explorer.bat