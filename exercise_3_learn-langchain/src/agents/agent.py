import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.utils.config import setup_environment

setup_environment()

from langchain.agents import create_agent
from langchain.tools import tool


# Simple Custom Tools
# Create tools using the @tool decorator
@tool
def get_word_count(text: str) -> int:
    """Count the number of words in the given text."""
    return len(text.split())


@tool
def get_current_times() -> str:
    """Get the current date and time."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@tool
def calculate(expression: str) -> str:
    """Evaluate a math expression and return the result."""
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error: {e}"


# CREATING AN AGENT
def create_simple_agent():
    tools = [
        get_word_count,
        get_current_times,
        calculate
    ]

    return create_agent("ollama:llama3.2", tools=tools)


# Wikipedia Tool (Built-in)
def create_wikipedia_agent():
    try:
        from langchain_community.tools import WikipediaQueryRun
        from langchain_community.utilities import WikipediaAPIWrapper
    except ImportError:
        print("Install: wikipedia-api langchain-community")
        return None
    
    # Create Wikipedia tool
    wikipedia = WikipediaQueryRun(
        api_wrapper=WikipediaAPIWrapper(
            top_k_results=1,
            doc_content_chars_max=1000
        )
    )

    tools = [wikipedia, calculate]

    return create_agent("ollama:llama3.2", tools=tools)


# Restaurant Recommendation Agent
def create_restaurant_agent():    
    # Domain-specific tools
    @tool
    def get_cuisine_info(cuisine: str) -> str:
        """Get information about a specific cuisine type."""
        cuisines = {
            "indian": "Indian cuisine varies by region, known for curries, tandoori, and extensive spice usage.",
            "italian": "Italian cuisine features pasta, pizza, olive oil, and fresh ingredients. Known for regional diversity.",
            "japanese": "Japanese cuisine emphasizes fresh, seasonal ingredients. Known for sushi, ramen, and umami flavors.",
            "mexican": "Mexican cuisine is rich in spices, featuring tacos, enchiladas, and complex mole sauces.",
            "thai": "Thai cuisine balances sweet, sour, salty, and spicy. Known for curries and stir-fries.",
        }
        return cuisines.get(cuisine.lower(), f"I don't have specific info about {cuisine} cuisine.")
    
    @tool
    def suggest_restaurant_name(cuisine: str) -> str:
        """Suggest a restaurant name for the given cuisine type."""
        import random
        prefixes = {
            "italian": ["La Bella", "Trattoria", "Casa", "Il"],
            "japanese": ["Sakura", "Zen", "Koi", "Hana"],
            "mexican": ["Casa", "El", "La Cantina", "Taqueria"],
            "indian": ["Spice", "Tandoor", "Masala", "Curry"],
            "thai": ["Golden", "Lotus", "Bangkok", "Siam"],
        }
        suffixes = ["Garden", "House", "Kitchen", "Table", "Room"]
        
        prefix = random.choice(prefixes.get(cuisine.lower(), ["The"]))
        suffix = random.choice(suffixes)
        return f"{prefix} {suffix}"
    
    tools = [get_cuisine_info, suggest_restaurant_name, calculate]

    return create_agent("ollama:llama3.2", tools=tools)


if __name__ == "__main__":
    print("LangChain Agents Demo")
    
    print("TEST 1: Simple Agent with Custom Tools")
    
    try:
        agent = create_simple_agent()
        
        result = agent.invoke({
            "messages": [{"role": "user", "content": "What is 25 times 17?"}]
        })
        print(f"\nFinal Answer: {result['messages'][-1].content}")

        result = agent.invoke({
            "messages": [{"role": "user", "content": "What time is it right now?"}]
        })
        print(f"\nFinal Answer: {result['messages'][-1].content}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "-"*60)
    print("TEST 2: Wikipedia Agent")

    try:
        wiki_agent = create_wikipedia_agent()
        if wiki_agent:
            result = wiki_agent.invoke({
                "messages": [{"role": "user", "content": "Tell me about Albert Einstein"}]
            })
            print(f"\nFinal Answer: {result['messages'][-1].content}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n" + "-"*60)
    print("TEST 3: Restaurant Recommendation Agent")
    
    try:
        restaurant_agent = create_restaurant_agent()
        
        result = restaurant_agent.invoke({
            "messages": [{"role": "user", "content": "I want to open an Italian restaurant. Tell me about Italian cuisine and suggest a name."}]
        })
        print(f"\nFinal Answer: {result['messages'][-1].content}")
        
    except Exception as e:
        print(f"Error: {e}")
