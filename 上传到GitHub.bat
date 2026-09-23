@echo off
setlocal
cd /d "%~dp0"

set "PYTHON_CMD=python"
where py >nul 2>nul && set "PYTHON_CMD=py"

where git >nul 2>nul
if errorlevel 1 (
  echo Git was not found. Please install Git for Windows first.
  goto :error
)

git rev-parse --is-inside-work-tree >nul 2>nul
if errorlevel 1 (
  echo This folder is not connected to a Git repository.
  goto :error
)

git add -A
git diff --cached --quiet
if not errorlevel 1 (
  echo No new changes were found. Nothing needs to be uploaded.
  goto :done
)

git commit -m "Update Dingshe website"
if errorlevel 1 goto :error
git push
if errorlevel 1 goto :error

echo.
echo Upload to GitHub completed.
echo Waiting before submitting changed URLs to IndexNow...
timeout /t 45 /nobreak >nul
%PYTHON_CMD% tools\submit_indexnow.py
if errorlevel 1 echo IndexNow was not submitted. You can try again later.
goto :done

:error
echo.
echo Upload was not completed. Keep this window open and check the message above.
pause
exit /b 1

:done
pause
exit /b 0
