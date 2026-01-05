from dotenv import load_dotenv
import os
from langchain_community.document_loaders import ConfluenceLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_qdrant import QdrantVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

# ==================== Configuration ====================

# Confluence credentials
CONFLUENCE_URL = os.getenv("CONFLUENCE_URL", "https://your-domain.atlassian.net/wiki")
CONFLUENCE_USERNAME = os.getenv("CONFLUENCE_USERNAME")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")

# Confluence space key (e.g., "TVA" for TellerView Application)
SPACE_KEY = os.getenv("CONFLUENCE_SPACE_KEY", "TVA")

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
        space_key=SPACE_KEY,
        include_children=True,  # ✅ Include child pages
        limit=50,  # Max pages per request (Confluence API limit)
    )
    
    docs = loader.load()
    print(f"✅ Loaded {len(docs)} pages from Confluence")
    
    if not docs:
        print("⚠️ Warning: No pages found. Check credentials and space key.")
        exit(1)
    
except Exception as e:
    print(f"❌ Error loading from Confluence: {e}")
    print("\nMake sure you have:")
    print("  1. Set CONFLUENCE_URL in .env")
    print("  2. Set CONFLUENCE_USERNAME in .env")
    print("  3. Set CONFLUENCE_API_TOKEN in .env")
    print("  4. Set CONFLUENCE_SPACE_KEY in .env")
    print("\nTo generate API token: https://id.atlassian.com/manage/api-tokens")
    exit(1)

# ==================== Split Documents into Chunks ====================

print("\n✂️ Splitting documents into chunks...")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=4000,
    chunk_overlap=400
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
    vector_store = QdrantVectorStore.from_documents(
        documents=chunks,
        embedding=embedding_model,
        url=QDRANT_URL,
        collection_name=COLLECTION_NAME,
        prefer_grpc=False,  # Use HTTP instead of gRPC (more compatible)
    )
    
    print(f"✅ Successfully indexed {len(chunks)} chunks into Qdrant!")
    print(f"✅ Collection: {COLLECTION_NAME}")
    print(f"✅ Qdrant URL: {QDRANT_URL}")
    
except Exception as e:
    print(f"❌ Error storing in Qdrant: {e}")
    print(f"\nMake sure Qdrant is running on {QDRANT_URL}")
    exit(1)

print("\n🎉 Indexing of Confluence documentation done!")
print(f"\n📊 Summary:")
print(f"   - Pages indexed: {len(docs)}")
print(f"   - Chunks created: {len(chunks)}")
print(f"   - Collection name: {COLLECTION_NAME}")
print(f"   - Ready for RAG queries!")
