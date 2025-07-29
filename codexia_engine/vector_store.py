# codexia_engine/vector_store.py

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from typing import List
from langchain.docstore.document import Document

def create_vector_store(chunks: List[Document]):
    """
    Creates a FAISS vector store from a list of document chunks.

    Args:
        chunks (list): A list of document chunks from the loader.

    Returns:
        FAISS: The searchable vector store object.
    """
    if not chunks:
        print("No chunks provided to create the vector store.")
        return None

    # Use a pre-trained model from Hugging Face to create embeddings
    # This model is great for code and text, and runs locally.
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    embeddings = HuggingFaceEmbeddings(model_name=model_name)

    print("Creating vector store from chunks...")
    # Create the FAISS vector store from the document chunks and embeddings
    vector_store = FAISS.from_documents(chunks, embeddings)
    print("Vector store created successfully.")

    return vector_store