@echo off
set VENV_DIR=venv

echo =====================================
echo Setting up environment
echo =====================================

if not exist "sd-venv\Scripts\activate.bat" (
    python -m venv %VENV_DIR%
)

echo Activate virtual environment
call %VENV_DIR%\Scripts\activate

echo.
echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Installing PyTorch (CPU build)...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

echo.
echo Installing other requirements...
pip install -r requirements.txt

echo.
echo Starting app...
python main.py

pause