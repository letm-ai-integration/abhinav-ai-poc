import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.utils.config import setup_environment

setup_environment()

from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_classic.chains import ConversationChain
from langchain_classic.memory import (
    ConversationBufferMemory,
    ConversationSummaryMemory,
    ConversationBufferWindowMemory #
)


# Buffer Memory (Store Everything)
def demo_buffer_memory():
    print("\nBuffer Memory Demo")
    
    memory = ConversationBufferMemory()
    
    llm = OllamaLLM(model="llama3.2", temperature=0.7)
    
    conversation = ConversationChain(
        llm=llm,
        memory=memory,
        verbose=True
    )
    
    print("\nStarting conversation...")
    
    response1 = conversation.predict(input="Hi! My name is Abhinav.")
    print(f"AI: {response1}")
    
    response2 = conversation.predict(input="What's a good project for learning AI?")
    print(f"AI: {response2}")
    
    response3 = conversation.predict(input="What was my name again?")
    print(f"AI: {response3}")
    
    print("\nMemory contents:")
    print(memory.buffer)


# Window Memory (Last K Messages)
def demo_window_memory():
    print("\nWindow Memory Demo (k=2)")
    
    memory = ConversationBufferWindowMemory(k=2)
    
    llm = OllamaLLM(model="llama3.2", temperature=0.7)
    conversation = ConversationChain(llm=llm, memory=memory, verbose=True)
    
    conversation.predict(input="My favorite color is blue.")
    conversation.predict(input="My favorite food is chole bhature.")
    conversation.predict(input="My favorite movie is Shawshank Redemption.")
    
    response = conversation.predict(input="What's my favorite color?")
    print(f"\nAI (might not remember!): {response}")
    
    print("\nMemory only has last 2 exchanges:")
    print(memory.buffer)


# Summary Memory (Compress Old Messages)
def demo_summary_memory():
    print("\nSummary Memory Demo")
    
    llm = OllamaLLM(model="llama3.2", temperature=0.7)
    
    memory = ConversationSummaryMemory(llm=llm)
    
    conversation = ConversationChain(llm=llm, memory=memory, verbose=True)
    
    conversation.predict(
        input="I'm building a RAG system with FAISS and sentence-transformers."
    )
    conversation.predict(
        input="I want to add PDF support using pdfplumber."
    )
    conversation.predict(
        input="The chunking strategy uses 500 characters with 50 overlap."
    )
    
    print("\nSummary of conversation:")
    print(memory.buffer)


# CUSTOM MEMORY: Adding Memory to Any Chain
def demo_custom_chain_with_memory():
    print("\nCustom Chain with Memory")
    
    from langchain_classic.chains import LLMChain
    
    llm = OllamaLLM(model="llama3.2", temperature=0.7)
    
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=False
    )
    
    prompt = PromptTemplate(
        input_variables=["chat_history", "input"],
        template="""
        You are a helpful restaurant advisor.
        
        Previous conversation:
        {chat_history}
        
        Human: {input}
        AI: """
    )
    
    chain = LLMChain(
        llm=llm,
        prompt=prompt,
        memory=memory,
        verbose=True
    )
    
    result1 = chain.predict(input="I don't love spicy food")
    print(f"AI: {result1}")
    
    result2 = chain.predict(input="What kind of restaurant should I try?")
    print(f"AI: {result2}")


if __name__ == "__main__":
    print("LangChain Memory Demo")

    
    try:
        # demo_buffer_memory()
        # demo_window_memory()
        # demo_summary_memory()
        demo_custom_chain_with_memory()
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure your Ollama is running!")
