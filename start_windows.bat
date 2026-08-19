@echo off
setlocal
cd /d "%~dp0"
chcp 65001 >nul

echo ==============================================
echo EBS Live Bridge v2.1 - Baslatiliyor
echo ==============================================

where py >nul 2>nul
if %errorlevel%==0 (
  py -3 app.py
) else (
  python app.py
)

if errorlevel 1 (
  echo.
  echo Uygulama hata ile kapandi. Yukaridaki mesaji kontrol edin.
  pause
)
endlocal
