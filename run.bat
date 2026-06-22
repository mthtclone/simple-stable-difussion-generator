@echo off
setlocal enabledelayedexpansion
cd /d %~dp0

set DEBUG=0

echo Checking for updates...
powershell -ExecutionPolicy Bypass -File updater.ps1

echo.
echo Setting up environment

if not exist "sd-venv\Scripts\activate.bat" (
    echo Creating venv...
    python -m venv sd-venv
)

echo Activating venv...
call sd-venv\Scripts\activate

echo.
echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Installing PyTorch...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128

echo.
echo Installing requirements...
pip install -r requirements.txt

echo.
echo Starting app...
if "%DEBUG%"=="1" (
    python main.py
) else (
    start "" pythonw main.py
    exit
)

pause