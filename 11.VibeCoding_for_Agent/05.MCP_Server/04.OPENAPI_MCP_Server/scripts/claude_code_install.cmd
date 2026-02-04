@echo off
setlocal
set "VENV_PYTHON=C:\Users\skyop\jaeho_template\dotenv_windows\Scripts\python.exe"
set "SERVER_SCRIPT=C:\Users\skyop\jaeho_template\11.VibeCoding_for_Agent\05.MCP_Server\04.OPENAPI_MCP_Server\src\server.py"
claude mcp add seoul-culture-events -- "%VENV_PYTHON%" "%SERVER_SCRIPT%"
endlocal
