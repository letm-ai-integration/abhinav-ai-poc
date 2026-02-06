import os
from dotenv import load_dotenv

load_dotenv()

class Config:
  # Groq Configuration
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL = "openai/gpt-oss-120b"

    # Hugging Face Configuration
    HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN", "")
    HUGGINGFACE_MODEL = "meta-llama/Meta-Llama-3-8B-Instruct"

    # Ollama Configuration
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = "llama2"

    # API Configuration
    API_HOST = "0.0.0.0"
    API_PORT = 8000

    @classmethod
    def validate(cls):
        issues = []

        if not cls.GROQ_API_KEY:
            issues.append("GROQ_API_KEY not set - Groq models will not work")

        if not cls.HUGGINGFACE_API_TOKEN:
            issues.append("HUGGINGFACE_API_TOKEN not set - HuggingFace models will not work")

        return issues

config = Config()
