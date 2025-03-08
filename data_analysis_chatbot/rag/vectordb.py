"""
Vector database manager for document embeddings.
"""
from typing import Dict, Any, List, Optional
import os
from pathlib import Path
from loguru import logger

from langchain.docstore.document import Document
from langchain.vectorstores import Chroma, FAISS
from langchain.embeddings import HuggingFaceEmbeddings


class VectorDBManager:
    """
    Vector database manager for document embeddings.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the vector database manager.
        
        Args:
            config: Vector database configuration
        """
        self.config = config
        self.db_type = config.get("type", "chroma").lower()
        self.persist_directory = config.get("persist_directory", "data/vectordb")
        
        # Ensure the persist directory exists
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # Initialize embedding model
        embedding_model_name = config.get("embedding_model", "sentence-transformers/all-MiniLM-L6-v2")
        self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name)
        
        # Initialize vector database
        self.vectordb = self._init_vectordb()
        
        logger.info(f"Vector database initialized: {self.db_type}")
    
    def _init_vectordb(self):
        """
        Initialize the vector database based on the configuration.
        
        Returns:
            Vector database instance
        """
        if self.db_type == "chroma":
            return Chroma(
                embedding_function=self.embeddings,
                persist_directory=self.persist_directory,
            )
        elif self.db_type == "faiss":
            # Check if index exists
            index_file = Path(self.persist_directory) / "index.faiss"
            if index_file.exists():
                return FAISS.load_local(
                    self.persist_directory,
                    self.embeddings,
                    "index"
                )
            return FAISS.from_documents(
                [],
                self.embeddings
            )
        else:
            raise ValueError(f"Unsupported vector database type: {self.db_type}")
    
    def add_documents(self, documents: List[Document]) -> None:
        """
        Add documents to the vector database.
        
        Args:
            documents: List of documents to add
        """
        if not documents:
            logger.warning("No documents to add")
            return
        
        if self.db_type == "chroma":
            self.vectordb.add_documents(documents)
        elif self.db_type == "faiss":
            if not self.vectordb._index:
                self.vectordb = FAISS.from_documents(
                    documents,
                    self.embeddings
                )
            else:
                self.vectordb.add_documents(documents)
            # Save the index
            self.vectordb.save_local(self.persist_directory, "index")
        
        logger.info(f"Added {len(documents)} documents to vector database")
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for documents similar to the query.
        
        Args:
            query: Query string
            top_k: Number of results to return
            
        Returns:
            List of document chunks with similarity scores
        """
        results = self.vectordb.similarity_search_with_score(query, k=top_k)
        
        # Format results
        formatted_results = []
        for doc, score in results:
            formatted_results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": float(score),
            })
        
        return formatted_results
    
    def delete_documents(self, filter: Dict[str, Any]) -> bool:
        """
        Delete documents from the vector database.
        
        Args:
            filter: Filter to select documents to delete
            
        Returns:
            True if successful
        """
        if self.db_type == "chroma":
            self.vectordb._collection.delete(where=filter)
            return True
        elif self.db_type == "faiss":
            logger.warning("Delete operation not fully supported in FAISS, recreating index")
            # For FAISS, we need to recreate the index without the deleted documents
            # This is a limitation of FAISS
            docs = self.get_all_documents()
            filtered_docs = [doc for doc in docs if not all(doc["metadata"].get(k) == v for k, v in filter.items())]
            
            # Convert to Document objects
            langchain_docs = [
                Document(
                    page_content=doc["content"],
                    metadata=doc["metadata"]
                )
                for doc in filtered_docs
            ]
            
            # Recreate the index
            self.vectordb = FAISS.from_documents(
                langchain_docs,
                self.embeddings
            )
            # Save the index
            self.vectordb.save_local(self.persist_directory, "index")
            return True
        
        return False
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """
        Get all documents from the vector database.
        
        Returns:
            List of document metadata
        """
        if self.db_type == "chroma":
            docs = self.vectordb._collection.get()
            return [
                {
                    "id": doc_id,
                    "content": doc,
                    "metadata": meta,
                }
                for doc_id, doc, meta in zip(docs["ids"], docs["documents"], docs["metadatas"])
            ]
        elif self.db_type == "faiss":
            if not self.vectordb._index:
                return []
            
            # For FAISS, we need a different approach
            # This is a simplified version - in a real app you might need
            # to store document data separately
            return [
                {
                    "id": i,
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                }
                for i, doc in enumerate(self.vectordb.docstore._dict.values())
            ]
        
        return []