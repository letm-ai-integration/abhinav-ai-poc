from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain_groq import ChatGroq

from dotenv import load_dotenv
load_dotenv()

import asyncio
import os
import sys

async def main():
    # Project root so mcp_server/math_server.py and venv are found
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    client = MultiServerMCPClient(
        {
            "math" : {
                "command" : sys.executable,
                "args" : ["mcp_server/math_server.py"],
                "transport" : "stdio",
                "cwd" : project_root,
            },
            "weather" : {
                "url" : "http://localhost:8000/mcp",
                "transport" : "streamable-http",
            }
        }
    )

    os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

    tools = await client.get_tools()
    model = ChatGroq(model = "openai/gpt-oss-120b")
    agent = create_agent(model, tools)

    math_response = await agent.ainvoke(
        {"messages" : [{"role" : "user", "content" : "What is (10 + 20) * 3?"}]}
    )

    print("Math Response: ", math_response['messages'][-1].content)

    weather_response = await agent.ainvoke(
        {"messages" : [{"role" : "user", "content" : "What is the weather in Lucknow?"}]}
    )

    print("Weather Response: ", weather_response['messages'][-1].content)

asyncio.run(main())    