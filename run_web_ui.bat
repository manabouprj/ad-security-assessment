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

REM Check if npm is installed
where npm >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: npm is not installed or not in the PATH.
    echo Please install Node.js and npm to run the frontend.
    echo Download from: https://nodejs.org/
    pause
    exit /b 1
)

REM Check if node is installed
where node >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Node.js is not installed or not in the PATH.
    echo Please install Node.js to run the frontend.
    echo Download from: https://nodejs.org/
    pause
    exit /b 1
)

REM Install required Python packages directly (no virtual environment)
echo Installing required Python packages...
python -m pip install --upgrade pip setuptools
if %ERRORLEVEL% neq 0 (
    echo Warning: Failed to upgrade pip and setuptools. Continuing anyway...
)

python -m pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo Warning: Failed to install some Python dependencies. Continuing anyway...
)

REM Ensure frontend dependencies are installed
echo Installing frontend dependencies...
cd frontend
echo Running npm install with --force flag to resolve dependency conflicts...
npm install --force --no-audit --no-fund --loglevel=error
if %ERRORLEVEL% neq 0 (
    echo Warning: Failed to install all frontend dependencies. Continuing anyway...
    
    REM Try installing core dependencies one by one
    echo Installing react and core dependencies...
    call npm install react react-dom react-scripts react-router-dom --force --no-audit --no-fund --loglevel=error
    
    echo Installing bootstrap dependencies...
    call npm install bootstrap react-bootstrap --force --no-audit --no-fund --loglevel=error
    
    echo Installing chart dependencies...
    call npm install chart.js react-chartjs-2 --force --no-audit --no-fund --loglevel=error
)

REM Ensure react-bootstrap-icons is installed specifically
echo Ensuring react-bootstrap-icons is installed...
npm install react-bootstrap-icons --save --force --no-audit --no-fund --loglevel=error
if %ERRORLEVEL% neq 0 (
    echo Warning: Failed to install react-bootstrap-icons. Trying alternative approach...
    call npm install react-bootstrap-icons@^1.10.3 --save --force --no-audit --no-fund --loglevel=error
)

REM Ensure axios is installed for API calls
echo Ensuring axios is installed...
call npm install axios --save --force --no-audit --no-fund --loglevel=error

REM Check if react-scripts exists
if not exist "node_modules\.bin\react-scripts.cmd" (
    echo react-scripts not found. Installing react-scripts...
    call npm install react-scripts --force --no-audit --no-fund --loglevel=error
)

cd ..

REM Set environment variables for the React app
set "PORT=3000"
set "REACT_APP_API_URL=http://localhost:5000/api"

REM Start the API server in a separate window
echo Starting API server...
start cmd /k "python api_server.py --host localhost --port 5000 --debug --load-sample-data"

REM Wait a moment for the API server to start
echo Waiting for API server to start...
timeout /t 5 /nobreak > nul

REM Start the frontend server in a separate window
echo Starting frontend server...
cd frontend
start cmd /k "npm start"
cd ..

echo.
echo Web UI is now running:
echo API server: http://localhost:5000/api
echo Frontend: http://localhost:3000
echo.
echo Press any key to shut down the servers when done...
pause

REM When the user presses a key, terminate the servers
echo Shutting down servers...
taskkill /f /im node.exe > nul 2>&1
taskkill /f /im python.exe > nul 2>&1
echo Servers shut down.
