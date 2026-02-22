"""
Weather MCP Client
Connects to the Weather MCP server and uses an LLM for natural language interaction.

LLM provider is controlled via LLM_PROVIDER env var :
  - ollama    : local Ollama
"""

import asyncio
import json
import os
import sys
from abc import ABC, abstractmethod
from contextlib import AsyncExitStack
from pathlib import Path

from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()


# ---------------------------------------------------------------------------
# LLM Backend Abstraction
# ---------------------------------------------------------------------------

class LLMBackend(ABC):
    """
    Base class for LLM providers.
    """

    @abstractmethod
    def chat(self, messages: list, tools: list) -> dict:
        pass

    def make_tool_result_message(self, tool_call_id: str, tool_name: str, content: str) -> dict:
        """Return a tool-result message in Ollama format."""
        return {"role": "tool", "tool_call_id": tool_call_id, "content": content}


class OllamaBackend(LLMBackend):
    def __init__(self):
        try:
            import ollama
            self.model = os.getenv("OLLAMA_MODEL", "llama3.2")
            self.client = ollama.Client(host=os.getenv("OLLAMA_HOST", "http://localhost:11434"))
        except ImportError:
            raise ImportError("Ollama package missing. Run: uv add ollama")

    def chat(self, messages: list, tools: list) -> dict:
        response = self.client.chat(
            model=self.model,
            messages=messages,
            tools=tools if tools else None,
        )
        msg = response.message
        tool_calls = []
        if msg.tool_calls:
            for i, tc in enumerate(msg.tool_calls):
                args = tc.function.arguments
                if isinstance(args, str):
                    args = json.loads(args)
                tool_calls.append({
                    "id": f"call_{i}",
                    "name": tc.function.name,
                    "arguments": args,
                })
        return {
            "text": msg.content or "",
            "tool_calls": tool_calls,
            "raw_assistant_message": msg,
        }


def build_llm_backend() -> LLMBackend:
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()
    backends = {"ollama": OllamaBackend}
    if provider not in backends:
        raise ValueError(f"Unknown LLM_PROVIDER '{provider}'. Choose: {list(backends.keys())}")
    backend = backends[provider]()
    print(f"[LLM] Provider: {provider}")
    return backend


# ---------------------------------------------------------------------------
# MCP Client
# ---------------------------------------------------------------------------

class WeatherMCPClient:
    def __init__(self, llm: LLMBackend):
        self.llm = llm
        self.session: ClientSession | None = None
        self.exit_stack = AsyncExitStack()
        self.tools: list[dict] = []

    async def connect(self, server_dir: str):
        server_params = StdioServerParameters(
            command="uv",
            args=["--directory", server_dir, "run", "weather_server.py"],
        )
        transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        read_stream, write_stream = transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(read_stream, write_stream)
        )
        await self.session.initialize()

        mcp_tools = (await self.session.list_tools()).tools
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description or "",
                    "parameters": t.inputSchema,
                },
            }
            for t in mcp_tools
        ]
        print(f"[MCP] Connected. Tools: {[t['function']['name'] for t in self.tools]}\n")

    async def run_query(self, query: str) -> str:
        messages = [{"role": "user", "content": query}]

        for _ in range(6):  # max agentic iterations
            response = self.llm.chat(messages, self.tools)

            if not response["tool_calls"]:
                return response["text"]

            # Append assistant message to history
            messages.append(response["raw_assistant_message"])

            # Execute each tool call via MCP server
            for tc in response["tool_calls"]:
                print(f"  [tool] {tc['name']}({tc['arguments']})")
                result = await self.session.call_tool(tc["name"], tc["arguments"])
                output = "\n".join(
                    block.text for block in result.content if hasattr(block, "text")
                )
                messages.append(
                    self.llm.make_tool_result_message(tc["id"], tc["name"], output)
                )

        return "Reached max iterations without a final answer."

    async def chat_loop(self):
        print("Weather Assistant ready. Ask about weather anywhere in the world.")
        print("Type 'quit' to exit.\n")
        while True:
            try:
                query = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if not query:
                continue
            if query.lower() in ("quit", "exit"):
                break
            try:
                answer = await self.run_query(query)
                print(f"\nAssistant: {answer}\n")
            except Exception as e:
                print(f"[Error] {e}\n", file=sys.stderr)

    async def cleanup(self):
        await self.exit_stack.aclose()


async def main():
    server_dir = str(Path(__file__).parent)
    llm = build_llm_backend()
    client = WeatherMCPClient(llm)
    try:
        await client.connect(server_dir)
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
