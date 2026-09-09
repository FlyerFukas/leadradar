@echo off
chcp 65001 >nul
cd /d "%~dp0.."
echo ============================================================
echo  LeadRadar - Haftalik otomatik calistirma kurulumu
echo  Her Pazartesi saat 09:00'da tarama yapilacak.
echo  (Bilgisayar o saatte acik olmalidir.)
echo ============================================================
echo.
powershell -ExecutionPolicy Bypass -File "haftalik_zamanlama.ps1"
echo.
pause
