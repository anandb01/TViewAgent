from dotenv import load_dotenv
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_qdrant import QdrantVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

pdf_path = Path(__file__).parent / "data" / "sample.pdf"

# load the file

loader = PyPDFLoader(file_path=pdf_path)
docs = loader.load()

#split doc in chunks

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=4000,
    chunk_overlap=400
)

chunks = text_splitter.split_documents(documents=docs)

# create vector embeddings

embedding_model = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)

vector_store = QdrantVectorStore.from_documents(
    documents=chunks,
    embedding=embedding_model,
    url="http://localhost:6333",
    collection_name = "pdf_rag"
)

print("indexing of docs done.")
