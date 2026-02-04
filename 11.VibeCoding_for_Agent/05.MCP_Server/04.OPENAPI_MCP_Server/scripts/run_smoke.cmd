@echo off
setlocal
set "VENV_DIR=C:\Users\skyop\jaeho_template\dotenv_windows"
set "VENV_PYTHON=%VENV_DIR%\Scripts\python.exe"
set "PATH=%VENV_DIR%\Scripts;%PATH%"
set "VIRTUAL_ENV=%VENV_DIR%"
uv run --active --no-sync -p "%VENV_PYTHON%" python scripts/stdio_smoke.py
endlocal
