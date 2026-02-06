import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.utils.config import setup_environment

# Set up environment (load API key)
setup_environment()

# Import LangChain components
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_classic.chains import LLMChain

# Create the LLM object
def create_llm(temperature=0.7):
    llm = OllamaLLM(
        model="llama3.2",
        temperature=temperature,
    )
    return llm

# Create a Prompt Template
def create_restaurant_name_prompt():
    template = """
    You are a creative restaurant naming expert.
    
    I want to open a restaurant that serves {cuisine} cuisine.
    Suggest ONE creative and memorable name for this restaurant.
    
    Just provide the name, nothing else.
    """
    
    prompt = PromptTemplate(
        input_variables=["cuisine"],
        template=template
    )
    
    return prompt


# Create a Chain (combine LLM + Prompt)
def create_name_chain():
    llm = create_llm(temperature=0.8)
    prompt = create_restaurant_name_prompt()
    
    chain = LLMChain(
        llm=llm,
        prompt=prompt,
        verbose=True
    )
    
    return chain


# Run the chain!
def generate_restaurant_name(cuisine: str) -> str:
    chain = create_name_chain()
    
    result = chain.invoke({"cuisine": cuisine})
    
    return result["text"].strip()


# Test the chain
if __name__ == "__main__":
    print("LangChain Basic Chain Demo: Restaurant Name Generator")
    
    # Test with different cuisines
    cuisines = ["Italian", "Japanese", "Mexican", "Indian", "French"]
    
    for cuisine in cuisines:
        print(f"\nGenerating name for {cuisine} restaurant...")
        print("-" * 40)
        
        try:
            name = generate_restaurant_name(cuisine)
            print(f"Generated name: {name}")
        except Exception as e:
            print(f"Error: {e}")
            print("Make sure your Ollama is running!")
            break
    
    print("Demo complete!")
