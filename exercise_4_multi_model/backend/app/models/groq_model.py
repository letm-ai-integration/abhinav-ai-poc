from groq import Groq
from .base_model import BaseModel
from app.config import config

class GroqModel(BaseModel):

    def __init__(self, model_name: str = None):
        super().__init__(model_name or config.GROQ_MODEL)
        self.client = None

        if config.GROQ_API_KEY:
            try:
                self.client = Groq(api_key=config.GROQ_API_KEY)
            except Exception as e:
                print(f"Failed to initialize Groq client: {e}")

    def generate(self, prompt: str, **kwargs) -> str:
        if not self.client:
            return "Error: Groq client not initialized. Check your API key."

        try:
            temperature = kwargs.get("temperature", 0.7)
            max_tokens = kwargs.get("max_tokens", 1024)

            # Make API call
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"Error calling Groq API: {str(e)}"

    def is_available(self) -> bool:
        return self.client is not None and bool(config.GROQ_API_KEY)

    def get_info(self) -> dict:
        info = super().get_info()
        info["available"] = self.is_available()
        info["api_key_set"] = bool(config.GROQ_API_KEY)
        return info
