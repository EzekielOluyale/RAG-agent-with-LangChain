import os

from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_google_genai import GoogleGenerativeAIEmbeddings

from langchain_pinecone import PineconeVectorStore

from pinecone import Pinecone

from langgraph.checkpoint.postgres import PostgresSaver

def get_embeddings():
    return GoogleGenerativeAIEmbeddings(
        model="text-embedding-004",
        vertexai=True
    )

def get_vector_store():
    embeddings = get_embeddings()

    pc = Pinecone()

    index = pc.Index("rag")

    return PineconeVectorStore(
        embedding=embeddings,
        index=index
    )

def get_checkpointer():
    DB_URI = os.getenv("DATABASE_URL")

    if not DB_URI:
        raise ValueError("DATABASE_URL environment variable is missing!")
    
    checkpointer = PostgresSaver.from_conn_string(DB_URI)
    checkpointer.setup() 
    return checkpointer