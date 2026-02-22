# Exercise 5 — Model Context Protocol (MCP)

MCP (Model Context Protocol) is an open standard by Anthropic that lets AI assistants connect to external tools, data sources, and services in a uniform way. Think of it as a USB-C port for AI — any MCP-compatible client can talk to any MCP-compatible server.

---

## What You Will Learn

- What MCP is and how it works
- How to connect an **existing** MCP server (GitHub) to VS Code Copilot
- How to **build your own** MCP server (weather data) and Python client

---

## Structure

```
exercise_5_mcp/
├── .vscode/
│   └── mcp.json             # VS Code config — registers both MCP servers
├── part1_github_mcp/
│   └── README.md            # Guide: using the official GitHub MCP server
└── part2_weather_mcp/
    ├── pyproject.toml       # uv project dependencies
    ├── .python-version      # Python 3.11
    ├── .env.example         # LLM configuration template
    ├── weather_server.py    # Custom MCP Server (global weather via Open-Meteo)
    ├── mcp_client.py        # Python MCP Client (Ollama by default)
    └── README.md            # Guide: building and running the weather MCP
```

> `.vscode/` is git-ignored. The `mcp.json` file works locally but will not be committed. Recreate it from the content in this README if needed.

---

## MCP Architecture

```
┌─────────────────────────────────────────────────────────┐
│                       MCP Host                          │
│   (VS Code Copilot, Claude Desktop, your Python client) │
│                                                         │
│   ┌─────────────┐        ┌─────────────┐                │
│   │ MCP Client  │        │ MCP Client  │                │
│   └──────┬──────┘        └──────┬──────┘                │
└──────────┼──────────────────────┼───────────────────────┘
           │ stdio/HTTP/SSE       │ stdio/HTTP/SSE
           v                      v
  ┌─────────────────┐  ┌──────────────────────┐
  │  GitHub MCP     │  │  Weather MCP Server  │
  │  Server         │  │  (weather_server.py) │
  │  (GitHub-hosted)│  │  calls Open-Meteo API│
  └─────────────────┘  └──────────────────────┘
```

---

## Core MCP Concepts

| Concept | Description | Analogy |
|---|---|---|
| **Server** | Exposes tools/resources/prompts | A REST API |
| **Client** | Connects to servers and calls tools | An API consumer |
| **Tool** | Function the LLM can call (has side effects) | POST endpoint |
| **Resource** | Read-only data identified by a URI | GET endpoint |
| **Prompt** | Reusable prompt template | Stored procedure |
| **Transport** | Communication channel (`stdio`, `http`, `sse`) | HTTP vs gRPC |

---

## Part 1 — GitHub MCP Server

Uses GitHub's **officially hosted** MCP server via OAuth. No code to write — just configure.

Read: [part1_github_mcp/README.md](./part1_github_mcp/README.md)

Quick start:
1. Open this folder in VS Code
2. Open Copilot Chat → Agent mode
3. The GitHub server appears in the Tools list — click Auth
4. Ask Copilot to list your repos or create an issue

---

## Part 2 — Custom Weather MCP Server + Client

Build a server that exposes three tools (current weather, forecast, location search) using the free Open-Meteo API. Then run a Python client that connects to it and uses a local Ollama LLM.

Read: [part2_weather_mcp/README.md](./part2_weather_mcp/README.md)

Quick start:
```bash
# Install Ollama and pull a model
ollama pull llama3.2

cd part2_weather_mcp
uv sync
cp .env.example .env
uv run mcp_client.py
```

---

## VS Code mcp.json

The `.vscode/mcp.json` registers both servers for Copilot:

```json
{
  "servers": {
    "github": {
      "url": "https://api.githubcopilot.com/mcp/"
    },
    "weather": {
      "type": "stdio",
      "command": "uv",
      "args": ["--directory", "${workspaceFolder}/part2_weather_mcp", "run", "weather_server.py"]
    }
  }
}
```

Open the `exercise_5_mcp` folder as your VS Code workspace for `${workspaceFolder}` to resolve correctly.

---

## Prerequisites

| Tool | Install |
|---|---|
| Python 3.10+ | https://python.org |
| uv | `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"` |
| Ollama | https://ollama.com |
| VS Code 1.99+ | https://code.visualstudio.com |
| GitHub Copilot extension | VS Code Extensions marketplace |