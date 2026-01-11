import os
from dotenv import load_dotenv
from fastapi import Query
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from openai import OpenAI
from langchain_community.vectorstores import FAISS

load_dotenv()


QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")

client = OpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

embedding_model = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)

# vector_db = QdrantVectorStore.from_existing_collection(
#     embedding=embedding_model,
#     url=QDRANT_URL,
#     collection_name="confluence_rag"
# )

vector_db = FAISS.load_local("faiss_index", embedding_model, allow_dangerous_deserialization=True)

def process_query(qry: str):
    print(f"💬: {qry}")
    search_results = vector_db.similarity_search(query=qry)

    # context = "\n\n\n".join([f"Page Content: {result.page_content}\nPage Number: {result.metadata['page_label']}\nFile Location: {result.metadata['source']}" for result in search_results])
    context = "\n\n\n".join([f"Page Content: {result.page_content}\nFile Location: {result.metadata['source']}" for result in search_results])

    SYSTEM_PROMPT = f"""
        You are a helpful AI assistant who answers user query based on the available context retreived from a PDF file along with page_contents and page number.

        You should strictly answer the user based on the following context and navigate the user to open the right page number to know more.

        context: {context}
    """

    response = client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": qry}
        ]
    )
    print(f"🤖: {response.choices[0].message.content}")
    return response.choices[0].message.content