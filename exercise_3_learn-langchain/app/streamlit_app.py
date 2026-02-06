import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# PAGE CONFIGURATION
st.set_page_config(
    page_title="🍽️ Restaurant Concept Generator",
    page_icon="🍽️",
    layout="centered"
)

from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_classic.chains import LLMChain, SequentialChain


# CREATE LANGCHAIN COMPONENTS
@st.cache_resource
def get_chain():
    llm = OllamaLLM(model="llama3.2", temperature=0.8)
    
    # Chain 1: Generate restaurant name
    name_prompt = PromptTemplate(
        input_variables=["cuisine"],
        template="""
        You are a creative restaurant naming expert.
        Suggest ONE unique and memorable name for a {cuisine} restaurant.
        Just the name, nothing else.
        """
    )
    name_chain = LLMChain(llm=llm, prompt=name_prompt, output_key="restaurant_name")
    
    # Chain 2: Generate menu
    menu_prompt = PromptTemplate(
        input_variables=["restaurant_name", "cuisine"],
        template="""
        You are a menu designer for {restaurant_name}, a {cuisine} restaurant.
        
        Create an appetizing menu with exactly 5 signature dishes.
        For each dish include:
        - Creative name
        - Brief, mouth-watering description
        - Price ($)
        
        Format it beautifully.
        """
    )
    menu_chain = LLMChain(llm=llm, prompt=menu_prompt, output_key="menu")
    
    # Combine into sequential chain
    full_chain = SequentialChain(
        chains=[name_chain, menu_chain],
        input_variables=["cuisine"],
        output_variables=["restaurant_name", "menu"]
    )
    
    return full_chain


# STREAMLIT UI
def main():
    """Main Streamlit application."""
    
    # Header
    st.title("🍽️ Restaurant Concept Generator")
    st.markdown("""
    *Powered by LangChain + Ollama (Local LLM)*
    
    Enter a cuisine type and get a creative restaurant name plus a custom menu!
    """)
    
    st.divider()
    
    # Input section
    st.subheader("🌍 Choose Your Cuisine")
    
    # Two ways to input - dropdown or custom text
    col1, col2 = st.columns(2)
    
    with col1:
        preset_cuisines = [
            "Select a cuisine...",
            "Italian", "Japanese", "Mexican", "Indian", "Thai",
            "French", "Chinese", "Greek", "Korean", "Vietnamese"
        ]
        selected = st.selectbox("Popular cuisines:", preset_cuisines)
    
    with col2:
        custom = st.text_input("Or enter your own:", placeholder="e.g., Ethiopian")
    
    # Determine which cuisine to use
    cuisine = custom if custom else (selected if selected != "Select a cuisine..." else None)
    
    # Generate button
    st.divider()
    
    if st.button("✨ Generate Restaurant Concept", type="primary", disabled=not cuisine):
        if cuisine:
            with st.spinner(f"Creating your {cuisine} restaurant concept..."):
                try:
                    # Get the chain and run it
                    chain = get_chain()
                    result = chain.invoke({"cuisine": cuisine})
                    
                    # Display results
                    st.success("Restaurant concept created!")
                    
                    # Restaurant name in a nice box
                    st.subheader("🏪 Restaurant Name")
                    st.markdown(f"## {result['restaurant_name'].strip()}")
                    
                    # Menu
                    st.subheader("📜 Signature Menu")
                    st.markdown(result['menu'])
                    
                    # Add some interaction
                    st.divider()
                    st.markdown("*Like this concept? Try another cuisine!*")
                    
                except Exception as e:
                    st.error(f"Error generating concept: {e}")
    
    elif not cuisine:
        st.info("👆 Select or enter a cuisine type to get started!")
    
    # Footer with explanation
    st.divider()
    with st.expander("🎓 How does this work?"):
        st.markdown("""
        This app uses **LangChain's Sequential Chain** pattern:
        
        1. **Chain 1: Name Generator**
           - Takes your cuisine choice
           - Uses GPT to create a creative restaurant name
           
        2. **Chain 2: Menu Generator**  
           - Takes the name from Chain 1 + your cuisine
           - Uses GPT to create matching menu items
        
        **The flow:**
        ```
        Your Input (cuisine)
              ↓
        [Name Chain] → restaurant_name
              ↓
        [Menu Chain] → menu items
              ↓
        Display Results
        ```
        
        This is called **chaining** - one LLM call's output becomes
        the next call's input!
        """)

if __name__ == "__main__":
    main()
