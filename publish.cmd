@echo off
setlocal
cd /d "%~dp0"

REM ============================================================
REM  One-click publish: commit everything, then push to GitHub.
REM  The live site refreshes about 1 minute later.
REM
REM  ASCII-only on purpose -- cmd.exe reads .cmd files with the
REM  system ANSI codepage on zh-CN Windows, so Chinese text in
REM  this file would get mangled and could break the script.
REM ============================================================


REM ---- 1. Locate git -----------------------------------------
REM  Why this block exists: this machine has no system-wide
REM  Git for Windows installed, and no "git" on PATH. Without
REM  the lookup below the script used to run git, get
REM  "'git' is not recognized", fail every command -- and then
REM  still print "Done", which was very misleading.
REM  Cherry Studio ships its own copy of git, so fall back to
REM  that and nothing has to be installed.
set "GIT="

for /f "delims=" %%i in ('where git 2^>nul') do (
    if not defined GIT set "GIT=%%i"
)

if not defined GIT if exist "C:\Program Files\Git\cmd\git.exe" set "GIT=C:\Program Files\Git\cmd\git.exe"
if not defined GIT if exist "C:\Program Files (x86)\Git\cmd\git.exe" set "GIT=C:\Program Files (x86)\Git\cmd\git.exe"
if not defined GIT if exist "%LOCALAPPDATA%\Programs\Git\cmd\git.exe" set "GIT=%LOCALAPPDATA%\Programs\Git\cmd\git.exe"
if not defined GIT if exist "D:\cherry studio\resources\app.asar.unpacked\resources\binaries\win32-x64\git\cmd\git.exe" set "GIT=D:\cherry studio\resources\app.asar.unpacked\resources\binaries\win32-x64\git\cmd\git.exe"

if not defined GIT (
    echo.
    echo   [ERROR] git not found on this machine.
    echo.
    echo   Install it with:   winget install Git.Git -e
    echo   Then run this file again.
    echo.
    pause
    exit /b 1
)


REM ---- 2. Sanity check: are we in a git repo? ----------------
if not exist ".git" (
    echo.
    echo   [ERROR] no .git folder in:
    echo   %CD%
    echo   This script must sit next to hugo.toml.
    echo.
    pause
    exit /b 1
)


echo.
echo   git   : %GIT%
echo   repo  : %CD%
echo.
echo   Publishing to GitHub ...
echo.

"%GIT%" add -A

"%GIT%" commit -m "update: %date% %time%"

"%GIT%" push
if errorlevel 1 goto failed

echo.
echo   ------------------------------------------------------
echo   Done. The live site refreshes in about 1 minute.
echo   Check progress at:  GitHub repo - Actions tab
echo   ------------------------------------------------------
echo.
pause
exit /b 0


:failed
echo.
echo   ------------------------------------------------------
echo   [ERROR] push failed -- nothing was published.
echo.
echo   The usual cause is a network reset while talking to
echo   GitHub. It is not a broken setup: just double-click
echo   this file again, it usually succeeds on the 2nd or
echo   3rd try.
echo.
echo   Your commit is already saved locally either way, so
echo   nothing is lost.
echo   ------------------------------------------------------
echo.
pause
exit /b 1
