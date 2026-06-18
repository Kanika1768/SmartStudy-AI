# src/pdf_processor.py
import PyPDF2

def extract_text_from_pdf(pdf_path):
    reader = PyPDF2.PdfReader(pdf_path)
    all_text = ""
    for page in reader.pages:
        res = page.extract_text()
        if res:
            all_text += res
    return all_text

def chunk_text(text, chunk_size=500):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i+chunk_size])
        chunks.append(chunk)
    return chunks

if __name__ == "__main__":
    # if __name__ == "__main__": means: when you run python pdf_processor.py directly, 
    # that block executes. But when another file does from src.pdf_processor import extract_text_from_pdf, 
    # that block is skipped entirely. This is THE standard way Python separates "code to run when this file is the main program" from "code to use as a library." 
    # This is genuinely a common interview question: "What does if __name__ == '__main__' do and why use it?"
    text = extract_text_from_pdf("test.pdf")
    print(len(text))
    print(text[:300])
    chunks = chunk_text(text)
    print("Number of chunks:", len(chunks))
    print(chunks[0][:200])