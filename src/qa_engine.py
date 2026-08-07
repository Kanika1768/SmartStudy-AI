import os
import time
import chromadb
from google import genai
from dotenv import load_dotenv

# -------------------------
# Configuration
# -------------------------

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# -------------------------
# ChromaDB Setup
# -------------------------

chroma_client = chromadb.Client()

collection = chroma_client.get_or_create_collection(
    name="study_notes"
)

# -------------------------
# Embedding Model
# -------------------------

def get_embedding(text):
    """
    Generate embedding using Gemini Embedding Model.
    """

    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=[text]
    )

    return result.embeddings[0].values


# -------------------------
# Store Chunks
# -------------------------

def store_chunks(chunks):
    """
    Store document chunks along with metadata.

    Metadata:
    - document name
    - page number
    """

    for i, chunk in enumerate(chunks):

        try:

            embedding = get_embedding(chunk["text"])

            collection.add(
                ids=[
                    f'{chunk["document"]}_{chunk["page"]}_{i}'
                ],

                documents=[
                    chunk["text"]
                ],

                embeddings=[
                    embedding
                ],

                metadatas=[
                    {
                        "page": chunk["page"],
                        "document": chunk["document"]
                    }
                ]
            )

            # Prevent API rate limits
            time.sleep(1)

        except Exception as e:

            print(f"Error storing chunk {i}: {e}")

            time.sleep(5)


# -------------------------
# Retrieve Relevant Chunks
# -------------------------

def retrieve_relevant_chunks(question, top_k=5):
    """
    Retrieve Top-K most relevant chunks.
    """

    question_embedding = get_embedding(question)

    results = collection.query(

        query_embeddings=[question_embedding],

        n_results=top_k,

        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    retrieved_chunks = []

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for doc, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):

        retrieved_chunks.append({

            "text": doc,

            "page": metadata["page"],

            "document": metadata["document"],

            "distance": distance

        })

    return retrieved_chunks


# -------------------------
# Build Context
# -------------------------

def build_context(retrieved_chunks):
    """
    Merge retrieved chunks into a single context.
    """

    return "\n\n".join(
        chunk["text"] for chunk in retrieved_chunks
    )


# -------------------------
# Answer Question
# -------------------------

def answer_question(question):

    retrieved_chunks = retrieve_relevant_chunks(question)

    context = build_context(retrieved_chunks)

    prompt = f"""
You are SmartStudy AI.

You are an AI tutor helping students learn from uploaded study material.

Rules:

1. Answer ONLY from the supplied context.

2. Never hallucinate.

3. If the answer cannot be found in the context, reply:

"I couldn't find this in the uploaded study material."

4. Explain in simple language.

5. Give examples whenever appropriate.

6. Structure long answers using bullet points.

Context:

{context}

Question:

{question}
"""

    response = client.models.generate_content(

        model="gemini-2.5-flash-lite",

        contents=prompt
    )

    sources = []

    for chunk in retrieved_chunks:

        sources.append(
            f'{chunk["document"]} (Page {chunk["page"]})'
        )

    return {

        "answer": response.text,

        "sources": sorted(list(set(sources)))
    }


# -------------------------
# Testing
# -------------------------

if __name__ == "__main__":

    from ingestion.pdf_loader import load_pdf
    from ingestion.text_splitter import split_documents

    pages = load_pdf("../test.pdf")

    chunks = split_documents(pages)

    store_chunks(chunks)

    result = answer_question(
        "What is Balance of Payment?"
    )

    print("\nAnswer\n")
    print(result["answer"])

    print("\nSources\n")

    for source in result["sources"]:
        print(source)