"""
Document retriever for RAG.
"""
from typing import Dict, Any, List, Optional
from loguru import logger

from data_analysis_chatbot.rag.document_store import DocumentStore


class DocumentRetriever:
    """
    Document retriever for RAG.
    """
    
    def __init__(self, document_store: DocumentStore, config: Dict[str, Any]):
        """
        Initialize the document retriever.
        
        Args:
            document_store: Document store
            config: Retriever configuration
        """
        self.document_store = document_store
        self.config = config
        self.top_k = config.get("top_k", 5)
        
        logger.info("Document retriever initialized")
    
    def retrieve(self, query: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retrieve documents relevant to the query.
        
        Args:
            query: Query string
            top_k: Number of results to return (overrides config)
            
        Returns:
            List of document chunks with similarity scores
        """
        if top_k is None:
            top_k = self.top_k
        
        results = self.document_store.search(query, top_k=top_k)
        
        logger.debug(f"Retrieved {len(results)} documents for query: {query}")
        return results
    
    def retrieve_and_format(self, query: str, top_k: Optional[int] = None) -> str:
        """
        Retrieve documents and format them for inclusion in a prompt.
        
        Args:
            query: Query string
            top_k: Number of results to return (overrides config)
            
        Returns:
            Formatted string of retrieved documents
        """
        results = self.retrieve(query, top_k=top_k)
        
        if not results:
            return "No relevant information found."
        
        formatted_results = []
        for i, result in enumerate(results):
            content = result["content"]
            source = result["metadata"].get("source", "Unknown")
            score = result["score"]
            
            formatted_result = f"Document {i+1} (Source: {source}, Relevance: {score:.2f}):\n{content}\n"
            formatted_results.append(formatted_result)
        
        return "\n".join(formatted_results)