import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.utils.config import setup_environment

setup_environment()

from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_classic.chains import LLMChain, SequentialChain


# Generate Restaurant Name
def create_name_chain():
    llm = OllamaLLM(model="llama3.2", temperature=0.8)
    
    prompt = PromptTemplate(
        input_variables=["cuisine"],
        template="""
        You are a creative restaurant naming expert.
        
        Suggest ONE creative name for a {cuisine} restaurant.
        Just the name, nothing else.
        """
    )
    
    return LLMChain(
        llm=llm,
        prompt=prompt,
        output_key="restaurant_name"
    )


# Generate Menu Items
def create_menu_chain():

    llm = OllamaLLM(model="llama3.2", temperature=0.7)
    
    prompt = PromptTemplate(
        input_variables=["restaurant_name", "cuisine"],
        template="""
        You are a menu designer for {restaurant_name}, a {cuisine} restaurant.
        
        Create a short menu with exactly 5 dishes. For each dish, provide:
        - Name of the dish
        - Brief description (one line)
        - Price
        
        Format it nicely.
        """
    )
    
    return LLMChain(
        llm=llm,
        prompt=prompt,
        output_key="menu_items"
    )


# COMBINE INTO SEQUENTIAL CHAIN
def create_restaurant_concept_chain():
    chain1 = create_name_chain()
    chain2 = create_menu_chain()
    
    # Combine into a sequence
    full_chain = SequentialChain(
        chains=[chain1, chain2],
        input_variables=["cuisine"],
        output_variables=["restaurant_name", "menu_items"],
        verbose=True
    )
    
    return full_chain


# Test the chains
def generate_restaurant_concept(cuisine: str) -> dict:
    chain = create_restaurant_concept_chain()
    result = chain.invoke({"cuisine": cuisine})
    return result


if __name__ == "__main__":
    
    print("Full SequentialChain (Name + Menu)")
    
    try:
        result = generate_restaurant_concept("Indian")
        
        print(f"\nRestaurant Name: {result['restaurant_name'].strip()}")
        print(f"\nMenu:")
        print(result['menu_items'])
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure your Ollama is running!")
