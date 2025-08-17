import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma

PDF_PATH = "src/linear_algebra/advanced_linear_algebra.pdf"
CHROMA_DB_PATH = "chroma_db"

def ingest_documents():

    print("Loading document...")
    loader = PyPDFLoader(PDF_PATH)
    documents = loader.load()

    print(f"Loaded {len(documents)} pages.")
    print("Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )
    docs = text_splitter.split_documents(documents)
    print(f"Split into {len(docs)} chunks.")

    print("Creating embeddings and storing in ChromaDB...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    db = Chroma.from_documents(docs, embeddings, persist_directory=CHROMA_DB_PATH)
    print("Ingestion complete. Vector store created.")
    return db

if __name__ == "__main__":
    ingest_documents()

