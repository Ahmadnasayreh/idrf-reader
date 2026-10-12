@echo off
rem Start IDRF Reader on Windows. Double-click this file, or run it from a terminal.
cd /d "%~dp0"

if not exist ".env" (
  copy ".env.example" ".env" >nul
  echo.
  echo  A settings file .env was created.
  echo  Open it, change ADMIN_PASSWORD, save it, then run this file again.
  echo.
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo Creating a Python environment, first time only...
  py -3 -m venv .venv 2>nul || python -m venv .venv
  if not exist ".venv\Scripts\python.exe" (
    echo Python 3.10 or newer was not found. Install it from python.org and tick "Add Python to PATH".
    pause
    exit /b 1
  )
)

".venv\Scripts\python.exe" -m pip install --quiet --upgrade pip
".venv\Scripts\python.exe" -m pip install --quiet -r requirements.txt
".venv\Scripts\python.exe" run.py
pause
