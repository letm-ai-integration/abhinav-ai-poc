from fastapi import APIRouter, HTTPException

from app.schemas import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Generate a chat response using the specified provider

    Args:
        request: ChatRequest with provider, prompt, and optional parameters

    Returns:
        ChatResponse with the generated text
    """
    from app import model_providers

    if request.provider not in model_providers:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid provider '{request.provider}'. Available: {list(model_providers.keys())}"
        )

    provider = model_providers[request.provider]

    if not provider.is_available():
        raise HTTPException(
            status_code=503,
            detail=f"Provider '{request.provider}' is not available. Check configuration."
        )

    if request.model_name:
        provider.model_name = request.model_name

    try:
        response_text = provider.generate(
            request.prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )

        return ChatResponse(
            provider=request.provider,
            model=provider.model_name,
            response=response_text
        )

    except Exception as e:
        return ChatResponse(
            provider=request.provider,
            model=provider.model_name,
            response="",
            error=str(e)
        )