@echo off
REM IES4 JSON Consolidation Batch Runner
REM This script runs the Python consolidation process on Windows

echo IES4 Military Database JSON Consolidator
echo ==========================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if required modules are installed
python -c "import jsonschema" >nul 2>&1
if errorlevel 1 (
    echo Installing required dependencies...
    pip install jsonschema
    if errorlevel 1 (
        echo Error: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Set the base path (modify if needed)
set BASE_PATH=C:\ies4-military-database-analysis

REM Check if base path exists
if not exist "%BASE_PATH%" (
    echo Error: Base path does not exist: %BASE_PATH%
    echo Please verify the path and update this script if needed
    pause
    exit /b 1
)

REM Change to the script directory
cd /d "%~dp0"

REM Run the consolidation
echo.
echo Running consolidation process...
echo Base path: %BASE_PATH%
echo.

python run_consolidation.py --base-path "%BASE_PATH%" --verbose

REM Check result
if errorlevel 1 (
    echo.
    echo Consolidation completed with errors. Check the log file for details.
) else (
    echo.
    echo Consolidation completed successfully!
)

echo.
echo Press any key to exit...
pause >nul
