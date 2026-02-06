"""""
THE RAG PATTERN
---------------
Without RAG:
  User Question → LLM → Answer (based only on training data)

With RAG:
  User Question → Retrieve Context → LLM (with context) → Answer

The LLM gets additional context, so it can answer questions about
information that wasn't in its training data.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

class LLMClient:
    def __init__(self, api_key: str = None):
        load_dotenv()
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

        if not self.api_key:
            raise ValueError(
                "No API key provided."
            )
        
        self.client = OpenAI(api_key=self.api_key)
        self.default_model = "gpt-4o-mini"

    def generate(
        self,
        prompt: str,
        system_prompt: str = None,
        max_tokens: int = 1024,
        temperature: float = 0.7
    ) -> str:
        messages = [
            {"role": "system", "content": system_prompt or "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]

        response = self.client.chat.completions.create(
            model=self.default_model,
            max_tokens=max_tokens,
            messages=messages,
            temperature=temperature
        )

        return response.choices[0].message.content
    
    def generate_with_context(
        self,
        question: str,
        context: str,
        max_tokens: int = 1024
    ) -> str:
        system_prompt = """You are a helpful assistant that answers questions based on the provided context.

Instructions:
- Use ONLY the information in the provided context to answer questions
- If the context doesn't contain enough information, say so
- Be concise and direct in your answers
- If you quote from the context, indicate that you're doing so"""

        prompt = f"""Context information:
---
{context}
---

Based on the above context, please answer this question:
{question}"""
        
        return self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=0.3  # Lower temperature for more factual responses
        )
    
if __name__ == "__main__":
    try:
        llm = LLMClient()
        print("LLM initialized successfully!")
        
        question = "What is Python in one sentence?"
        print(f"Question: {question}")
        response = llm.generate(question)
        print(f"Response: {response}")
        
        # Test RAG-style generation with context 
        context = """
        Acme Corp was founded in 2020 by Jane Smith.
        The company specializes in AI-powered widgets.
        Their headquarters is located in San Francisco.
        They have 150 employees as of 2024.
        """ 
        question = "Where is Acme Corp located and who founded it?"
        print(f"Question: {question}")
        print(f"Context: (provided company info)")
        response = llm.generate_with_context(question, context)
        print(f"Response: {response}")
        
    except ValueError as e:
        print(f"\nError: {e}")