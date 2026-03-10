@echo off
cd /d %~dp0

echo ================================
echo Yusen AI Decision Intelligence
echo Starting Streamlit Dashboard
echo ================================

python -m streamlit run app.py

pause
