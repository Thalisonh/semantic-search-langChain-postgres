import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from langchain_postgres import PGVector

load_dotenv()

for k in ("PDF_PATH", "GEMINI_API_KEY", "DATABASE_URL"):
    if not os.getenv(k):
        raise ValueError(f"Missing environment variable: {k}")

PDF_PATH = os.getenv("PDF_PATH")

def ingest_pdf():
    loader = PyPDFLoader(PDF_PATH)
    docs = loader.load()
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
    )
    
    docs_split = splitter.split_documents(docs)

    enriched = [
        Document(
            page_content=d.page_content,
            metadata={k: v for k,v in d.metadata.items() if v not in ("", None)}
        ) 
        for d in docs_split
    ]

    ids = [f"doc_{i}" for i in range(len(docs_split))]

    embeddings = GoogleGenerativeAIEmbeddings(
        model=os.getenv("GOOGLE_EMBEDDING_MODEL"),
        google_api_key=os.getenv("GEMINI_API_KEY")
    )
    
    store = PGVector(
        embeddings=embeddings,
        collection_name="documents",
        connection=os.getenv("DATABASE_URL"),
        use_jsonb=True,
    )

    store.add_documents(enriched, ids=ids)

if __name__ == "__main__":
    ingest_pdf()