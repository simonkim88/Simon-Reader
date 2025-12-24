@echo off
echo Starting Simon-Reader...
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
pause
