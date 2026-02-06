import pdfplumber
from pathlib import Path


def load_pdf(pdf_path: str, chunk_size: int = 500, overlap: int = 50) -> list[dict]:
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    
    chunks = []
    chunk_index = 0
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if not text:
                continue
            
            # Split page text into chunks
            start = 0
            while start < len(text):
                end = start + chunk_size
                chunk_text = text[start:end].strip()
                
                if chunk_text:
                    chunks.append({
                        "text": chunk_text,
                        "page": page_num,
                        "chunk": chunk_index,
                        "source": pdf_path.name
                    })
                    chunk_index += 1
                
                start = end - overlap
    
    return chunks


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        chunks = load_pdf(sys.argv[1])
        print(f"Extracted {len(chunks)} chunks")
        if chunks:
            print(f"\nFirst chunk:\n{chunks[0]['text'][:200]}...")
    else:
        print("Usage: python pdf_loader.py <pdf_path>")
