from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Weather")

@mcp.tool()
async def get_current_weather(location: str) -> str:
    """Get the current weather for a location"""
    return f"The current weather in {location} is sunny"

if __name__ == "__main__":
    mcp.run(transport="streamable-http")