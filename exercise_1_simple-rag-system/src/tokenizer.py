import tiktoken

class SimpleTokenizer:
    def __init__(self, encoding_name: str = "cl100k_base"):
        self.encoding = tiktoken.get_encoding(encoding_name)
        self.encoding_name = encoding_name

    def tokenize(self, text: str) -> list[int]:
        return self.encoding.encode(text)
    
    def detokenize(self, tokens: list[int]) -> str:
        return self.encoding.decode(tokens)
    
    def get_tokens_as_strings(self, text: str) -> list[str]:
        token_ids = self.tokenize(text)
        return [self.encoding.decode([token_id]) for token_id in token_ids]
    
    def count_tokens(self, text: str) -> int:
        return len(self.tokenize(text))
    
if __name__ == "__main__":
    tokenizer = SimpleTokenizer()

    examples = [
        "Learning AI and LLMs",
        "Tokens are the basic units that language models work with.",
        "Tokenization is the process of converting raw text into these tokens."
    ]

    for text in examples:
        tokens = tokenizer.tokenize(text)
        detokenized_text = tokenizer.detokenize(tokens)
        token_strings = tokenizer.get_tokens_as_strings(text)
        token_count = tokenizer.count_tokens(text)

        print(f"Original Text: {text}")
        print(f"Token IDs: {tokens}")
        print(f"Detokenized Text: {detokenized_text}")
        print(f"Token Strings: {token_strings}")
        print(f"Token Count: {token_count}")