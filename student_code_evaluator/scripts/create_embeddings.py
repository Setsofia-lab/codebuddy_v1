import os
import chromadb
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ensure the GOOGLE_API_KEY is set
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables.")

def create_embeddings_and_store(documents, db_path="./chroma_db"):
    """
    Creates embeddings for document chunks and stores them in ChromaDB.

    Args:
        documents (list): A list of dictionaries, each with 'filename' and 'content'.
        db_path (str): The path to store the ChromaDB database.
    """
    # Initialize ChromaDB client
    client = chromadb.PersistentClient(path=db_path)

    # Get or create a collection
    collection_name = "student_code_collection"
    try:
        collection = client.create_collection(name=collection_name)
        print(f"Collection '{collection_name}' created.")
    except:
        collection = client.get_collection(name=collection_name)
        print(f"Collection '{collection_name}' already exists. Using existing collection.")


    # Initialize text splitter
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    # Initialize Google Generative AI Embeddings
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    for doc in documents:
        filename = doc['filename']
        content = doc['content']

        # Split document into chunks
        chunks = text_splitter.split_text(content)

        # Create embeddings and add to ChromaDB
        for i, chunk in enumerate(chunks):
            # Generate a unique ID for each chunk
            chunk_id = f"{filename}_{i}"
            try:
                collection.add(
                    embeddings=[embeddings.embed_query(chunk)],
                    documents=[chunk],
                    metadatas=[{"filename": filename, "chunk_index": i}],
                    ids=[chunk_id]
                )
                print(f"Added chunk {i} from {filename} to ChromaDB.")
            except Exception as e:
                print(f"Error adding chunk {i} from {filename} to ChromaDB: {e}")

if __name__ == '__main__':
    # Example usage (requires process_documents.py and a 'data' directory with files)
    from process_documents import process_documents_in_directory

    # Assuming you have a 'data' directory in the parent folder of 'scripts'
    data_directory = "/Users/samuelsetsofia/dev/codebuddy_v1/student_code_evaluator/data"
    if not os.path.exists(data_directory):
        print(f"Error: Data directory '{data_directory}' not found. Please create it and add your documents.")
    else:
        print(f"Processing documents in '{data_directory}'...")
        documents = process_documents_in_directory(data_directory)
        if documents:
            print(f"Found {len(documents)} documents. Creating embeddings and storing in ChromaDB...")
            create_embeddings_and_store(documents)
            print("Embedding and storing complete.")
        else:
            print("No supported documents found in the data directory.")
