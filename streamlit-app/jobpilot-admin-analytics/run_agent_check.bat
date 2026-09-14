@echo off
setlocal
cd /d "%~dp0"
if not exist "venv\Scripts\python.exe" (
    echo Run install_requirements.bat first.
    pause
    exit /b 1
)
call venv\Scripts\activate.bat
echo JobPilot scheduler placeholder.
echo Configure an authorized job-search API in .env before enabling scheduled discovery.
python -c "from automation.agent_runner import load_jobs; print('Stored jobs:', len(load_jobs()))"
pause
