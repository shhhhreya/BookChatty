import os
import chromadb
import openai
from fastapi import FastAPI, File, UploadFile, Form
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Load API key
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize FastAPI
app = FastAPI()

# Load embedding model
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path="./db")  # Persistent storage
collection = chroma_client.get_or_create_collection(name="books")

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = PdfReader(pdf_file)
    text = " ".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
    return text

# Function to chunk text
def chunk_text(text, chunk_size=500):
    words = text.split()
    return [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

# Upload PDF endpoint
@app.post("/upload/")
async def upload_pdf(file: UploadFile = File(...), book_title: str = Form(...)):
    text = extract_text_from_pdf(file.file)
    chunks = chunk_text(text)

    # Convert chunks to embeddings and store in ChromaDB
    for i, chunk in enumerate(chunks):
        embedding = embedder.encode(chunk).tolist()
        collection.add(ids=[f"{book_title}_{i}"], embeddings=[embedding], metadatas=[{"text": chunk}])

    return {"message": f"Book '{book_title}' uploaded and stored successfully!"}

# Query endpoint
@app.get("/query/")
async def ask_question(query: str):
    query_embedding = embedder.encode(query).tolist()
    results = collection.query(query_embeddings=[query_embedding], n_results=3)  # Retrieve top 3 results

    context = " ".join([doc["text"] for doc in results["metadatas"][0]])  # Get retrieved text
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "Answer based on the book's content."},
                  {"role": "user", "content": f"Context: {context} \nQuestion: {query}"}],
        api_key=OPENAI_API_KEY
    )

    return {"answer": response["choices"][0]["message"]["content"]}
