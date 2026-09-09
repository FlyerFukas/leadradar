@echo off
chcp 65001 >nul
cd /d "%~dp0.."
echo ============================================================
echo  LeadRadar - Kontrol Paneli baslatiliyor...
echo  Tarayici otomatik acilacak: http://127.0.0.1:8765
echo  Kapatmak icin bu pencerede Ctrl+C
echo ============================================================
echo.
py panel.py
pause
