"""
Embedding generation utilities
"""
from sentence_transformers import SentenceTransformer  # type: ignore
from typing import List, Union, Optional
import numpy as np  # type: ignore
from config import settings


class EmbeddingService:
    """Service for generating embeddings using sentence-transformers"""
    
    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize the embedding model
        
        Args:
            model_name: Name of the sentence-transformers model to use
        """
        self.model_name = model_name or settings.embedding_model
        print(f"Loading embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        print(f"Model loaded. Embedding dimension: {self.dimension}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        if not text or not text.strip():
            # Return zero vector for empty text
            return [0.0] * self.dimension
        
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (batch processing)
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        # Filter out empty texts but keep track of indices
        valid_texts = [(i, text) for i, text in enumerate(texts) if text and text.strip()]
        
        if not valid_texts:
            return [[0.0] * self.dimension] * len(texts)
        
        # Extract valid texts
        indices, valid_text_list = zip(*valid_texts)
        
        # Generate embeddings for valid texts
        embeddings = self.model.encode(list(valid_text_list), convert_to_numpy=True, show_progress_bar=True)
        
        # Create result list with zero vectors for empty texts
        result = [[0.0] * self.dimension] * len(texts)
        result = [list(vec) for vec in result]
        
        # Fill in valid embeddings
        for idx, embedding in zip(indices, embeddings):
            result[idx] = embedding.tolist()
        
        return result
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Similarity score between -1 and 1
        """
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        
        dot_product = np.dot(v1, v2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))


# Global instance - loaded once when the service starts
_embedding_service: Union[EmbeddingService, None] = None


def get_embedding_service() -> EmbeddingService:
    """Get or create the global embedding service instance"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
