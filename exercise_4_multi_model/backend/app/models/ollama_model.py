import ollama
from .base_model import BaseModel
from app.config import config

class OllamaModel(BaseModel):
    def __init__(self, model_name: str = None):
        super().__init__(model_name or config.OLLAMA_MODEL)
        self.base_url = config.OLLAMA_BASE_URL

    def generate(self, prompt: str, **kwargs) -> str:
        try:
            temperature = kwargs.get("temperature", 0.7)

            response = ollama.chat(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                options={
                    "temperature": temperature
                }
            )

            return response['message']['content']

        except Exception as e:
            error_msg = str(e)

            if "connection" in error_msg.lower():
                return "Error: Cannot connect to Ollama. Make sure Ollama is running (try 'ollama serve' in terminal)."
            elif "model" in error_msg.lower():
                return f"Error: Model '{self.model_name}' not found. Run 'ollama pull {self.model_name}' to download it."
            else:
                return f"Error calling Ollama: {error_msg}"

    def is_available(self) -> bool:
        try:
            ollama.list()
            return True
        except Exception:
            return False

    def get_info(self) -> dict:
        info = super().get_info()
        info["available"] = self.is_available()
        info["base_url"] = self.base_url

        try:
            models = ollama.list()
            info["installed_models"] = [m['name'] for m in models.get('models', [])]
        except Exception:
            info["installed_models"] = []

        return info
