@echo off
echo Active Directory Security Assessment Agent
echo ========================================
echo.

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Python is not installed or not in the PATH.
    echo Please install Python 3.8 or higher and try again.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo Error: Failed to create virtual environment.
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install setuptools first to ensure pkg_resources is available
echo Installing setuptools...
pip install setuptools

REM Install required dependencies
echo Installing required dependencies...
pip install -r requirements.txt

REM Run dependency checker
echo Running dependency checker...
set RUN_FROM_SCRIPT=1
python check_dependencies.py

REM Run the main application in mock mode by default
echo Running the application in mock mode...
python main.py --mock

REM Keep the virtual environment active until the script completes
REM The deactivate command will be called by the dependency checker if needed

echo.
echo Finished.
pause
