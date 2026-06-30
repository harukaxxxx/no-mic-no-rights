@echo off
chcp 65001 >nul 2>&1

echo === No mic, no rights ===
echo.

if not exist .env (
    echo Warning: .env file not found. Copying from .env.example...
    copy .env.example .env >nul
    echo Please edit .env and add your Discord bot token.
    echo.
)

echo Installing Python dependencies...
uv sync
if errorlevel 1 (
    echo Failed to install Python dependencies.
    pause
    exit /b 1
)

echo Installing frontend dependencies...
cd frontend
call npm install
if errorlevel 1 (
    echo Failed to install frontend dependencies.
    pause
    exit /b 1
)

echo Building frontend...
call npm run build
if errorlevel 1 (
    echo Failed to build frontend.
    pause
    exit /b 1
)
cd ..

echo.
echo Starting server...
for /f "tokens=2 delims==" %%a in ('findstr /b "PORT=" .env 2^>nul') do set PORT=%%a
if not defined PORT set PORT=8000

echo Access the web interface at: http://localhost:%PORT%
echo.

uv run python -m backend.main
