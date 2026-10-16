@echo off
echo Starting MediLoop Application (Backend + Frontend)...
start "MediLoop Backend Server" cmd /k "cd /d %~dp0backend && .venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 3
start "MediLoop Flutter Web" cmd /k "cd /d %~dp0 && flutter run -d chrome"
echo Both Backend and Frontend are launching!
