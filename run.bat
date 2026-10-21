@echo off
cd /d "%~dp0"
start /min python -m streamlit run employee-leave-system.py
exit