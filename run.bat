@echo off
set VENV_DIR=venv

echo =====================================
echo Setting up environment
echo =====================================

if not exist "sd-venv\Scripts\activate.bat" (
    python -m venv sd-venv
)

echo Activate virtual environment
call sd-venv\Scripts\activate

echo.
echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Installing PyTorch (CUDA build)...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128

echo.
echo Installing other requirements...
pip install -r requirements.txt

echo.
echo Starting app...
python main.py

pause