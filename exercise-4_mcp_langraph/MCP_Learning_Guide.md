# Model Context Protocol (MCP)

## 1. The Problem: Why Do We Need MCP?

Large Language Models (LLMs) like ChatGPT can generate text, images, and other content. But they **cannot take actions on their own** — they can't book a flight, query a database, or interact with external services.

To bridge this gap, we use **AI Agents**. An AI agent is essentially an automation script that uses an LLM to make decisions. It can interact with third-party tools, maintain memory, and go back and forth with the LLM until a task is completed.

> **Think of it this way:**
> - **Old automation scripts:** You coded all the decision logic manually.
> - **AI Agents:** The LLM makes the decisions — which tool to call, when to loop, when to stop.

### How an AI Agent Works (Flight Booking Example)

1. User says: *"I'd like to fly to London"*
2. Agent sends input to LLM → LLM extracts: destination = London
3. Agent asks LLM which tools to use → LLM says: query flight APIs
4. Agent fetches flight details from airlines
5. Agent asks LLM what next → LLM says: fetch user preferences
6. Agent sends all data to LLM → LLM picks the best flight
7. Agent books the flight and returns details to the user

### The Problem with Tools

Each third-party service has its own API format, endpoints, and response structure. Writing custom integration code for every service is painful and unscalable.

**This is exactly the problem MCP solves.**

---

## 2. What is MCP?

MCP stands for **Model Context Protocol**. Let's break that down:

| Term | Meaning |
|------|---------|
| **Model** | The AI / LLM (e.g., GPT, Claude, DeepSeek) |
| **Context** | Giving the AI context about a third-party service |
| **Protocol** | A set of standards / rules to follow |

MCP is a **standardized way for AI applications to discover and interact with external services**. Think of it as a universal adapter — if a service builds an MCP server following the standard, any MCP-compatible client can use it without writing custom code.

The specification is maintained at [modelcontextprotocol.io](https://modelcontextprotocol.io) and defines rules like:

- Communication must use **JSON-RPC** format
- Connections must be **stateful**
- Servers must expose capabilities through a defined structure (tools, resources, prompts)
- Clients must offer features like sampling, roots, and elicitation

**Key takeaway:** Anyone can build an MCP server as long as they follow the spec. And if a server follows the spec, any compliant client can use it.

---

## 3. MCP Architecture

### 3.1 Client-Server Model

MCP follows a client-server architecture:

- **MCP Server** — Exposes capabilities (tools, resources, prompts) of a service
- **MCP Client** — Embedded in AI agents/IDEs to discover and call those capabilities

Clients are built into tools like Cursor, Windsurf, Claude Code, and VS Code extensions like Roo Code.

### 3.2 The Three Components of an MCP Server

#### Tools

Actions the server can perform. Each tool has a name, description, and input/output schema.

Examples: `search_flights`, `create_booking`, `check_in`

```python
@mcp.tool()
def search_flights(origin: str, destination: str, date: str):
    """Search available flights between airports"""
    # ... query flight database and return results
```

#### Resources

Data the server makes available for the AI's decision-making. Each resource has a URI, name, and description. The URI can point to a web resource, a file, or a git repo.

Examples: airport info, refund policies, FAQs, weather data

```python
@mcp.resource("file://airports")
def get_airports():
    """Return list of supported airports and codes"""
    return airport_data
```

#### Prompts

Predefined prompt templates crafted by the server developer (who knows the best way to prompt for their service). These guide the LLM to use tools correctly.

```python
@mcp.prompt()
def find_best_flight(origin: str, destination: str):
    return f"You are a travel assistant. Search flights from {origin} \
    to {destination}. Format dates as YYYY-MM-DD. Be concise."
```

---

## 4. How Client and Server Communicate

### 4.1 JSON-RPC Protocol

MCP uses **JSON-RPC 2.0** for communication. It defines how a client can remotely call a method on the server, pass parameters, and receive a response.

| Direction | Contains |
|-----------|----------|
| **Client Request** | `jsonrpc: "2.0"`, `method`, `params`, `id` |
| **Server Response** | `jsonrpc: "2.0"`, `result`, `id`, `error` (optional) |

Example request:
```json
{
  "jsonrpc": "2.0",
  "method": "search_flights",
  "params": {"origin": "LAX", "destination": "JFK"},
  "id": 1
}
```

Example response:
```json
{
  "jsonrpc": "2.0",
  "result": [{"flight": "AA100", "price": 350}],
  "id": 1
}
```

### 4.2 Transport Mechanisms

MCP supports two transport modes:

| Transport | Use Case | When to Use |
|-----------|----------|-------------|
| **Standard IO (stdio)** | Local process communication | Dev/testing, single IDE, lightweight |
| **HTTP (Streamable)** | Network communication | Remote servers, shared access, production |

---

## 5. Using an Existing MCP Server

Before building your own, learn to use one.

### 5.1 Local MCP Server (stdio)

Configure via an `mcp.json` file in your IDE:

```json
{
  "mcpServers": {
    "flight-booking": {
      "command": "uv",
      "args": ["run", "python", "server.py"],
      "cwd": "/path/to/flight-booking-server"
    }
  }
}
```

The IDE starts the MCP server process, connects via stdio, lists available tools, and you can then chat with the agent to use those tools.

### 5.2 Remote MCP Server (HTTP)

Change the config to point to a URL:

```json
{
  "mcpServers": {
    "flight-booking": {
      "url": "http://remote-server:8080/mcp"
    }
  }
}
```

> **⚠️ Security Note:** When connecting to remote MCP servers, ensure proper authentication, authorization, data privacy, and trust verification are in place.

---

## 6. Building an MCP Server (Python)

The MCP Python SDK (FastMCP) makes building servers straightforward.

### Step-by-Step Setup

1. Initialize a Python project: `uv init flight-booking-server`
2. Add the MCP dependency: `uv add mcp[cli]`
3. Create `server.py` and import FastMCP
4. Define your tools, resources, and prompts using decorators
5. Run the server with your chosen transport

### Complete Server Template

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("flight-booking")

# --- Resources ---
@mcp.resource("file://airports")
def get_airports():
    return {"LAX": "Los Angeles", "JFK": "New York"}

# --- Tools ---
@mcp.tool()
def search_flights(origin: str, destination: str, date: str):
    """Search flights between two airports"""
    # Query your database / API here
    return [{"flight": "AA100", "price": 350}]

@mcp.tool()
def create_booking(flight_id: str, passenger: str):
    """Book a flight for a passenger"""
    return {"confirmation": "BK-12345"}

# --- Prompts ---
@mcp.prompt()
def find_best_flight(origin: str, destination: str):
    return f"You are a travel assistant. Use search_flights for \
    {origin} to {destination}. Compare prices and recommend the best."

# --- Run ---
if __name__ == "__main__":
    mcp.run(transport="stdio")  # Change to "http" for network access
```

### Server Run Modes

```python
# stdio (local, for IDE connections)
mcp.run(transport="stdio")

# HTTP (network, for remote/shared access)
mcp.run(transport="http", host="0.0.0.0", port=8080)

# Streamable HTTP
mcp.run(transport="streamable-http", host="0.0.0.0", port=8080)

# Stateless mode
mcp = FastMCP("flight-booking", stateless_http=True)
```

### Testing with MCP Inspector

Before building a client, test your server using the MCP Inspector:

```bash
npx @modelcontextprotocol/inspector
```

This starts a web UI where you can connect to your server and test tools, resources, and prompts interactively.

---

## 7. Building an MCP Client (Python)

If you're building your own AI agent, you need to build the client yourself.

### 7.1 Basic Client

```python
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async with streamablehttp_client("http://localhost:8080") as (r, w, _):
    async with ClientSession(r, w) as session:
        await session.initialize()

        # List tools
        tools = await session.list_tools()

        # Call a tool
        result = await session.call_tool("search_flights",
            {"origin": "LAX", "destination": "JFK", "date": "2026-03-01"})

        # Read a resource
        data = await session.read_resource("file://airports")

        # Get prompts
        prompts = await session.get_prompt("find_best_flight",
            {"origin": "LAX", "destination": "JFK"})
```

### 7.2 Client-Side Features

Just as servers expose tools/resources/prompts, clients have their own capabilities:

| Feature | Purpose | Example |
|---------|---------|---------|
| **Roots** | Shared folders the server can access | Expose `/project/src` for a code linter MCP |
| **Sampling** | Server asks client to call the LLM | Server sends data to LLM for summarization |
| **Elicitation** | Server asks the end user a question | Confirm flight choice before booking |

**Roots** — Define allowed directories the server can access:
```python
# Client side
allowed_roots = ["/project/src", "/project/config"]
# Pass while creating client session

# Server side
roots = await ctx.session.list_roots()
```

**Sampling** — Server delegates LLM calls to the client:
```python
# Client side: define a sampling handler
async def sampling_handler(message):
    # Call your LLM here and return response
    return llm_response

# Server side: request LLM via client
response = await ctx.session.create_message(sampling_message)
```

**Elicitation** — Server asks the end user for input:
```python
# Server side
answer = await ctx.elicit(message="Confirm booking for flight AA100?")

# Client side: define an elicitation callback
async def elicitation_handler(message):
    # Show to user, get response
    return user_response
```

### 7.3 Context (Server-to-Client Updates)

For long-running tasks, the server can send progress updates:

```python
from mcp.server.fastmcp import Context

@mcp.tool()
async def create_booking(flight_id: str, ctx: Context):
    await ctx.info("Starting booking process...")
    await ctx.report_progress(50, 100)
    # ... perform booking ...
    await ctx.info("Booking confirmed!")
    return {"status": "confirmed"}
```

---

## 8. Quick Reference

| Concept | Key Points |
|---------|------------|
| **MCP** | A standard protocol for AI to interact with external services |
| **MCP Server** | Exposes tools, resources, and prompts following the MCP spec |
| **MCP Client** | Connects to MCP servers; embedded in IDEs or custom agents |
| **Tools** | Actions the server can perform (functions with `@mcp.tool()`) |
| **Resources** | Data available for AI decision-making (URIs to files/APIs) |
| **Prompts** | Pre-built prompt templates from the server developer |
| **JSON-RPC 2.0** | Communication protocol between client and server |
| **Transport** | stdio (local) or HTTP (remote/shared) |
| **Roots** | Client-side: folders exposed to the server |
| **Sampling** | Server delegates LLM calls back to the client |
| **Elicitation** | Server asks the end user for input via the client |
| **MCP Inspector** | Web UI tool for testing MCP servers |

---
