import os
from dotenv import load_dotenv


def setup_environment():

    load_dotenv()
    
    # api_key = os.getenv("OPENAI_API_KEY")
    
    # if not api_key:
    #     print("WARNING: OPENAI_API_KEY not found!")
    #     return False
    
    print("Using Ollama (local LLM) - no API key needed!")
    return True

# def get_api_key():
#     return os.getenv("OPENAI_API_KEY")

def get_ollama_model():
    return os.getenv("OLLAMA_MODEL", "llama3.2")

if __name__ == "__main__":
    setup_environment()