@echo off
echo Starting AD Security Assessment Web UI
echo =====================================
echo.

REM Start the API server in a new window
echo Starting API server on port 5000...
start cmd /k "python api_server.py --host localhost --port 5000 --debug --load-sample-data"

REM Wait a moment for the API server to start
echo Waiting for API server to start...
timeout /t 3 /nobreak > nul

REM Start the frontend server in a new window
echo Starting frontend server on port 3000...
cd frontend
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
