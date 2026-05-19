@echo off
echo ============================================
echo   DocSwitch Hub - Setting up dependencies
echo ============================================
echo.

cd /d "%~dp0"

echo [1/3] Creating Python virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo [2/3] Installing Python packages (this may take a few minutes)...
call venv\Scripts\pip.exe install -r requirements.txt --quiet
if errorlevel 1 (
    echo ERROR: Failed to install some packages.
    pause
    exit /b 1
)

echo [3/3] Setup complete!
echo.
echo ============================================
echo   DocSwitch Hub is ready to use!
echo   Launch it from the Desktop or Start Menu.
echo ============================================
pause
