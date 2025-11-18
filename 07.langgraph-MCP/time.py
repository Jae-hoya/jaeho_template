from mcp.server.fastmcp import FastMCP
from datetime import datetime
import pytz
from typing import Optional

timezone = "Asia/Seoul"
tz = pytz.timezone(timezone)

current_time = datetime.now(tz)

formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S %Z")

print(f"Current time in {timezone} is: {formatted_time}" )
