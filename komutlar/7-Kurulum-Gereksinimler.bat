@echo off
chcp 65001 >nul
cd /d "%~dp0.."
echo ============================================================
echo  LeadRadar - Gerekli Python paketleri kuruluyor
echo  (Sadece ilk kurulumda veya yeni bilgisayarda gerekir)
echo ============================================================
echo.
py -m pip install -r requirements.txt
echo.
echo Kurulum tamamlandi.
pause
