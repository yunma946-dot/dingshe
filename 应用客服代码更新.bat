@echo off
setlocal
cd /d "%~dp0"

set "PYTHON_CMD=python"
where py >nul 2>nul && set "PYTHON_CMD=py"

where %PYTHON_CMD% >nul 2>nul
if errorlevel 1 (
  echo Python was not found.
  goto :error
)

%PYTHON_CMD% -u apply_chat_site1.py
if errorlevel 1 goto :error

echo.
echo Chat code update completed. Preview dist\index.html before uploading.
pause
exit /b 0

:error
echo.
echo Chat code update failed. No Excel or content data was replaced.
pause
exit /b 1
