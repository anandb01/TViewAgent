from dotenv import load_dotenv
import os
from langchain_community.document_loaders import ConfluenceLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_qdrant import QdrantVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS 

load_dotenv()

# ==================== Configuration ====================

# Confluence credentials
CONFLUENCE_URL = os.getenv("CONFLUENCE_URL")
CONFLUENCE_USERNAME = os.getenv("CONFLUENCE_USERNAME")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")

# Confluence space key (e.g., "TVA" for TellerView Application)
SPACE_KEY = os.getenv("CONFLUENCE_SPACE_KEY")

# Vector DB configuration
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = "confluence_rag"

# ==================== Load Confluence Pages ====================

print(f"📚 Loading Confluence pages from space: {SPACE_KEY}...")

try:
    loader = ConfluenceLoader(
        url=CONFLUENCE_URL,
        username=CONFLUENCE_USERNAME,
        api_key=CONFLUENCE_API_TOKEN,
        space_key=SPACE_KEY
    )
    
    docs = loader.load()
    print(f"✅ Loaded {len(docs)} pages from Confluence")
    
    if not docs:
        print("⚠️ Warning: No pages found. Check credentials and space key.")
        exit(1)
    
except Exception as e:
    print(f"❌ Error loading from Confluence: {e}")
    exit(1)

# ==================== Split Documents into Chunks ====================

print("\n✂️ Splitting documents into chunks...")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100
)

chunks = text_splitter.split_documents(documents=docs)
print(f"✅ Created {len(chunks)} chunks from {len(docs)} pages")

# Display sample chunk info
if chunks:
    print(f"\n📄 Sample chunk:")
    print(f"   Source: {chunks[0].metadata.get('source', 'N/A')}")
    print(f"   Title: {chunks[0].metadata.get('title', 'N/A')}")
    print(f"   Content preview: {chunks[0].page_content[:100]}...")

# ==================== Create Vector Embeddings ====================

print("\n🔗 Generating vector embeddings...")

embedding_model = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)

# ==================== Store in Qdrant ====================

print(f"\n💾 Storing vectors in Qdrant (collection: {COLLECTION_NAME})...")

try:
    # vector_store = QdrantVectorStore.from_documents(
    #     documents=chunks,
    #     embedding=embedding_model,
    #     url=QDRANT_URL,
    #     collection_name=COLLECTION_NAME,
    #     prefer_grpc=False,  # Use HTTP instead of gRPC (more compatible)
    # )
    
    # print(f"✅ Successfully indexed {len(chunks)} chunks into Qdrant!")
    # print(f"✅ Collection: {COLLECTION_NAME}")
    # print(f"✅ Qdrant URL: {QDRANT_URL}")

    vector_store = FAISS.from_documents(chunks, embedding_model)
    vector_store.save_local("faiss_index")
    
except Exception as e:
    print(f"❌ Error storing in FAISS: {e}")
    exit(1)

print("\n🎉 Indexing of Confluence documentation done!")
print(f"\n📊 Summary:")
print(f"   - Pages indexed: {len(docs)}")
print(f"   - Chunks created: {len(chunks)}")
print(f"   - Collection name: {COLLECTION_NAME}")
print(f"   - Ready for RAG queries!")
