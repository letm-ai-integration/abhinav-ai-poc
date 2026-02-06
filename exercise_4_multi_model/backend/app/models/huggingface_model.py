from huggingface_hub import InferenceClient
from .base_model import BaseModel
from app.config import config

class HuggingFaceModel(BaseModel):
    def __init__(self, model_name: str = None):
        super().__init__(model_name or config.HUGGINGFACE_MODEL)
        self.client = None

        if config.HUGGINGFACE_API_TOKEN:
            try:
                self.client = InferenceClient(
                    model=self.model_name,
                    token=config.HUGGINGFACE_API_TOKEN
                )
            except Exception as e:
                print(f"Failed to initialize HuggingFace client: {e}")

    def generate(self, prompt: str, **kwargs) -> str:
        if not self.client:
            return "Error: HuggingFace client not initialized. Check your API token."

        try:
            temperature = kwargs.get("temperature", 0.7)
            max_tokens = kwargs.get("max_tokens", 1024)

            response = self.client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"Error calling HuggingFace API: {str(e)}"

    def is_available(self) -> bool:
        return self.client is not None and bool(config.HUGGINGFACE_API_TOKEN)

    def get_info(self) -> dict:
        info = super().get_info()
        info["available"] = self.is_available()
        info["api_token_set"] = bool(config.HUGGINGFACE_API_TOKEN)
        return info
