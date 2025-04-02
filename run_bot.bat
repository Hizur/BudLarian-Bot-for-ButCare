@echo off
title BudCare Discord Bot
color 0A
echo ====================================
echo         BudCare Discord Bot         
echo ====================================
echo.

:start
echo Starting bot...
python bot.py
echo.
echo Bot stopped or crashed.
echo Restarting in 5 seconds...
timeout /t 5 /nobreak >nul
goto start
