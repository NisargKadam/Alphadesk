import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from mcp.server.fastmcp import FastMCP
from app.tools import get_price_history, get_quotes

mcp = FastMCP("alphadesk")

mcp.tool()(get_price_history.func)
mcp.tool()(get_quotes.func)

if __name__ == "__main__":
    mcp.run() #stdio: JSON RPC over stdin/stdout, one client per process.

