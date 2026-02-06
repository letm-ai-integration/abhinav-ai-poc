from pydantic import BaseModel
from typing import Optional, Dict, Any


class ChatRequest(BaseModel):
    provider: str
    prompt: str
    model_name: Optional[str] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1024


class ChatResponse(BaseModel):
    provider: str
    model: str
    response: str
    error: Optional[str] = None


class ProviderInfo(BaseModel):
    provider: str
    available: bool
    details: Dict[str, Any]
