@echo off
REM DataFlow launcher (Windows).
cd /d "%~dp0"

set PYTHON=python
if exist "runtime\python\python.exe" set PYTHON=runtime\python\python.exe

"%PYTHON%" -c "import nicegui" >nul 2>&1
if errorlevel 1 (
  echo DataFlow needs its dependencies. Installing them now...
  "%PYTHON%" -m pip install -r requirements.txt
)

"%PYTHON%" main.py
pause