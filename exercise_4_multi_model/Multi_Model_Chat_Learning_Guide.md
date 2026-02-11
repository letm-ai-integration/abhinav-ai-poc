# Multi-Model Chat System

## 1. The Problem: Why Multiple Models?

In previous exercises, we used a single LLM provider. But relying on one provider is limiting:

| Problem | Why It Matters |
|---------|---------------|
| **Vendor lock-in** | If one provider has an outage, your app goes down |
| **Cost** | Different providers have different pricing |
| **Model strengths** | Some models are better at code, others at reasoning |
| **Privacy** | Some data can't leave your network — local models solve this |
| **Experimentation** | Compare outputs side-by-side to pick the best model |

> **Think of it this way:**
> - **Single model:** A restaurant with one chef — if they're sick, no food.
> - **Multi-model:** Multiple chefs, each specializing in different cuisines, with backup always available.

---

## 2. What We Built

A **production-style chat application** with:
- A **FastAPI backend** that routes requests to multiple LLM providers
- A **Streamlit frontend** for interactive chat with provider selection
- An **abstract model layer** for clean provider switching

### Architecture

```
┌──────────────────┐         ┌──────────────────────────┐
│   Streamlit UI   │  HTTP   │     FastAPI Backend       │
│                  │ ──────→ │                           │
│ - Provider select│         │  POST /chat               │
│ - Chat interface │         │  GET  /providers           │
│ - Temperature    │         │                           │
│                  │ ←────── │  ┌──────┐ ┌───────────┐  │
└──────────────────┘         │  │ Groq │ │HuggingFace│  │
                             │  └──────┘ └───────────┘  │
                             │  ┌──────┐                 │
                             │  │Ollama│                 │
                             │  └──────┘                 │
                             └──────────────────────────┘
```

---

## 3. Core Concepts

### 3.1 Strategy Pattern — Abstract Base Model

The key design pattern: define a **common interface** and let each provider implement it differently. The rest of the app never knows which provider it's talking to.

```python
class BaseModel(ABC):
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        pass
```

- Every provider (Groq, HuggingFace, Ollama) extends `BaseModel`
- They all implement `generate()` and `is_available()` their own way
- Adding a new provider = one new class, no changes to existing code

### 3.2 The Three Providers

| Provider | Type | Key Feature | Authentication |
|----------|------|-------------|---------------|
| **Groq** | Cloud API | Extremely fast (custom LPU hardware) | API key |
| **HuggingFace** | Cloud API | Thousands of open-source models | API token |
| **Ollama** | Local | Data stays on your machine, free | None (just `ollama serve`) |

Each provider wraps its SDK in the same `BaseModel` interface:
- **Groq** uses the `groq` Python SDK
- **HuggingFace** uses `huggingface_hub.InferenceClient`
- **Ollama** uses the `ollama` Python library

### 3.3 Configuration

All credentials and settings are managed through **environment variables** and a centralized `Config` class.

```env
# .env file
GROQ_API_KEY=gsk_your_key_here
HUGGINGFACE_API_TOKEN=hf_your_token_here
OLLAMA_BASE_URL=http://localhost:11434
```

The config class loads these values and provides a `validate()` method that reports which providers are configured.

### 3.4 FastAPI Backend

**Two endpoints:**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/chat` | POST | Send a prompt to a specific provider, get a response |
| `/providers` | GET | List all providers with their availability status |

**Request/Response schemas** use Pydantic models:
- `ChatRequest` — provider name, prompt, optional temperature and max_tokens
- `ChatResponse` — provider, model name, response text, optional error

The backend validates the provider exists, checks availability, then calls `provider.generate()`.

### 3.5 Streamlit Frontend

The frontend provides an interactive chat UI:

| Component | What It Does |
|-----------|-------------|
| **Sidebar** | Shows provider status (green/yellow), selection dropdown, temperature slider |
| **Chat area** | Message history with user/assistant bubbles |
| **Provider caption** | Shows which provider/model generated each response |
| **Session state** | Preserves chat history across Streamlit reruns |

---

## 4. How It All Fits Together

### Startup
1. Backend starts → checks which providers are configured
2. Frontend starts → calls `GET /providers` → shows available models

### Chat Flow
1. User types a message and selects a provider
2. Frontend sends `POST /chat` with provider, prompt, temperature
3. Backend validates provider → calls `provider.generate(prompt)`
4. Provider SDK makes the actual API call (or local Ollama call)
5. Response flows back → user sees the message with provider attribution

---

## 5. Key Design Patterns

| Pattern | Where | Why |
|---------|-------|-----|
| **Strategy Pattern** | BaseModel + providers | Swap providers without changing app logic |
| **API Gateway** | FastAPI routes | Single entry point routing to the right provider |
| **Request/Response Schemas** | Pydantic models | Type-safe API contracts |
| **Environment Config** | Config class + `.env` | Credentials separated from code |

---

## 6. Dependencies

| Package | Purpose |
|---------|---------|
| **fastapi** | Web framework for the REST API |
| **uvicorn** | ASGI server to run FastAPI |
| **groq** | Groq API client |
| **huggingface_hub** | HuggingFace Inference API client |
| **ollama** | Ollama Python client (local models) |
| **python-dotenv** | Load env variables from `.env` |
| **streamlit** | Interactive web UI framework |
| **requests** | HTTP client (frontend → backend) |
| **pydantic** | Data validation (included with FastAPI) |

---

## 7. Quick Reference

| Concept | What It Is |
|---------|-----------|
| **BaseModel (ABC)** | Abstract class all providers must implement |
| **Strategy Pattern** | Different implementations sharing a common interface |
| **Provider** | An LLM service wrapped in a BaseModel class |
| **FastAPI** | Python web framework for building REST APIs |
| **Pydantic** | Data validation for request/response schemas |
| **`is_available()`** | Checks if a provider is configured and reachable |
| **Streamlit Session State** | Preserves data (chat history) across UI reruns |
| **Temperature** | Controls randomness (0 = deterministic, 1 = creative) |
| **Ollama** | Local LLM server — free, private, no API key |
| **Groq** | Cloud provider with fast custom hardware (LPU) |
| **HuggingFace** | Cloud platform with thousands of open-source models |

---
