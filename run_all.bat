@echo off
title VaxKavach - All-in-One Launcher
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_all.ps1 %*
pause
