@echo off
title Smart Webcam Intruder Security System
color 0A
echo ========================================================
echo       STARTING SMART WEBCAM INTRUDER SECURITY SYSTEM
echo ========================================================
echo.
cd /d "%~dp0"

echo [1/2] Checking Dependencies...
python -m pip install opencv-python numpy requests >nul 2>&1

echo [2/2] Launching Security Camera...
python intruder_detector.py

pause
