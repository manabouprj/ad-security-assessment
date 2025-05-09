@echo off
echo Starting AD Security Assessment Web UI
echo =====================================
echo.

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

REM Start the API server in a new window
echo Starting API server on port 5000...
start cmd /k "python api_server.py --host localhost --port 5000 --debug --load-sample-data"

REM Wait a moment for the API server to start
echo Waiting for API server to start...
timeout /t 3 /nobreak > nul

REM Start the frontend server in a new window
echo Starting frontend server on port 3000...
cd frontend

REM Check if node_modules exists
echo Checking if node_modules exists...
if not exist "node_modules\" (
    echo node_modules not found. Installing dependencies...
    call npm install --force --no-audit --no-fund --loglevel=error
    if %ERRORLEVEL% neq 0 (
        echo Warning: Failed to install all frontend dependencies. Trying alternative approach...
        
        REM Try installing core dependencies one by one
        echo Installing react and core dependencies...
        call npm install react react-dom react-scripts react-router-dom --force --no-audit --no-fund --loglevel=error
        
        echo Installing bootstrap dependencies...
        call npm install bootstrap react-bootstrap --force --no-audit --no-fund --loglevel=error
        
        echo Installing chart dependencies...
        call npm install chart.js react-chartjs-2 --force --no-audit --no-fund --loglevel=error
        
        echo Installing react-bootstrap-icons...
        call npm install react-bootstrap-icons --save --force --no-audit --no-fund --loglevel=error
        
        echo Installing axios...
        call npm install axios --save --force --no-audit --no-fund --loglevel=error
    )
)

REM Check if react-scripts exists
if not exist "node_modules\.bin\react-scripts.cmd" (
    echo react-scripts not found. Installing react-scripts...
    call npm install react-scripts --force --no-audit --no-fund --loglevel=error
)

REM Set environment variables for the React app
set "PORT=3000"
set "REACT_APP_API_URL=http://localhost:5000/api"

REM Start the frontend server
echo Starting React development server...
start cmd /k "npm start"
cd ..

echo.
echo Web UI should now be running:
echo API server: http://localhost:5000/api
echo Frontend: http://localhost:3000
echo.
echo If the web UI doesn't open automatically, please open http://localhost:3000 in your browser.
echo.
echo Press Ctrl+C to exit this script (the servers will continue running in their own windows).
echo.

REM Keep the script running until Ctrl+C
pause
