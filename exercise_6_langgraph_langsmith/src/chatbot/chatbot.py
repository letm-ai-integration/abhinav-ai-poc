from typing import Annotated
from typing_extensions import TypedDict
from dotenv import load_dotenv
import os

from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode, tools_condition

from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langsmith import traceable


load_dotenv()


memory = MemorySaver()


class State(TypedDict):
    messages: Annotated[list, add_messages]


@tool
def get_stock_price(symbol: str) -> float:
    """Return current price of a stock given its symbol"""
    return {
        "MSFT": 200.3,
        "AAPL": 100.4,
        "AMZN": 150.0,
        "RIL": 87.6,
    }.get(symbol.upper(), 0.0)


tools = [get_stock_price]


llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
)

llm_with_tools = llm.bind_tools(tools)


def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


def build_graph():
    builder = StateGraph(State)

    builder.add_node("chatbot", chatbot)
    builder.add_node("tools", ToolNode(tools))

    builder.add_edge(START, "chatbot")
    builder.add_conditional_edges("chatbot", tools_condition)
    builder.add_edge("tools", "chatbot")

    return builder.compile(checkpointer=memory)


graph = build_graph()


def save_graph_png(filename="stock_agent_graph.png"):
    png_bytes = graph.get_graph().draw_mermaid_png()
    with open(filename, "wb") as f:
        f.write(png_bytes)
    print(f"Graph saved as {filename}")


# LangSmith Traced Call
@traceable(name="StockAgentGraphRun")
def call_graph(query: str, thread_id: str = "1"):
    config = {"configurable": {"thread_id": thread_id}}

    state = graph.invoke(
        {"messages": [{"role": "user", "content": query}]},
        config=config,
    )

    return state["messages"][-1].content


def main():
    save_graph_png()

    print("\n--- Thread 1 ---")
    print(call_graph(
        "I want to buy 20 AMZN stocks using current price. Then 15 MSFT. What will be the total cost?",
        thread_id="1"
    ))

    print("\n--- Thread 1 Continued ---")
    print(call_graph(
        "Using the current price tell me the total price of 10 RIL stocks and add it to previous total cost",
        thread_id="1"
    ))

    print("\n--- Thread 2 ---")
    print(call_graph(
        "Tell me the current price of 5 AAPL stocks.",
        thread_id="2"
    ))

    print("\n--- Thread 2 Continued ---")
    print(call_graph(
        "Tell me the current price of 5 MSFT stocks and add it to previous total",
        thread_id="2"
    ))


if __name__ == "__main__":
    main()