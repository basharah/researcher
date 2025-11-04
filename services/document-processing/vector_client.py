"""
Vector DB Service Client
Handles communication with the Vector DB service
"""
import httpx  # type: ignore
import logging
from typing import Optional, Dict, Any
from config import settings

logger = logging.getLogger(__name__)


class VectorDBClient:
    """Client for interacting with the Vector DB service"""
    
    def __init__(self, base_url: Optional[str] = None, timeout: Optional[int] = None):
        """
        Initialize the Vector DB client
        
        Args:
            base_url: Base URL of the Vector DB service
            timeout: Request timeout in seconds
        """
        self.base_url = base_url or settings.vector_service_url
        self.timeout = timeout or settings.vector_db_timeout
        self.enabled = settings.enable_vector_db
    
    async def process_document(
        self,
        document_id: int,
        full_text: str,
        sections: Optional[Dict[str, str]] = None,
        tables: Optional[list] = None,
        references: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Send document to Vector DB for chunking and embedding generation
        
        Args:
            document_id: ID of the document
            full_text: Complete document text
            sections: Dictionary of section names to text
            tables: List of extracted tables
            references: References text
            
        Returns:
            Response from Vector DB or None if disabled/failed
        """
        if not self.enabled:
            logger.info("Vector DB integration is disabled")
            return None
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "document_id": document_id,
                    "full_text": full_text,
                    "sections": sections,
                    "tables": tables,
                    "references": references
                }
                
                logger.info(f"Sending document {document_id} to Vector DB for processing")
                response = await client.post(
                    f"{self.base_url}/process-document",
                    json=payload
                )
                
                response.raise_for_status()
                result = response.json()
                logger.info(
                    f"Vector DB processed document {document_id}: "
                    f"{result.get('chunks_created', 0)} chunks created"
                )
                return result
                
        except httpx.TimeoutException:
            logger.error(
                f"Timeout while processing document {document_id} in Vector DB "
                f"(timeout: {self.timeout}s)"
            )
            return None
        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error from Vector DB for document {document_id}: "
                f"{e.response.status_code} - {e.response.text}"
            )
            return None
        except Exception as e:
            logger.error(
                f"Unexpected error while processing document {document_id} in Vector DB: {e}"
            )
            return None
    
    async def search(
        self,
        query: str,
        max_results: int = 10,
        document_id: Optional[int] = None,
        section: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Perform semantic search across document chunks
        
        Args:
            query: Search query
            max_results: Maximum number of results
            document_id: Filter by specific document
            section: Filter by section
            
        Returns:
            Search results or None if failed
        """
        if not self.enabled:
            logger.info("Vector DB integration is disabled")
            return None
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                payload = {
                    "query": query,
                    "max_results": max_results,
                    "document_id": document_id,
                    "section": section
                }
                
                response = await client.post(
                    f"{self.base_url}/search",
                    json=payload
                )
                
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Error during Vector DB search: {e}")
            return None
    
    async def delete_document_chunks(self, document_id: int) -> bool:
        """
        Delete all chunks for a document
        
        Args:
            document_id: ID of the document
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return True  # Skip if disabled
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.delete(
                    f"{self.base_url}/documents/{document_id}/chunks"
                )
                
                response.raise_for_status()
                logger.info(f"Deleted chunks for document {document_id} from Vector DB")
                return True
                
        except Exception as e:
            logger.error(f"Error deleting chunks for document {document_id}: {e}")
            return False
    
    async def health_check(self) -> bool:
        """
        Check if Vector DB service is healthy
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/health")
                response.raise_for_status()
                return True
        except Exception:
            return False


# Global client instance
_vector_client: Optional[VectorDBClient] = None


def get_vector_client() -> VectorDBClient:
    """Get or create the global Vector DB client instance"""
    global _vector_client
    if _vector_client is None:
        _vector_client = VectorDBClient()
    return _vector_client
