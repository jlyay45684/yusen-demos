@echo off
cd /d %~dp0

echo =========================================
echo   Yusen AI Decision Intelligence Console
echo =========================================
echo.

echo Checking Python environment...
python --version >nul 2>&1

IF %ERRORLEVEL% NEQ 0 (
    echo Python not detected.
    echo Please install Python first.
    pause
    exit
)

echo Python detected.
echo.

echo Installing required packages...
python -m pip install --upgrade pip
python -m pip install streamlit pandas plotly

echo.
echo Starting Streamlit Dashboard...
echo.

start http://localhost:8501

python -m streamlit run app.py

pause
