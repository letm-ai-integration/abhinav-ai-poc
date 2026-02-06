from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.models import GroqModel, HuggingFaceModel, OllamaModel
from app.routes import chat_router, providers_router

app = FastAPI(
    title="Multi-Model Chat API",
    description="API for chatting with multiple LLM providers (Groq, HuggingFace, Ollama)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model_providers = {
    "groq": GroqModel(),
    "huggingface": HuggingFaceModel(),
    "ollama": OllamaModel()
}

app.include_router(chat_router)
app.include_router(providers_router)
