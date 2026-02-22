@echo off
title Dictionary Forge - First Time Setup
echo ---------------------------------------------------
echo Installing Dictionary Forge Requirements...
echo ---------------------------------------------------

:: 1. Check if uv is installed
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo [1/2] uv not found. Downloading and installing uv...
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    :: Add uv to current session path so we can use it immediately
    set "PATH=%USERPROFILE%\.cargo\bin;%PATH%"
) else (
    echo [1/2] uv is already installed.
)

:: 2. Sync dependencies
echo [2/2] Preparing the application environment...
uv sync

echo ---------------------------------------------------
echo SETUP COMPLETE!
echo You can now close this window and run 'run.bat'
echo ---------------------------------------------------
pause