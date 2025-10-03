import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore

# .env dosyasındaki değişkenleri yükle
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def get_retriever():
    print("🔧 Retriever oluşturuluyor...")

    try:
        # 1. Pinecone bağlantısı
        pc = Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index(PINECONE_INDEX_NAME)

        # 2. Embedding Modeli
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=OPENAI_API_KEY
        )

        # 3. Vector Store ve Retriever
        vector_store = PineconeVectorStore(
            index=index,
            embedding=embeddings,
        
        )
        retriever = vector_store.as_retriever()

        print("✅ Retriever başarıyla oluşturuldu.")
        return retriever

    except Exception as e:
        print(f"❌ Retriever oluşturulurken hata: {e}")
        raise
