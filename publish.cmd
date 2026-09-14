@echo off
setlocal
cd /d "%~dp0"

REM ============================================================
REM  One-click publish.
REM  Double-click this file to push your changes to GitHub.
REM  The live site refreshes about 1 minute later.
REM
REM  ASCII-only on purpose: cmd.exe reads .cmd files with the
REM  system ANSI codepage on zh-CN Windows, so Chinese text here
REM  would get mangled and could break the script.
REM ============================================================

echo.
echo   Publishing to GitHub ...
echo.

git add -A
git commit -m "update: %date% %time%"
git push

echo.
echo   ------------------------------------------------------
echo   Done. The live site refreshes in about 1 minute.
echo   Check progress at:  GitHub repo - Actions tab
echo   ------------------------------------------------------
echo.
pause
