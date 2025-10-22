"""
Retrieval-Augmented Generation for Cultural Knowledge
"""

import os
from typing import List, Dict
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from config.settings import settings

class CulturalRAG:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings()
        self.vector_store = None
        self._initialize_knowledge_base()
    
    def _initialize_knowledge_base(self):
        """Initialize the cultural knowledge vector database"""
        cultural_data = self._load_cultural_data()
        
        if cultural_data:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50
            )
            
            docs = []
            for item in cultural_data:
                doc = Document(
                    page_content=item["content"],
                    metadata={"culture": item["culture"], "category": item["category"]}
                )
                docs.append(doc)
            
            split_docs = text_splitter.split_documents(docs)
            
            self.vector_store = Chroma.from_documents(
                documents=split_docs,
                embedding=self.embeddings,
                persist_directory=os.path.join(settings.CULTURAL_DB_PATH, "chroma_db")
            )
    
    def _load_cultural_data(self) -> List[Dict]:
        """Load cultural etiquette data"""
        # Sample cultural data - in practice, load from files/database
        return [
            {
                "culture": "japanese",
                "category": "greetings",
                "content": "In Japanese culture, bowing is essential. Use 'arigatou gozaimasu' for formal thanks."
            },
            {
                "culture": "american",
                "category": "business",
                "content": "American business culture values directness and efficiency. Be clear and confident."
            },
            {
                "culture": "chinese",
                "category": "respect",
                "content": "Chinese culture emphasizes hierarchy and face-saving. Avoid direct criticism."
            }
        ]
    
    def retrieve_cultural_context(self, query: str, culture: str, k: int = 3) -> List[str]:
        """
        Retrieve relevant cultural context for a query
        
        Args:
            query: The text to find cultural context for
            culture: Target culture
            k: Number of relevant documents to retrieve
        
        Returns:
            List of relevant cultural guidance texts
        """
        if not self.vector_store:
            return []
        
        # Search for relevant cultural information
        docs = self.vector_store.similarity_search(
            query,
            k=k,
            filter={"culture": culture}
        )
        
        return [doc.page_content for doc in docs]
