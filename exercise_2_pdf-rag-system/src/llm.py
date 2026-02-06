import os
from openai import OpenAI
from dotenv import load_dotenv


class LLMClient:
    def __init__(self, api_key: str = None):
        load_dotenv()
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError("No OpenAI API key. Set OPENAI_API_KEY in .env file.")
        
        self.client = OpenAI(api_key=self.api_key)
    
    def generate_answer(self, question: str, context: str) -> str:
        system_prompt = """Answer questions based on the provided context.
- Use only information from the context
- If the context doesn't have the answer, say so
- Be concise"""

        prompt = f"""Context:
{context}

Question: {question}

Answer:"""
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        return response.choices[0].message.content


if __name__ == "__main__":
    try:
        llm = LLMClient()
        
        context = "Chelsea is a football club based in London."
        # question = "Where is Chelsea based?"
        question = "Where is AC Milan based?"
        
        answer = llm.generate_answer(question, context)
        print(f"Q: {question}\nA: {answer}")
    except ValueError as e:
        print(f"Error: {e}")
