from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END


class PortfolioState(TypedDict):
    amount_usd: float
    total_usd: float
    target_currency: Literal["INR", "EUR"]
    total: float


def calc_total(state: PortfolioState) -> PortfolioState:
    state["total_usd"] = state["amount_usd"] * 1.08
    return state


def convert_to_inr(state: PortfolioState) -> PortfolioState:
    state["total"] = state["total_usd"] * 85
    return state

def convert_to_eur(state: PortfolioState) -> PortfolioState:
    state["total"] = state["total_usd"] * 0.92
    return state

def choose_conversion(state: PortfolioState) -> str:
    return state["target_currency"]


def build_graph():
    builder = StateGraph(PortfolioState)

    builder.add_node("calc_total_node", calc_total)
    builder.add_node("convert_to_inr_node", convert_to_inr)
    builder.add_node("convert_to_eur_node", convert_to_eur)

    builder.add_edge(START, "calc_total_node")
    builder.add_conditional_edges(
        "calc_total_node", 
        choose_conversion, 
        {
            "INR": "convert_to_inr_node",
            "EUR": "convert_to_eur_node"
        }
    )
    builder.add_edge([ "convert_to_inr_node", "convert_to_eur_node"], END)

    return builder.compile()


def save_graph_png(graph, filename="graph_with_condition.png"):
    png_bytes = graph.get_graph().draw_mermaid_png()

    with open(filename, "wb") as f:
        f.write(png_bytes)

    print(f"Graph PNG saved as: {filename}")


def main():
    graph = build_graph()

    save_graph_png(graph)

    result = graph.invoke({"amount_usd": 1000, "target_currency": "INR"})
    print("Final Result:", result)


if __name__ == "__main__":
    main()