"""
MCP Server that exposes weather tools via the Model Context Protocol.

This server can be used by any MCP-compatible client (Claude Desktop, 
your Chainlit app, or other MCP clients).

Run with: python mcp_server.py
"""

import os
import asyncio
import httpx
from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Load environment variables
load_dotenv()

# Create the MCP server
server = Server("weather-tools")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """
    List all available tools.
    This is called by MCP clients to discover what tools are available.
    """
    return [
        Tool(
            name="get_weather",
            description="Get the current weather for a city. Provides temperature, conditions, humidity, and wind speed.",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city name (e.g., 'London', 'Tokyo', 'New York')"
                    }
                },
                "required": ["city"]
            }
        ),
        Tool(
            name="get_forecast",
            description="Get the weather forecast for the next 3 days for a city.",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city name"
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days (1-3)",
                        "default": 3
                    }
                },
                "required": ["city"]
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """
    Handle tool calls from MCP clients.
    """
    api_key = os.getenv("WEATHER_API_KEY")
    
    if not api_key or api_key == "your_weather_api_key_here":
        return [TextContent(
            type="text",
            text="Error: WEATHER_API_KEY not configured in .env file"
        )]
    
    if name == "get_weather":
        result = await fetch_current_weather(api_key, arguments.get("city", ""))
        return [TextContent(type="text", text=result)]
        
    elif name == "get_forecast":
        city = arguments.get("city", "")
        days = min(arguments.get("days", 3), 3)  # Max 3 days on free tier
        result = await fetch_forecast(api_key, city, days)
        return [TextContent(type="text", text=result)]
    
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def fetch_current_weather(api_key: str, city: str) -> str:
    """Fetch current weather from WeatherAPI."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://api.weatherapi.com/v1/current.json",
                params={"key": api_key, "q": city, "aqi": "no"},
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            
            location = data["location"]["name"]
            country = data["location"]["country"]
            temp_c = data["current"]["temp_c"]
            temp_f = data["current"]["temp_f"]
            condition = data["current"]["condition"]["text"]
            humidity = data["current"]["humidity"]
            wind_kph = data["current"]["wind_kph"]
            
            return f"""Weather for {location}, {country}:
🌡️ Temperature: {temp_c}°C ({temp_f}°F)
☁️ Condition: {condition}
💧 Humidity: {humidity}%
💨 Wind: {wind_kph} km/h"""
            
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 400:
            return f"Could not find weather for '{city}'. Check the city name."
        return f"API error: {e}"
    except Exception as e:
        return f"Error: {e}"


async def fetch_forecast(api_key: str, city: str, days: int) -> str:
    """Fetch weather forecast from WeatherAPI."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://api.weatherapi.com/v1/forecast.json",
                params={"key": api_key, "q": city, "days": days, "aqi": "no"},
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            
            location = data["location"]["name"]
            country = data["location"]["country"]
            
            forecast_text = f"📅 {days}-Day Forecast for {location}, {country}:\n\n"
            
            for day in data["forecast"]["forecastday"]:
                date = day["date"]
                max_c = day["day"]["maxtemp_c"]
                min_c = day["day"]["mintemp_c"]
                condition = day["day"]["condition"]["text"]
                rain_chance = day["day"]["daily_chance_of_rain"]
                
                forecast_text += f"**{date}**\n"
                forecast_text += f"  🌡️ {min_c}°C - {max_c}°C\n"
                forecast_text += f"  ☁️ {condition}\n"
                forecast_text += f"  🌧️ Rain chance: {rain_chance}%\n\n"
            
            return forecast_text
            
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 400:
            return f"Could not find forecast for '{city}'."
        return f"API error: {e}"
    except Exception as e:
        return f"Error: {e}"


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
