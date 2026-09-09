@echo off
chcp 65001 >nul
echo Haftalik otomatik gorev siliniyor...
schtasks /Delete /TN "LeadRadar Lead Avcisi" /F
echo.
pause
