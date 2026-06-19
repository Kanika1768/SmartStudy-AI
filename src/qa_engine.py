import os
import chromadb
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key=os.getenv("GEMINI_API_KEY")
client=genai.Client(api_key=api_key)



chroma_client=chromadb.Client()
collection=chroma_client.create_collection(name="study_notes")

def get_embedding(text):
    result=client.models.embed_content(
        model="gemini-embedding-001",
        contents=[text]
    )
    return result.embeddings[0].values

def store_chunks(chunks):
    for i,chunk in enumerate(chunks):
        embedding=get_embedding(chunk)
        collection.add(
            ids=[str(i)],
            documents=[chunk],
            embeddings=[embedding]
        )

def retrieve_relevant_chunks(question):
    question_embedding=get_embedding(question)
    results=collection.query(
        query_embeddings=[question_embedding],
        n_results=1
    )
    return results['documents'][0][0]

def answer_question(question):
    relevant_chunk=retrieve_relevant_chunks(question)
    prompt=f"""
    Answer the following question using ONLY the context below.
    If the answer is'nt in the context, say "i dont know based on provided notes"
    
    Context:{relevant_chunk}
    Question:{question}
    """
    response = client.models.generate_content(
    model="gemini-2.5-flash-lite",
    contents=prompt
    )
    return response.text

if __name__=="__main__":
    from pdf_processor import extract_text_from_pdf, chunk_text as chunk_fn

    text=extract_text_from_pdf("../test.pdf")
    chunks=chunk_fn(text)
    store_chunks(chunks)

    answer=answer_question("Meaning of KanikaS")
    print(answer)
    # relevant_chunk=retrieve_relevant_chunks(question)

    # print("Most relevant chunk found:\n", relevant_chunk)




