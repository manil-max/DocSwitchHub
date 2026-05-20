@echo off
REM DocSwitch Hub - Fixed Build Script
REM This version fixes Python PATH issues

setlocal enabledelayedexpansion

cd /d "%~dp0"

echo ============================================
echo DocSwitch Hub - Build Process (FIXED)
echo ============================================
echo.

REM Try to find Python
echo [0/3] Locating Python...

REM Method 0: Check virtual environment first
if exist "%~dp0venv\Scripts\python.exe" (
    set PYTHON_PATH="%~dp0venv\Scripts\python.exe"
    goto :found_python
)

REM Method 1: Windows Registry
for /f "tokens=2*" %%A in ('reg query "HKLM\SOFTWARE\Python\PythonCore" /s 2^>nul ^| findstr InstallPath') do (
    set PYTHON_PATH=%%B\python.exe
    goto :found_python
)

REM Method 2: Try common locations
for %%P in (
    "C:\Python311\python.exe"
    "C:\Python310\python.exe"
    "C:\Python39\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    "%PROGRAMFILES%\Python311\python.exe"
    "%PROGRAMFILES%\Python310\python.exe"
) do (
    if exist %%P (
        set PYTHON_PATH=%%P
        goto :found_python
    )
)

REM Method 3: Try where command
for /f "tokens=*" %%i in ('where python.exe 2^>nul') do (
    set PYTHON_PATH=%%i
    goto :found_python
)

echo ERROR: Python not found!
echo.
echo Solutions:
echo 1. Install Python from https://www.python.org/downloads/
echo 2. Make sure to check "Add Python to PATH" during installation
echo 3. Restart this script after installation
echo.
pause
exit /b 1

:found_python
echo Found Python: %PYTHON_PATH%
echo.

REM Get pip path
for /f "tokens=*" %%i in ('%PYTHON_PATH% -m pip --version 2^>nul') do (
    echo Found pip: %%i
)

REM Install/Upgrade pip first
echo.
echo [1/4] Updating pip...
%PYTHON_PATH% -m pip install --upgrade pip >nul 2>&1

REM Install PyInstaller
echo [2/4] Installing PyInstaller...
%PYTHON_PATH% -m pip install pyinstaller >nul 2>&1

if errorlevel 1 (
    echo ERROR: Failed to install PyInstaller!
    echo.
    echo Try running this first:
    echo   python -m pip install --upgrade pip
    echo.
    pause
    exit /b 1
)

REM Build app.exe
echo [3/4] Building app.exe with PyInstaller...
%PYTHON_PATH% -m PyInstaller --noconfirm build.spec

if errorlevel 1 (
    echo ERROR: PyInstaller build failed!
    pause
    exit /b 1
)

REM Prepare installer
echo [4/4] Preparing installer...
if exist "installer\AppFiles\" rmdir /s /q "installer\AppFiles\"
mkdir "installer\AppFiles\"
xcopy "dist\DocSwitch" "installer\AppFiles\" /E /I /Y >nul

REM Find Inno Setup
echo.
echo ============================================
echo Building installer with Inno Setup...
echo ============================================

for /f "tokens=2*" %%a in ('reg query "HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall\Inno Setup 6" /v "InstallLocation" 2^>nul') do set INNO_PATH=%%b

if not defined INNO_PATH (
    for /f "tokens=2*" %%a in ('reg query "HKLM\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Inno Setup 6" /v "InstallLocation" 2^>nul') do set INNO_PATH=%%b
)

if not defined INNO_PATH (
    echo ERROR: Inno Setup 6 not found!
    echo.
    echo Please install from: https://jrsoftware.org/isdl.php
    echo.
    pause
    exit /b 1
)

set ISCC=!INNO_PATH!\ISCC.exe

if not exist "!ISCC!" (
    echo ERROR: ISCC.exe not found at !ISCC!
    echo.
    pause
    exit /b 1
)

echo Compiling setup with: !ISCC!
"!ISCC!" /O"installer\Output" "installer\setup.iss"

if errorlevel 1 (
    echo ERROR: Installer compilation failed!
    pause
    exit /b 1
)

echo.
echo ============================================
echo Build Successful!
echo ============================================
echo Installer location: installer\Output\DocSwitchHub_Setup_v*.exe
echo.
pause
