@echo off
chcp 65001 >nul
cd /d "%~dp0.."
echo Sistem rehberi PDF'i yeniden uretiliyor...
py make_system_guide.py
echo.
echo Rehber: docs\LeadRadar_Sistem_Rehberi.pdf
pause
