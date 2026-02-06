from fastapi import APIRouter, HTTPException

from app.config import config

router = APIRouter()


@router.get("/")
async def root():
    """Root endpoint - API info"""
    from app import model_providers

    return {
        "message": "Multi-Model Chat API",
        "version": "1.0.0",
        "providers": list(model_providers.keys())
    }


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@router.get("/providers")
async def list_providers():
    """List all available model providers and their status"""
    from app import model_providers

    providers_info = []

    for name, provider in model_providers.items():
        providers_info.append({
            "name": name,
            "available": provider.is_available(),
            "info": provider.get_info()
        })

    return {"providers": providers_info}


@router.get("/providers/{provider_name}")
async def get_provider_info(provider_name: str):
    """Get detailed information about a specific provider"""
    from app import model_providers

    if provider_name not in model_providers:
        raise HTTPException(
            status_code=404,
            detail=f"Provider '{provider_name}' not found. Available: {list(model_providers.keys())}"
        )

    provider = model_providers[provider_name]
    return {
        "name": provider_name,
        "available": provider.is_available(),
        "info": provider.get_info()
    }


@router.get("/config/validate")
async def validate_config():
    """Validate configuration and return any issues"""
    issues = config.validate()

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "config": {
            "groq_configured": bool(config.GROQ_API_KEY),
            "huggingface_configured": bool(config.HUGGINGFACE_API_TOKEN),
            "ollama_url": config.OLLAMA_BASE_URL
        }
    }
