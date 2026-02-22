"""
Weather MCP Server
Provides global weather data via Open-Meteo API (free, no API key required).
"""

import sys
import httpx
from typing import Any
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather")

GEOCODING_API = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_API = "https://api.open-meteo.com/v1/forecast"

WMO_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Foggy", 48: "Icy fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow", 77: "Snow grains",
    80: "Slight showers", 81: "Moderate showers", 82: "Violent showers",
    85: "Slight snow showers", 86: "Heavy snow showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Thunderstorm with heavy hail",
}


async def geocode(location: str) -> dict[str, Any] | None:
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(
                GEOCODING_API,
                params={"name": location, "count": 1, "language": "en", "format": "json"},
                timeout=10.0,
            )
            r.raise_for_status()
            results = r.json().get("results")
            if results:
                loc = results[0]
                return {
                    "name": loc["name"],
                    "country": loc.get("country", ""),
                    "latitude": loc["latitude"],
                    "longitude": loc["longitude"],
                }
        except Exception as e:
            print(f"Geocoding error: {e}", file=sys.stderr)
    return None


@mcp.tool()
async def get_current_weather(location: str) -> str:
    """Get current weather conditions for any city or location worldwide.

    Args:
        location: City name or location (e.g. 'London', 'Tokyo', 'Mumbai', 'New York')
    """
    coords = await geocode(location)
    if not coords:
        return f"Location not found: '{location}'. Try a different city name."

    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(
                WEATHER_API,
                params={
                    "latitude": coords["latitude"],
                    "longitude": coords["longitude"],
                    "current": (
                        "temperature_2m,relative_humidity_2m,apparent_temperature,"
                        "weather_code,wind_speed_10m,wind_direction_10m,precipitation"
                    ),
                    "timezone": "auto",
                    "wind_speed_unit": "kmh",
                },
                timeout=10.0,
            )
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            return f"Failed to fetch weather: {e}"

    c = data["current"]
    desc = WMO_CODES.get(c["weather_code"], "Unknown")
    return (
        f"Current Weather — {coords['name']}, {coords['country']}\n"
        f"{'─' * 45}\n"
        f"Condition    : {desc}\n"
        f"Temperature  : {c['temperature_2m']}°C (feels like {c['apparent_temperature']}°C)\n"
        f"Humidity     : {c['relative_humidity_2m']}%\n"
        f"Wind         : {c['wind_speed_10m']} km/h\n"
        f"Precipitation: {c['precipitation']} mm\n"
        f"Updated      : {c['time']}"
    )


@mcp.tool()
async def get_forecast(location: str, days: int = 7) -> str:
    """Get a multi-day weather forecast for any location worldwide.

    Args:
        location: City name or location (e.g. 'Paris', 'Sydney', 'Nairobi')
        days: Number of forecast days, 1–16 (default 7)
    """
    days = max(1, min(days, 16))
    coords = await geocode(location)
    if not coords:
        return f"Location not found: '{location}'."

    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(
                WEATHER_API,
                params={
                    "latitude": coords["latitude"],
                    "longitude": coords["longitude"],
                    "daily": (
                        "temperature_2m_max,temperature_2m_min,weather_code,"
                        "precipitation_sum,precipitation_probability_max,wind_speed_10m_max"
                    ),
                    "timezone": "auto",
                    "forecast_days": days,
                    "wind_speed_unit": "kmh",
                },
                timeout=10.0,
            )
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            return f"Failed to fetch forecast: {e}"

    d = data["daily"]
    lines = [
        f"{days}-Day Forecast — {coords['name']}, {coords['country']}",
        "─" * 75,
        f"{'Date':<12} {'Condition':<26} {'High':>6} {'Low':>6} {'Rain%':>6} {'Wind':>10}",
        "─" * 75,
    ]
    for i in range(len(d["time"])):
        desc = WMO_CODES.get(d["weather_code"][i], "Unknown")
        lines.append(
            f"{d['time'][i]:<12} {desc:<26} "
            f"{d['temperature_2m_max'][i]:>5}°C {d['temperature_2m_min'][i]:>5}°C "
            f"{d['precipitation_probability_max'][i]:>5}% "
            f"{d['wind_speed_10m_max'][i]:>7} km/h"
        )
    return "\n".join(lines)


@mcp.tool()
async def search_location(query: str) -> str:
    """Search for a location by name and return matching results with coordinates.
    Use this when unsure about a city name before calling weather tools.

    Args:
        query: Partial or full location name to search
    """
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(
                GEOCODING_API,
                params={"name": query, "count": 5, "language": "en", "format": "json"},
                timeout=10.0,
            )
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            return f"Search failed: {e}"

    results = data.get("results")
    if not results:
        return f"No locations found for '{query}'."

    lines = [f"Locations matching '{query}':", "─" * 40]
    for loc in results:
        lines.append(
            f"- {loc['name']}, {loc.get('admin1', '')}, {loc.get('country', '')} "
            f"(lat: {loc['latitude']}, lon: {loc['longitude']})"
        )
    return "\n".join(lines)


@mcp.resource("weather://current/{location}")
async def weather_resource(location: str) -> str:
    """Read-only resource: current weather snapshot for a location."""
    return await get_current_weather(location)


@mcp.prompt()
def weather_report_prompt(location: str) -> str:
    """Reusable prompt template: ask for a full weather briefing for a location."""
    return (
        f"Give me a full weather briefing for {location}. "
        "Include current conditions and a 7-day forecast. "
        "Highlight any significant weather events or warnings."
    )


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
