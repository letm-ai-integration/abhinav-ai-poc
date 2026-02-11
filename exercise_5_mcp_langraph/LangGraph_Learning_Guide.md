# LangGraph

## 1. The Problem: Why Do We Need LangGraph?

We already know that AI agents use LLMs to make decisions and interact with tools. But building a reliable agent involves more than just calling an LLM in a loop. Real-world agents need:

- **State management** — remembering what happened across multiple steps
- **Conditional logic** — choosing different paths based on LLM output
- **Loops and cycles** — retrying or iterating until a task is complete
- **Human-in-the-loop** — pausing for human approval before taking action
- **Persistence** — resuming a workflow even after a crash or restart

Writing all of this from scratch with plain Python is painful and error-prone. LangChain helped with chaining LLM calls, but it was too linear — it couldn't handle cycles, conditional branching, or persistent state well.

**LangGraph solves this.** It lets you model your AI agent as a **directed graph** where nodes are actions and edges define the flow — including conditions, loops, and parallel paths.

> **Think of it this way:**
> - **LangChain** = A straight assembly line (do A, then B, then C)
> - **LangGraph** = A flowchart (do A, then if X go to B, else go to C, loop back if needed)

---

## 2. What is LangGraph?

LangGraph is a **Python framework** (built by the LangChain team) for creating **stateful, cyclic, multi-actor LLM applications** using graph-based architectures.

| Aspect | Details |
|--------|---------|
| **Built by** | LangChain (same team) |
| **Version** | 1.0 (GA — October 2025) |
| **License** | MIT (free and open source) |
| **Language** | Python and JavaScript |
| **Used by** | Uber, LinkedIn, Klarna, Elastic, JP Morgan |

**Key idea:** You define your agent workflow as a graph with **nodes** (functions/actions), **edges** (flow between nodes), and **state** (shared memory). LangGraph handles execution, persistence, streaming, and human oversight.

---

## 3. Core Concepts

### 3.1 State — The Shared Memory

State is a dictionary (typically a `TypedDict`) that flows through the entire graph. Every node reads from it and writes back to it. Think of it as the working memory of your agent.

```python
from typing import TypedDict

class AgentState(TypedDict):
    messages: list       # Conversation history
    current_step: str    # What the agent is doing now
    flight_data: dict    # Data fetched from tools
    decision: str        # Final decision made
```

**Key points:**
- State is defined once and shared across all nodes
- Each node receives the current state and returns updates to it
- Updates are merged into the state automatically
- State can be persisted to a database for durability

### 3.2 Nodes — The Actions

Nodes are **Python functions** that take the state as input, do something (call an LLM, query a database, run logic), and return state updates.

```python
def extract_intent(state: AgentState):
    """Use LLM to understand what the user wants"""
    response = llm.invoke(state["messages"])
    return {"current_step": "intent_extracted", "decision": response.content}

def fetch_flights(state: AgentState):
    """Call flight API to get options"""
    flights = search_flights_api(state["decision"])
    return {"flight_data": flights, "current_step": "flights_fetched"}
```

**Key points:**
- A node is just a regular Python function
- It receives the full state dictionary
- It returns a dictionary with only the keys it wants to update
- Nodes can call LLMs, APIs, databases, or run any Python logic

### 3.3 Edges — The Flow

Edges connect nodes and define the order of execution. There are three types:

| Edge Type | What It Does | When to Use |
|-----------|-------------|-------------|
| **Normal Edge** | Always go from A → B | Fixed sequential steps |
| **Conditional Edge** | Go to A or B based on a function's output | Branching / decision points |
| **Entry Edge** | Defines which node runs first | Starting point of the graph |

**Normal edge:**
```python
graph.add_edge("fetch_flights", "compare_options")
```

**Conditional edge:**
```python
def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "call_tool"    # Go to tool node
    return "end"              # Finish

graph.add_conditional_edges(
    "llm_call",          # After this node...
    should_continue,     # Run this function...
    {                    # Map outputs to nodes:
        "call_tool": "tool_node",
        "end": END
    }
)
```

### 3.4 The Graph — Putting It All Together

The `StateGraph` is the container that holds nodes and edges. You build it, compile it, and then invoke it.

```python
from langgraph.graph import StateGraph, START, END

# 1. Create the graph with your state schema
graph = StateGraph(AgentState)

# 2. Add nodes
graph.add_node("extract_intent", extract_intent)
graph.add_node("fetch_flights", fetch_flights)
graph.add_node("compare_options", compare_options)

# 3. Add edges
graph.add_edge(START, "extract_intent")
graph.add_edge("extract_intent", "fetch_flights")
graph.add_edge("fetch_flights", "compare_options")
graph.add_edge("compare_options", END)

# 4. Compile
agent = graph.compile()

# 5. Run
result = agent.invoke({"messages": [("user", "Find me a flight to London")]})
```

---

## 4. How LangGraph Works — Step by Step

Here's what happens when you call `agent.invoke(...)`:

1. **Input is merged into the initial state**
2. **The entry node runs** — receives the state, returns updates
3. **State is updated** with the node's return value
4. **The next edge is evaluated** — normal edges go directly, conditional edges run the routing function
5. **The next node runs** — receives the updated state
6. **Steps 3-5 repeat** until the graph reaches the `END` node
7. **Final state is returned** to the caller

This is fundamentally different from a simple function chain because:
- **Cycles are allowed** — a node can route back to a previous node (e.g., retry logic)
- **Branching is native** — conditional edges make decision-making clean
- **State persists** — every step has access to the full history

---

## 5. Building a Complete Agent (Calculator Example)

This is the classic LangGraph pattern — an LLM that can use tools, looping until the task is done.

### Step 1: Install Dependencies

```bash
pip install langgraph langchain-anthropic
```

### Step 2: Define Tools

```python
from langchain_core.tools import tool

@tool
def add(a: float, b: float) -> float:
    """Add two numbers"""
    return a + b

@tool
def multiply(a: float, b: float) -> float:
    """Multiply two numbers"""
    return a * b

tools = [add, multiply]
tools_by_name = {t.name: t for t in tools}
```

### Step 3: Define the LLM Node

```python
from langchain_anthropic import ChatAnthropic

llm = ChatAnthropic(model="claude-sonnet-4-5-20250929").bind_tools(tools)

def llm_call(state):
    """Call the LLM with the current messages"""
    return {"messages": [llm.invoke(state["messages"])]}
```

### Step 4: Define the Tool Node

```python
from langchain_core.messages import ToolMessage

def tool_node(state):
    """Execute whatever tool the LLM requested"""
    results = []
    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_by_name[tool_call["name"]]
        result = tool.invoke(tool_call["args"])
        results.append(ToolMessage(content=str(result), tool_call_id=tool_call["id"]))
    return {"messages": results}
```

### Step 5: Define the Routing Logic

```python
from typing import Literal
from langgraph.graph import MessagesState, StateGraph, START, END

def should_continue(state) -> Literal["tool_node", "__end__"]:
    """If the LLM made a tool call, execute it. Otherwise, finish."""
    if state["messages"][-1].tool_calls:
        return "tool_node"
    return END
```

### Step 6: Build and Run the Graph

```python
# Build the graph
builder = StateGraph(MessagesState)
builder.add_node("llm_call", llm_call)
builder.add_node("tool_node", tool_node)

builder.add_edge(START, "llm_call")
builder.add_conditional_edges("llm_call", should_continue, ["tool_node", END])
builder.add_edge("tool_node", "llm_call")  # Loop back after tool execution

agent = builder.compile()

# Run it
from langchain_core.messages import HumanMessage
result = agent.invoke({"messages": [HumanMessage(content="What is 3 + 4, then multiply by 2?")]})

for msg in result["messages"]:
    print(f"{msg.type}: {msg.content}")
```

**What happens:**
1. User asks "What is 3 + 4, then multiply by 2?"
2. LLM decides to call `add(3, 4)` → routes to tool_node
3. Tool returns 7 → loops back to LLM
4. LLM decides to call `multiply(7, 2)` → routes to tool_node
5. Tool returns 14 → loops back to LLM
6. LLM has the answer, no more tool calls → routes to END
7. Returns: "3 + 4 = 7, multiplied by 2 = 14"

---

## 6. Key Features for Production

### 6.1 Persistence (Checkpointing)

Save and resume agent state — survives crashes, server restarts, and long-running workflows.

```python
from langgraph.checkpoint.memory import InMemorySaver

checkpointer = InMemorySaver()
agent = builder.compile(checkpointer=checkpointer)

# Each thread_id gets its own saved state
config = {"configurable": {"thread_id": "user-123"}}
result = agent.invoke({"messages": [HumanMessage(content="Hello")]}, config)

# Later, resume the same conversation
result = agent.invoke({"messages": [HumanMessage(content="Continue")]}, config)
```

### 6.2 Human-in-the-Loop

Pause the agent for human review before taking sensitive actions.

```python
from langgraph.types import interrupt

@tool
def book_flight(flight_id: str):
    """Book a flight — requires human approval"""
    # This pauses execution and asks the human
    approval = interrupt({"question": f"Book flight {flight_id}?"})
    if approval == "yes":
        return f"Flight {flight_id} booked!"
    return "Booking cancelled."
```

### 6.3 Streaming

Stream node outputs as they happen, instead of waiting for the full graph to complete.

```python
for event in agent.stream({"messages": [HumanMessage(content="Find flights")]}):
    print(event)
```

### 6.4 Memory (Short-term and Long-term)

- **Short-term memory** — State within a single conversation (built-in via state)
- **Long-term memory** — Cross-conversation memory with semantic search

```python
# Long-term memory stores facts across sessions
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()
agent = builder.compile(checkpointer=checkpointer, store=store)
```

### 6.5 Time Travel

Inspect and roll back to any previous state in the execution.

```python
# Get all checkpoints for a thread
for state in agent.get_state_history(config):
    print(state.values, state.created_at)

# Roll back to a specific checkpoint
agent.update_state(config, values=previous_state)
```

---

## 7. Multi-Agent Patterns

LangGraph supports multiple agents working together:

| Pattern | Description | Example |
|---------|-------------|---------|
| **Sequential** | Agent A → Agent B → Agent C | Document: extract → classify → summarize |
| **Parallel** | Agent A + Agent B run simultaneously | Search web + search database at same time |
| **Hierarchical** | Supervisor agent delegates to worker agents | Manager routes to researcher, writer, reviewer |
| **Handoff** | One agent transfers control to another | Chatbot escalates to specialist |

### Supervisor Pattern Example

```python
def supervisor(state):
    """Decide which specialist agent to call next"""
    response = llm.invoke(
        f"Given the task: {state['task']}, which agent should handle it? "
        f"Options: researcher, writer, reviewer, FINISH"
    )
    return {"next_agent": response.content}

# Conditional routing from supervisor to specialists
graph.add_conditional_edges(
    "supervisor",
    lambda state: state["next_agent"],
    {
        "researcher": "researcher_node",
        "writer": "writer_node",
        "reviewer": "reviewer_node",
        "FINISH": END,
    }
)
```

---

## 8. LangGraph vs Other Approaches

| Aspect | Plain Python | LangChain | LangGraph |
|--------|-------------|-----------|-----------|
| **Control flow** | Manual loops/ifs | Linear chains | Graph with cycles & conditions |
| **State management** | DIY | Limited | Built-in, persistent |
| **Human-in-the-loop** | DIY | Not built-in | First-class support |
| **Persistence** | DIY | Not built-in | Built-in checkpointing |
| **Streaming** | DIY | Basic | Full support |
| **Multi-agent** | Complex | Difficult | Native patterns |
| **Debugging** | Print statements | LangSmith traces | LangGraph Studio + LangSmith |

---

## 9. LangGraph Ecosystem

| Tool | Purpose |
|------|---------|
| **LangGraph** | Core framework (open source, MIT license) |
| **LangGraph Platform** | Deployment infrastructure (SaaS or self-hosted) |
| **LangGraph Studio** | Visual IDE for prototyping and debugging graphs |
| **LangSmith** | Observability, tracing, and evaluation |
| **LangChain** | Model abstractions, tools, and integrations |

---

## 10. Quick Reference

| Concept | What It Is |
|---------|-----------|
| **StateGraph** | The graph builder — you add nodes and edges to it |
| **State** | A TypedDict that flows through the graph as shared memory |
| **Node** | A Python function that reads state and returns updates |
| **Edge** | A connection between nodes (normal, conditional, or entry) |
| **START** | Special node — marks where the graph begins |
| **END** | Special node — marks where the graph finishes |
| **Conditional Edge** | A routing function that decides the next node |
| **Compile** | Turns the graph definition into a runnable |
| **Invoke** | Runs the graph with input and returns final state |
| **Stream** | Runs the graph and yields events as they happen |
| **Checkpointer** | Saves state for persistence and resume |
| **Interrupt** | Pauses execution for human-in-the-loop |
| **MessagesState** | Pre-built state with a `messages` list (common pattern) |

---