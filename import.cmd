@echo off
setlocal
cd /d "%~dp0"

REM ============================================================
REM  One-click import.
REM
REM  Steps:
REM    1. Export your articles from Feishu as Markdown
REM       (if the doc has images, Feishu gives you a .zip)
REM    2. Drop the .zip / .md files into the "inbox" folder
REM    3. Double-click this file
REM
REM  ASCII-only on purpose: cmd.exe reads .cmd files using the
REM  system ANSI codepage on zh-CN Windows, so Chinese text here
REM  would get mangled and could break the script.
REM ============================================================

echo.
echo   ==========================================================
echo    Import articles from the "inbox" folder
echo   ==========================================================
echo.
echo    Which section should they go to?
echo.
echo      1 = Writeups   (CTF writeups)
echo      2 = Notes      (reverse-engineering notes)
echo      3 = Musings    (essays / daily posts)
echo.

set "CHOICE="
set /p CHOICE=Enter 1 / 2 / 3  (Enter = 3):

if "%CHOICE%"=="1" set "SECTION=writeups"
if "%CHOICE%"=="2" set "SECTION=notes"
if "%CHOICE%"=="3" set "SECTION=musings"
if not defined SECTION set "SECTION=musings"

echo.
echo    Section: %SECTION%
echo.

uv run python _import.py %SECTION%

echo.
pause
