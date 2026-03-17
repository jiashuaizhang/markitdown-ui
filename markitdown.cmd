@echo off
setlocal enabledelayedexpansion

REM Always run from this folder
cd /d "%~dp0"

if not exist ".\Scripts\python.exe" (
  echo [ERROR] venv not found: ".\Scripts\python.exe"
  echo        Please create/restore the venv in this workspace root.
  exit /b 1
)

echo Using venv python:
".\Scripts\python.exe" -c "import sys; print(sys.executable)"

echo.
echo Installing/updating requirements...
".\Scripts\python.exe" -m pip install -r "requirements.txt"
if errorlevel 1 (
  echo [ERROR] pip install failed.
  exit /b 1
)

echo.
echo Starting Streamlit UI...
echo Close this window or press Ctrl+C to stop.
".\Scripts\python.exe" -m streamlit run "app.py"

