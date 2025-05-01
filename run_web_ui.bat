@echo off
echo Active Directory Security Assessment Web UI
echo ==========================================
echo.

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Python is not installed or not in the PATH.
    echo Please install Python 3.8 or higher and try again.
    pause
    exit /b 1
)

REM Add common Node.js installation directories to PATH
echo Adding potential Node.js paths to PATH...
set "PATH=%PATH%;C:\Program Files\nodejs;C:\Program Files (x86)\nodejs;%APPDATA%\npm"

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
if %ERRORLEVEL% neq 0 (
    echo Error: Failed to activate virtual environment.
    echo Trying alternative activation method...
    set "VIRTUAL_ENV=%CD%\venv"
    set "PATH=%VIRTUAL_ENV%\Scripts;%PATH%"
)

REM Verify virtual environment is activated
echo Verifying virtual environment...
venv\Scripts\python -c "import sys; print('Python version:', sys.version); print('Virtual env:', sys.prefix)"
if %ERRORLEVEL% neq 0 (
    echo Error: Virtual environment verification failed.
    pause
    exit /b 1
)

REM Install setuptools first to ensure pkg_resources is available
echo Installing setuptools...
venv\Scripts\pip install setuptools
if %ERRORLEVEL% neq 0 (
    echo Error: Failed to install setuptools.
    pause
    exit /b 1
)

REM Install required dependencies
echo Installing required dependencies...
venv\Scripts\pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo Error: Failed to install required dependencies.
    pause
    exit /b 1
)

REM Ensure react-bootstrap-icons is installed
echo Ensuring react-bootstrap-icons is installed...
cd frontend
npm install react-bootstrap-icons --save --force --no-audit --no-fund --loglevel=error
if %ERRORLEVEL% neq 0 (
    echo Warning: Failed to install react-bootstrap-icons. Continuing anyway...
)
cd ..

REM Run the web UI with sample data and debug mode for more verbose output
echo Starting the Web UI with sample data...
venv\Scripts\python run_web_ui.py --load-sample-data --debug --no-browser

REM Keep the virtual environment active until the script completes
echo.
echo Finished.
pause
