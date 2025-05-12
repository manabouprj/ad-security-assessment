@echo off
echo Starting AD Security Assessment Tool...

echo Installing required Python packages...
pip install flask flask-cors werkzeug
pip install -r requirements.txt

echo Starting API server with sample data...
start cmd /k python run_api.py --load-sample-data

echo Starting frontend...
cd frontend
start cmd /k npm start

echo.
echo Services started:
echo - API server: http://localhost:5000
echo - Frontend: http://localhost:3000
echo.
echo You can now access the application at http://localhost:3000
