@echo off
REM Robust startup batch with deterministic debugging output.
REM Writes a stable log file `logs\mcp_server_debug.log` to avoid locale/time parsing issues.
SETLOCAL ENABLEDELAYEDEXPANSION
SET REPO_DIR=%~dp0
cd /d "%REPO_DIR%"

REM Prefer a .venv inside the repo; fall back to system python.
IF EXIST "%REPO_DIR%\.venv\Scripts\python.exe" (
    SET "PY_EXE=%REPO_DIR%\.venv\Scripts\python.exe"
) ELSE IF EXIST "%REPO_DIR%\\.venv\\Scripts\\python.exe" (
    SET "PY_EXE=%REPO_DIR%\\.venv\\Scripts\\python.exe"
) ELSE (
    SET "PY_EXE=python"
)

REM Ensure logs directory exists
IF NOT EXIST "%REPO_DIR%logs" mkdir "%REPO_DIR%logs"
REM Create a timestamped logfile to avoid collisions when multiple runs start concurrently.
for /f "usebackq delims=" %%T in (`powershell -NoProfile -Command "(Get-Date).ToString('yyyyMMdd_HHmmss')"`) do set "TS=%%T"
SET "LOGFILE=%REPO_DIR%logs\mcp_server_%TS%.log"

(
    echo ===== MCP server start attempt =====
    echo Timestamp: %DATE% %TIME%
    echo TimestampISO: %TS%
    echo User: %USERNAME%
    echo Repo dir: %REPO_DIR%
    echo Current dir: %CD%
    echo Python candidate: %PY_EXE%
    echo ===== python info =====
) > "%LOGFILE%"

REM Log python version (if available)
%PY_EXE% --version >> "%LOGFILE%" 2>&1 || echo python --version failed >> "%LOGFILE%"

REM List repo contents for debugging
dir "%REPO_DIR%" >> "%LOGFILE%" 2>&1

REM Ensure Python can import modules from the repo's `src` directory when uvicorn imports `src.main`.
SET "PYTHONPATH=%REPO_DIR%src"
echo PYTHONPATH=%PYTHONPATH% >> "%LOGFILE%"
echo Running (background): "%PY_EXE%" -m uvicorn src.main:app --host 127.0.0.1 --port 8000 >> "%LOGFILE%"
REM Start uvicorn without leaving a visible console window. Use start /B to run detached in background and redirect output to the log.
start "mcp-server" /B "%PY_EXE%" -m uvicorn src.main:app --host 127.0.0.1 --port 8000 --log-level info >> "%LOGFILE%" 2>&1
if errorlevel 1 (
    echo Failed to start background process >> "%LOGFILE%"
) else (
    echo Background uvicorn start requested >> "%LOGFILE%"
)
echo Log file for this run: %LOGFILE%

ENDLOCAL
EXIT /B %ERRORLEVEL%
