# LangChain

## 1. The Problem: Why Do We Need LangChain?

In Exercises 1 and 2, we built RAG systems by manually wiring everything together — prompts were hardcoded strings, chains were manual function calls, and adding new capabilities meant writing more plumbing code.

As LLM apps grow complex, you need:
- **Prompt management** — reusable templates, not hardcoded strings
- **Chains** — link multiple LLM calls where one output feeds the next
- **Tools** — give the LLM the ability to call functions and APIs
- **Agents** — let the LLM decide *which* tools to call and *when*
- **Memory** — remember previous messages in a conversation

> **Think of it this way:**
> - **Without LangChain:** Building every LLM feature from raw API calls — like making a website with raw sockets.
> - **With LangChain:** Pre-built, composable building blocks — like using Flask or FastAPI.

---

## 2. What is LangChain?

LangChain is a **Python framework** for building LLM-powered applications. It provides abstractions for common patterns.

| Aspect | Details |
|--------|---------|
| **Built by** | Harrison Chase (LangChain Inc.) |
| **License** | MIT (free and open source) |
| **LLM Support** | OpenAI, Anthropic, Ollama, Groq, HuggingFace, and more |

---

## 3. Core Concepts We Covered

### 3.1 LLMs — Unified Model Interface

LangChain provides a **common interface** across LLM providers. Swap models without changing app code.

```python
from langchain_ollama import OllamaLLM
llm = OllamaLLM(model="llama3.2", temperature=0.7)
response = llm.invoke("What is the capital of France?")
```

We used **Ollama** (local LLM) — no API key needed, runs on your machine.

### 3.2 Prompt Templates

Instead of hardcoding prompts, `PromptTemplate` lets you create reusable, parameterized prompts.

```python
prompt = PromptTemplate(
    input_variables=["cuisine"],
    template="Suggest ONE creative name for a {cuisine} restaurant. Just the name."
)
```

Variables go in `{curly_braces}` and get filled in at runtime.

### 3.3 Chains — Linking LLM Calls Together

A **chain** combines an LLM + prompt into a reusable unit.

**Basic Chain** — single LLM call:
```python
chain = LLMChain(llm=llm, prompt=prompt)
result = chain.invoke({"cuisine": "Italian"})  # → "La Bella Vita"
```

**Sequential Chain** — multiple LLM calls where output flows between them:
```
Input ("Indian")
    ↓
[Name Chain] → "Spice Garden"       (output_key="restaurant_name")
    ↓
[Menu Chain] → 5 dishes + prices    (uses restaurant_name from above)
    ↓
Final Output
```

- `output_key` names a chain's output so the next chain can reference it
- `SequentialChain` automatically passes outputs between chains

### 3.4 Memory — Remembering Conversations

By default, each LLM call is **stateless**. Memory lets chains remember previous messages.

| Memory Type | What It Stores | Trade-off |
|-------------|---------------|-----------|
| **Buffer** | Complete conversation history | Simple but grows without limit |
| **Window (k)** | Only the last k exchanges | Fixed size, loses old context |
| **Summary** | LLM-generated summary of the conversation | Compressed, but uses extra LLM calls |

**Example with Buffer Memory:**
```python
conversation = ConversationChain(llm=llm, memory=ConversationBufferMemory())
conversation.predict(input="My name is Abhinav.")
conversation.predict(input="What's my name?")  # → "Your name is Abhinav!"
```

### 3.5 Tools — Giving the LLM Abilities

Tools are **Python functions** that an LLM can decide to call. The `@tool` decorator and docstring tell the LLM what each tool does.

```python
@tool
def calculate(expression: str) -> str:
    """Evaluate a math expression and return the result."""
    return str(eval(expression))
```

We built custom tools: `get_word_count`, `get_current_times`, `calculate`
We also used a built-in tool: **WikipediaQueryRun** for searching Wikipedia.

### 3.6 Agents — LLMs That Choose Tools Autonomously

An **agent** is an LLM that decides which tools to call, in what order, and when to stop. Unlike chains (fixed sequence), agents are **dynamic**.

```python
agent = create_agent("ollama:llama3.2", tools=[calculate, get_current_times])
agent.invoke({"messages": [{"role": "user", "content": "What is 25 * 17?"}]})
```

**How an agent works:**
1. User sends a message
2. LLM looks at available tools and decides which one to call
3. Agent executes the tool and gets the result
4. LLM decides: need another tool call? Or ready to answer?
5. Repeats until done, then returns the final answer

**Agents we built:**

| Agent | Tools | Purpose |
|-------|-------|---------|
| **Simple** | word_count, time, calculate | General-purpose utility |
| **Wikipedia** | WikipediaQueryRun, calculate | Research and math |
| **Restaurant** | cuisine_info, suggest_name, calculate | Domain-specific |

### 3.7 Streamlit UI

We built a web app using **Streamlit** that demonstrates the Sequential Chain visually — pick a cuisine, get a restaurant name + menu.

- `@st.cache_resource` caches the chain so it's not recreated on every interaction
- Run with: `streamlit run app/streamlit_app.py`

---

## 4. Dependencies

| Package | Purpose |
|---------|---------|
| **langchain** | Core framework (agents, tools) |
| **langchain-core** | Base abstractions (prompts, messages) |
| **langchain-ollama** | Ollama LLM integration |
| **langchain-community** | Community tools (Wikipedia, etc.) |
| **langchain-classic** | LLMChain, SequentialChain, memory classes |
| **streamlit** | Web UI framework |
| **wikipedia-api** | Backend for the Wikipedia tool |

> **Note:** This exercise uses Ollama (local). Run `ollama serve` and `ollama pull llama3.2` before starting.

---

## 5. Quick Reference

| Concept | What It Is |
|---------|-----------|
| **LangChain** | Python framework for building LLM apps |
| **PromptTemplate** | Reusable prompt with `{variables}` |
| **LLMChain** | LLM + Prompt combined into a callable unit |
| **SequentialChain** | Runs multiple chains in order, passing outputs between them |
| **Tool** | A Python function the LLM can call (`@tool` decorator) |
| **Agent** | An LLM that autonomously decides which tools to use |
| **Buffer Memory** | Stores complete conversation history |
| **Window Memory** | Stores only the last K exchanges |
| **Summary Memory** | Compresses conversation into a summary |
| **`output_key`** | Names a chain's output for the next chain |
| **Ollama** | Local LLM server — no API key needed |

---
