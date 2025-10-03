from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from typing import List

splitter = RecursiveCharacterTextSplitter(
      chunk_size=1000,
      chunk_overlap=200, 
      length_function=len
    )

def split_documents(documents: List[Document]) -> List[Document]:
    chunks = splitter.split_documents(documents)
    print(f"📊 Toplam {len(chunks)} chunk oluşturuldu")
    return chunks
