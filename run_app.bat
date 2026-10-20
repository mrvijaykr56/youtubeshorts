@echo off
echo Starting YouTube Shorts Studio...
echo.

echo Starting Flask Backend Server...
start "Shorts Studio Backend" /D "%~dp0backend" "C:\Users\vijay\AppData\Local\Programs\Python\Python311\python.exe" app.py

echo Starting Vite Frontend Server...
start "Shorts Studio Frontend" /D "%~dp0frontend" cmd /c "npm run dev"

echo.
echo Both applications have been launched.
pause
