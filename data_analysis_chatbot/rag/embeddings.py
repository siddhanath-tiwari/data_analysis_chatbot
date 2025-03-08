"""
Embedding models for RAG.
"""
from typing import Dict, Any, List
from loguru import logger
from langchain.embeddings import HuggingFaceEmbeddings, OpenAIEmbeddings


class EmbeddingManager:
    """
    Manager for embedding models.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the embedding manager.
        
        Args:
            config: Embedding configuration
        """
        self.config = config
        self.embedding_type = config.get("type", "huggingface").lower()
        self.model_name = config.get("model_name", "sentence-transformers/all-MiniLM-L6-v2")
        
        self.embeddings = self._init_embeddings()
        logger.info(f"Embedding model initialized: {self.embedding_type}")
    
    def _init_embeddings(self):
        """
        Initialize the embedding model based on the configuration.
        
        Returns:
            Embedding model instance
        """
        if self.embedding_type == "huggingface":
            return HuggingFaceEmbeddings(model_name=self.model_name)
        elif self.embedding_type == "openai":
            api_key = self.config.get("api_key") or os.environ.get("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API key not provided")
            
            return OpenAIEmbeddings(
                openai_api_key=api_key,
                model=self.config.get("model_name", "text-embedding-ada-002")
            )
        else:
            raise ValueError(f"Unsupported embedding type: {self.embedding_type}")
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Get embeddings for a list of texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embeddings
        """
        return self.embeddings.embed_documents(texts)
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Get embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        return self.embeddings.embed_query(text)