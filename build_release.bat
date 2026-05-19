@echo off
REM DocSwitch Hub - Build Script
REM Bu script DocSwitch Hub'ı dağıtım için hazırlar
REM (1) PyInstaller ile app.exe oluşturur
REM (2) LibreOffice standalone kurulumunu hazırlar
REM (3) Inno Setup installer'ını derler

cd /d "%~dp0"

echo ============================================
echo DocSwitch Hub - Build Process
echo ============================================
echo.

REM Adım 1: PyInstaller kontrol et
echo [1/3] Checking PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

REM Adım 2: app.exe oluştur
echo [2/3] Building app.exe with PyInstaller...
pyinstaller --noconfirm build.spec
if errorlevel 1 (
    echo ERROR: PyInstaller build failed!
    pause
    exit /b 1
)

REM Adım 3: dist klasöründen installer klasörüne kopyala
echo [3/3] Preparing installer...
if exist "installer\AppFiles\" rmdir /s /q "installer\AppFiles\"
mkdir "installer\AppFiles\"
xcopy "dist\DocSwitch" "installer\AppFiles\" /E /I /Y

REM Inno Setup ile derle
echo.
echo ============================================
echo Building installer with Inno Setup...
echo ============================================

REM Inno Setup'ı bul
for /f "tokens=2*" %%a in ('reg query "HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall\Inno Setup 6" /v "InstallLocation" 2^>nul') do set INNO_PATH=%%b

if not defined INNO_PATH (
    echo ERROR: Inno Setup 6 not found!
    echo Please install from: https://jrsoftware.org/isdl.php
    pause
    exit /b 1
)

set ISCC=%INNO_PATH%\ISCC.exe

if not exist "%ISCC%" (
    echo ERROR: ISCC.exe not found at %ISCC%
    pause
    exit /b 1
)

REM Setup.iss derle
echo Compiling setup with: %ISCC%
"%ISCC%" /O"installer\Output" "installer\setup.iss"

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
