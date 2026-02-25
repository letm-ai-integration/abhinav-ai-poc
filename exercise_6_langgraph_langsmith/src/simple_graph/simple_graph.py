from typing import TypedDict
from langgraph.graph import StateGraph, START, END


class PortfolioState(TypedDict):
    amount_usd: float
    total_usd: float
    total_inr: float


def calc_total(state: PortfolioState) -> PortfolioState:
    state["total_usd"] = state["amount_usd"] * 1.08
    return state


def convert_to_inr(state: PortfolioState) -> PortfolioState:
    state["total_inr"] = state["total_usd"] * 85
    return state


def build_graph():
    builder = StateGraph(PortfolioState)

    builder.add_node("calc_total_node", calc_total)
    builder.add_node("convert_to_inr_node", convert_to_inr)

    builder.add_edge(START, "calc_total_node")
    builder.add_edge("calc_total_node", "convert_to_inr_node")
    builder.add_edge("convert_to_inr_node", END)

    return builder.compile()


def save_graph_png(graph, filename="simple_graph.png"):
    png_bytes = graph.get_graph().draw_mermaid_png()

    with open(filename, "wb") as f:
        f.write(png_bytes)

    print(f"Graph PNG saved as: {filename}")


def main():
    graph = build_graph()

    save_graph_png(graph)

    result = graph.invoke({"amount_usd": 1000})
    print("Final Result:", result)


if __name__ == "__main__":
    main()