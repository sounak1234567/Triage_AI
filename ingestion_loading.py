import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from fiass_store import create_local_db, load_local_db
from dotenv import load_dotenv

load_dotenv()

def cook_protocols():
    pass

def cook_knowledge_base():
    loader = DirectoryLoader("./protocol", glob="/*.pdf", loader_cls=PyPDFLoader) # type: ignore
    raw_documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap=100)
    documents = text_splitter.split_documents(raw_documents)
    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
    vec_db = create_local_db(documents, embeddings)

def get_protocol_context(query: str, top_k: int = 3):
    vec_db = load_local_db(GoogleGenerativeAIEmbeddings(model="gemini-embedding-001"))
    docs = vec_db.similarity_search(query, k = top_k)
    return "\n\n".join([doc.page_content for doc in docs])
