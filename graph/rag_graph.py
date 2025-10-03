import os
from typing import Annotated, Dict
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langdetect import detect

from data.fetch_api import fetch_all_meals, process_meal_to_document
from data.splitter import split_documents
from data.pinecone_vector import upload_documents_to_pinecone, load_existing_vector_store
from data.retriever import get_retriever


# --- STATE ---
class State(TypedDict):
    query: str
    translated_query: str
    user_language: str
    retrieved_docs: list
    messages: Annotated[list, add_messages]
    context: str


# --- RAG GRAPH ---
class RAGGraph:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo-0125",
            temperature=0.4,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.retriever = None
        self.graph = None
    
    # --- VERİ KURULUMU ---
    def setup_data(self):
        if load_existing_vector_store():
            print("✅ Mevcut veri bulundu, yeni veri kurulumu atlanıyor.")
        else:
            print("🚀 İlk kurulum başlıyor...")
            meals = fetch_all_meals()
            documents = process_meal_to_document(meals)
            chunks = split_documents(documents)
            upload_documents_to_pinecone(chunks)
            print("✅ Kurulum tamamlandı!")
        
        self.retriever = get_retriever()

    # --- ÇEVİRİ ---
    def translate_to_english(self, text: str) -> str:
        if not text:
            return text
        prompt = f"Metni İngilizceye çevir:\n\n{text}"
        response = self.llm.invoke(prompt)
        return response.content.strip()
    
    def translate_query_node(self, state: State) -> Dict:
        query = state["query"]
        translated = self.translate_to_english(query)
        print(f"🇬🇧 Çevrilen Soru: '{translated}'")
        return {"translated_query": translated}

    # --- DİL TESPİT ---
    def detect_language_node(self, state: State) -> Dict:
        query = state["query"]
        try:
            lang = detect(query)  
        except:
            lang = "en"
        if lang not in ["tr", "en"]:
            lang = "en"
        print(f"🌐 Kullanıcı dili (local): {lang}")
        return {
            "user_language": lang,
            "query": query
        }

    # --- TRANSLATE GEREKLİ Mİ ---
    def should_translate(self, state: State) -> str:
        if state["user_language"] == "tr":
            return "translate_query"
        else:
            return "retrieve"

    # --- RETRIEVAL ---
    def retrieve_documents_node(self, state: State) -> Dict:
        query = state["translated_query"] if state["user_language"] == "tr" else state["query"]
        if self.retriever is None:
            raise ValueError("Vector store yok, önce setup_data() çalıştır!")
        retrieved_docs = self.retriever.get_relevant_documents(query)
        print(f"📋 {len(retrieved_docs)} döküman bulundu.")
        return {"retrieved_docs": retrieved_docs}

    # --- CONTEXT ---
    def prepare_context_node(self, state: State) -> Dict:
        print("📝 Context hazırlanıyor...")
        if not state["retrieved_docs"]:
            context = "İlgili tarif bulunamadı."
        else:
            context = "\n\n".join([doc.page_content for doc in state["retrieved_docs"]])
        return {"context": context}

    # --- CEVAP ÜRET ---
    def generate_answer_node(self, state: State) -> Dict:
        print("🤖 Cevap üretiliyor...")
        user_language = state["user_language"]

        if user_language == "tr":
            base_prompt = """
            Sen yemek tarifleri konusunda uzman bir Türk aşçısısın. 
            Aşağıdaki context bilgilerini kullanarak kullanıcının sorusunu cevapla.

            Context:
            {context}

            Kullanıcı Sorusu: {question}

            Cevabın detaylı, arkadaşça ve Türkçe olsun. 
            Tarif detayları, malzemeler ve yapım aşamalarını eklemeye çalış.
            Eğer context'te bilgi yoksa, genel mutfak bilgilerini kullan.
            """
        else:
            base_prompt = """
            You are an expert chef assistant. Use the context information below 
            to answer the user's question.

            Context:
            {context}

            User Question: {question}

            Provide a detailed answer in English, including recipe details, 
            ingredients, and cooking steps when applicable.
            If context is missing, use general cooking knowledge.
            """

        prompt = ChatPromptTemplate.from_template(base_prompt)
        formatted_prompt = prompt.format(context=state["context"], question=state["query"])
        response = self.llm.invoke(formatted_prompt)
        return {"messages": [response]}

    # --- GRAF OLUŞTUR ---
    def create_graph(self):
        if self.retriever is None:
            raise ValueError("setup_data() önce çalıştırılmalı!")
            
        graph_builder = StateGraph(State)
        graph_builder.add_node("detect_language", self.detect_language_node)
        graph_builder.add_node("translate_query", self.translate_query_node)
        graph_builder.add_node("retrieve", self.retrieve_documents_node)
        graph_builder.add_node("prepare_context", self.prepare_context_node)
        graph_builder.add_node("generate", self.generate_answer_node)

        graph_builder.add_edge(START, "detect_language")
        graph_builder.add_conditional_edges(
            "detect_language",
            self.should_translate,
            {
                "translate_query": "translate_query",
                "retrieve": "retrieve"
            }
        )
        graph_builder.add_edge("translate_query", "retrieve")
        graph_builder.add_edge("retrieve", "prepare_context")
        graph_builder.add_edge("prepare_context", "generate")
        graph_builder.add_edge("generate", END)

        self.graph = graph_builder.compile()
        print("🔗 Graf başarıyla oluşturuldu!")
        return self.graph

    # --- SORU SOR ---
    def ask(self, query: str) -> str:
        if self.graph is None:
            raise ValueError("Graph henüz oluşturulmamış! create_graph() çalıştır")
        
        print(f"\n💬 Soru alındı: {query}")
        result = self.graph.invoke({
            "query": query,
            "translated_query": "",
            "user_language": "",
            "retrieved_docs": [],
            "messages": [],
            "context": "",
        })
        
        if result.get("messages") and len(result["messages"]) > 0:
            return result["messages"][-1].content
        else:
            return "Cevap üretilemedi."
