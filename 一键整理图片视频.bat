@echo off
setlocal
cd /d "%~dp0"

if not exist "tools\rename_media.ps1" (
  echo Missing tools\rename_media.ps1
  goto :error
)

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\rename_media.ps1"
if errorlevel 1 goto :error

echo.
echo Media file names are ready. Run the site update next.
pause
exit /b 0

:error
echo.
echo Media rename was not completed. Check the message above.
pause
exit /b 1
