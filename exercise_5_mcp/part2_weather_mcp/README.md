# Part 2 — Building a Custom MCP Server and Client

This part shows how to build your own MCP server (global weather data) and a Python MCP client that connects to it using a local LLM via Ollama.

**Weather data**: Open-Meteo API — free, global coverage, no API key required.

---

## Concepts

| Concept | What it is |
|---|---|
| **MCP Server** | A process that exposes tools/resources/prompts over a standard protocol |
| **MCP Client** | A program that connects to an MCP server and calls its tools |
| **Tool** | A function the LLM can call (has side effects, returns data) |
| **Resource** | Read-only data the LLM can read (like a GET endpoint) |
| **Prompt** | A reusable prompt template registered on the server |
| **Transport** | How client and server communicate — `stdio` here (subprocess pipes) |

---

## Project Structure

```
part2_weather_mcp/
├── pyproject.toml       # uv project dependencies
├── .python-version      # pins Python 3.11
├── .env.example         # copy to .env and configure
├── weather_server.py    # MCP Server — exposes weather tools
└── mcp_client.py        # MCP Client — connects to server, uses Ollama LLM
```

---

## Setup

### 1. Install uv (if not already installed)

```bash
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Install Ollama and pull a model

Download Ollama from https://ollama.com and then:

```bash
ollama pull llama3.2
```

Models with good tool-calling support: `llama3.2`, `llama3.1`, `qwen2.5`

### 3. Set up the project

```bash
cd part2_weather_mcp

# Create virtual environment and install dependencies
uv sync

# Copy the environment file
cp .env.example .env
```

Edit `.env` if you want to change the Ollama model or switch to a different LLM provider.

---

## Running

### Option A — Run the client (starts the server automatically)

The client spawns the server as a subprocess:

```bash
uv run mcp_client.py
```

Example conversation:
```
You: What is the weather in Tokyo?
  [tool] get_current_weather({'location': 'Tokyo'})
Assistant: The current weather in Tokyo is partly cloudy with a temperature of 12°C...

You: Give me a 5-day forecast for Mumbai
  [tool] get_forecast({'location': 'Mumbai', 'days': 5})
Assistant: Here is the 5-day forecast for Mumbai...
```

### Option B — Test the server directly with MCP Inspector

MCP Inspector is a browser-based UI for testing your server:

```bash
uv run mcp dev weather_server.py
```

Then open http://localhost:5173 in your browser. You can call each tool manually and see the output.

### Option C — Use the server from VS Code Copilot

The `.vscode/mcp.json` at the root of `exercise_5_mcp` already configures the weather server. Open that folder in VS Code, then in Copilot Chat (Agent mode) ask:

```
What is the weather forecast for Berlin this week?
```

---

## Switching LLM Provider

Edit `.env` to change the provider:

```bash
# Use Anthropic Claude
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your-key-here

# Install the extra dependency
uv add anthropic
```

```bash
# Use OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=your-key-here

uv add openai
```

---

## Tools Exposed by the Server

### `get_current_weather(location)`
Returns temperature, humidity, wind, precipitation, and condition for any city.

```
get_current_weather("London")
get_current_weather("São Paulo")
```

### `get_forecast(location, days)`
Returns a day-by-day forecast table (up to 16 days).

```
get_forecast("Paris", days=7)
```

### `search_location(query)`
Search for a city by partial name, returns coordinates and country info.

```
search_location("frank")   # returns Frankfurt, etc.
```

---

## Resources and Prompts

The server also exposes a **resource** and a **prompt** (used by VS Code Copilot or any MCP-compatible client):

```
Resource URI : weather://current/{location}
Prompt name  : weather_report_prompt
```

---

## Important Notes

- **Never use `print()` in a stdio MCP server** — stdout is reserved for the MCP JSON-RPC protocol. Use `print(..., file=sys.stderr)` for debug output.
- The server is started fresh each time the client connects (subprocess via `uv run`).
- `uv run` automatically creates a virtual environment and installs dependencies on the first run.

---

## How It Works — Flow Diagram

```
User types query
      |
      v
mcp_client.py
  calls LLM (Ollama) with:
    - user message
    - list of MCP tools (name, description, parameters)
      |
      v
  LLM decides to call a tool
  e.g. get_current_weather(location="Paris")
      |
      v
  client sends tool call to weather_server.py (via stdio)
      |
      v
weather_server.py
  calls Open-Meteo API
  returns formatted weather string
      |
      v
  client passes tool result back to LLM
      |
      v
  LLM generates final natural language response
      |
      v
User sees answer
```
