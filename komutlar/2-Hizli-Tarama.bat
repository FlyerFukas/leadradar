@echo off
chcp 65001 >nul
cd /d "%~dp0.."
echo ============================================================
echo  LeadRadar - Hizli tarama (Berlin haftalik rotasyon)
echo  Cikti: output klasorune PDF + JSON
echo ============================================================
echo.
py run.py
echo.
echo Bitti. Rapor "output" klasorunde.
pause
