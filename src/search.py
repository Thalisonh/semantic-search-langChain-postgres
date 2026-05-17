import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from langchain_postgres import PGVector
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

for k in ("PDF_PATH", "GEMINI_API_KEY", "DATABASE_URL"):
    if not os.getenv(k):
        raise ValueError(f"Missing environment variable: {k}")

PROMPT_TEMPLATE = """
CONTEXTO:
{contexto}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{pergunta}

RESPONDA A "PERGUNTA DO USUÁRIO"
"""

def search_prompt(question=None):
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

    docs_and_scores = store.similarity_search_with_score(question, k=10)

    contexto_str = "\n\n".join([doc.page_content for doc, score in docs_and_scores])

    prompt_preenchido = PROMPT_TEMPLATE.format(contexto=contexto_str, pergunta=question)

    llm = ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite",
        google_api_key=os.getenv("GEMINI_API_KEY")
    )

    resposta_llm = llm.invoke(prompt_preenchido)
    
    return resposta_llm.content