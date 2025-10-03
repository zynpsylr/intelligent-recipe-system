import os
from typing import List
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document

# .env değişkenlerini yükle
load_dotenv()

# Pinecone bağlantısı
pinecone_api_key = os.getenv("PINECONE_API_KEY")
index_name = os.getenv("PINECONE_INDEX_NAME")

pc = Pinecone(api_key=pinecone_api_key)
index = pc.Index(host="https://meal-data-2-ac7k9cs.svc.aped-4627-b74a.pinecone.io")

# Embeddings
embeddings_model = OpenAIEmbeddings(
    model="text-embedding-3-small",
    api_key=os.getenv("OPENAI_API_KEY")
)

def upload_documents_to_pinecone(documents: List[Document], batch_size: int = 100):

    #  oluşan chunkların her birinin page_content ini alıp embed ediyor
    vectors = embeddings_model.embed_documents([doc.page_content for doc in documents])
    
    # 2. pinecon formatına dönüştürüyoruz
    items = [
        (str(doc.metadata["meal_id"]), vector, doc.metadata)
        for doc, vector in zip(documents, vectors)
        
    ]
    
    # İtems listesini batch'ler halinde  pinecone a yükle
    for i in range(0, len(items), batch_size):
        batch = items[i:i+batch_size]
        index.upsert(vectors=batch)
        print(f"✅ {len(batch)} döküman batch olarak yüklendi (Batch {i//batch_size + 1})")
    
    print(f"🎉 Toplam {len(items)} döküman Pinecone'a yüklendi.")

def load_existing_vector_store() -> bool:
    try:
        stats = index.describe_index_stats()
        vector_count = stats.get("total_vector_count", 0)
        
        if vector_count > 0:
            print(f"📊 Veritabanında {vector_count} adet tarif zaten mevcut. Veri çekme işlemi atlanıyor.")
            return True
        else:
            print("⏳ Veritabanı boş. Veri çekme ve yükleme işlemi başlatılıyor...")
            return False

    except Exception as e:
        print(f"❌ Pinecone ile iletişimde bir hata oluştu: {e}")
        return False
