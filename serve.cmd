@echo off
setlocal

REM ============================================================
REM  Local preview launcher.  Double-click this file.
REM
REM  Two things in here are deliberate -- please don't "simplify":
REM
REM  1) This file is ASCII-only.
REM     The zh-CN console codepage is GBK, but a file written by
REM     most editors is UTF-8. Chinese text in a .cmd therefore
REM     gets mis-parsed and can break the script outright.
REM
REM  2) The trailing backslash of %~dp0 is stripped.
REM     %~dp0 expands to "C:\path\to\blog\" INCLUDING the final
REM     backslash. Passing that as --source "%SITE%" produces
REM     --source "C:\path\to\blog\" where \" is read by Windows
REM     as an escaped quote. hugo then receives a broken path.
REM ============================================================

set "SITE=%~dp0"
set "SITE=%SITE:~0,-1%"

set "HUGO=%LOCALAPPDATA%\Microsoft\WinGet\Links\hugo.exe"

if not exist "%HUGO%" (
    for /f "delims=" %%i in ('dir /b /s "%LOCALAPPDATA%\Microsoft\WinGet\Packages\hugo.exe" 2^>nul') do set "HUGO=%%i"
)

if not exist "%HUGO%" (
    echo.
    echo   [ERROR] hugo.exe not found.
    echo   Install it with:  winget install Hugo.Hugo.Extended -e
    echo.
    pause
    exit /b 1
)

if not exist "%SITE%\hugo.toml" (
    echo.
    echo   [ERROR] hugo.toml not found in:
    echo   %SITE%
    echo.
    pause
    exit /b 1
)

echo.
echo   Site folder : %SITE%
echo   Hugo binary : %HUGO%
echo.
echo   Starting preview server...
echo   Open in browser:  http://localhost:1313/
echo.
echo   Keep this window OPEN while browsing. Press Ctrl+C to stop.
echo.

"%HUGO%" server --source "%SITE%" --buildDrafts --disableFastRender --navigateToChanged --port 1313

echo.
echo   Server stopped.
echo.
pause
