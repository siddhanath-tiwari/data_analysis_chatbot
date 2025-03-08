"""
Document store for managing documents for RAG.
"""
import os
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import json
import uuid
from loguru import logger

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document as LangchainDocument
from langchain.document_loaders import (
    TextLoader,
    PyPDFLoader,
    CSVLoader,
    UnstructuredExcelLoader,
    UnstructuredMarkdownLoader,
    UnstructuredHTMLLoader,
)

from data_analysis_chatbot.rag.vectordb import VectorDBManager


class DocumentStore:
    """
    Document store for managing documents for RAG.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the document store.
        
        Args:
            config: Configuration for the document store
        """
        self.config = config
        self.chunk_size = config.get("chunk_size", 1000)
        self.chunk_overlap = config.get("chunk_overlap", 200)
        
        # Initialize vector database
        self.vector_db_manager = VectorDBManager(config.get("vector_db", {}))
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )
        
        # Supported file types and their loaders
        self.file_loaders = {
            ".txt": TextLoader,
            ".pdf": PyPDFLoader,
            ".csv": CSVLoader,
            ".xlsx": UnstructuredExcelLoader,
            ".xls": UnstructuredExcelLoader,
            ".md": UnstructuredMarkdownLoader,
            ".html": UnstructuredHTMLLoader,
            ".htm": UnstructuredHTMLLoader,
        }
        
        logger.info("Document store initialized")
    
    def add_document(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add a document to the store.
        
        Args:
            content: Document content
            metadata: Document metadata
            
        Returns:
            Document ID
        """
        metadata = metadata or {}
        doc_id = str(uuid.uuid4())
        metadata["doc_id"] = doc_id
        
        # Split the document into chunks
        texts = self.text_splitter.split_text(content)
        documents = [
            LangchainDocument(
                page_content=text,
                metadata={**metadata, "chunk_id": i}
            )
            for i, text in enumerate(texts)
        ]
        
        # Add documents to vector store
        self.vector_db_manager.add_documents(documents)
        
        logger.info(f"Added document with ID: {doc_id}, chunks: {len(documents)}")
        return doc_id
    
    def add_file(self, file_path: Union[str, Path], metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add a file to the document store.
        
        Args:
            file_path: Path to the file
            metadata: Document metadata
            
        Returns:
            Document ID
        """
        file_path = Path(file_path)
        metadata = metadata or {}
        
        # Get file extension
        file_ext = file_path.suffix.lower()
        if file_ext not in self.file_loaders:
            raise ValueError(f"Unsupported file type: {file_ext}")
        
        # Add file metadata
        metadata["source"] = str(file_path)
        metadata["filename"] = file_path.name
        doc_id = str(uuid.uuid4())
        metadata["doc_id"] = doc_id
        
        # Load and split the document
        loader_cls = self.file_loaders[file_ext]
        loader = loader_cls(str(file_path))
        documents = loader.load()
        
        # Split the documents
        split_documents = self.text_splitter.split_documents(documents)
        
        # Add chunk ID to metadata
        for i, doc in enumerate(split_documents):
            doc.metadata.update({"chunk_id": i})
        
        # Add documents to vector store
        self.vector_db_manager.add_documents(split_documents)
        
        logger.info(f"Added file {file_path.name} with ID: {doc_id}, chunks: {len(split_documents)}")
        return doc_id
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for documents similar to the query.
        
        Args:
            query: Query string
            top_k: Number of results to return
            
        Returns:
            List of document chunks with similarity scores
        """
        results = self.vector_db_manager.search(query, top_k=top_k)
        
        return results
    
    def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document from the store.
        
        Args:
            doc_id: Document ID
            
        Returns:
            True if successful
        """
        result = self.vector_db_manager.delete_documents({"doc_id": doc_id})
        
        logger.info(f"Deleted document with ID: {doc_id}")
        return result
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """
        Get all documents from the store.
        
        Returns:
            List of document metadata
        """
        return self.vector_db_manager.get_all_documents()