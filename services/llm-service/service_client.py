"""
Service Client - Communicates with other microservices
"""
import httpx  # type: ignore
import logging
from typing import Optional, List, Dict, Any
from config import settings

logger = logging.getLogger(__name__)


class ServiceClient:
    """Client for communicating with other microservices"""
    
    def __init__(self):
        self.vector_url = settings.vector_service_url
        self.document_url = settings.document_service_url
        self.timeout = 30
    
    async def get_document(self, document_id: int) -> Optional[Dict[str, Any]]:
        """
        Get document details from Document Processing Service
        
        Args:
            document_id: ID of the document
            
        Returns:
            Document details or None if not found
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.document_url}/api/v1/documents/{document_id}"
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"Document {document_id} not found: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching document {document_id}: {e}")
            return None
    
    async def semantic_search(
        self,
        query: str,
        max_results: int = 5,
        document_id: Optional[int] = None,
        section: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Perform semantic search using Vector DB Service
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            document_id: Optional filter by document ID
            section: Optional filter by section
            
        Returns:
            Search results or None if failed
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "query": query,
                    "max_results": max_results
                }
                
                if document_id:
                    payload["document_id"] = document_id
                if section:
                    payload["section"] = section
                
                response = await client.post(
                    f"{self.vector_url}/search",
                    json=payload
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"Semantic search failed: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error performing semantic search: {e}")
            return None
    
    async def health_check_vector_db(self) -> bool:
        """Check if Vector DB service is available"""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.vector_url}/health")
                return response.status_code == 200
        except Exception:
            return False
    
    async def health_check_document_service(self) -> bool:
        """Check if Document Processing service is available"""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.document_url}/health")
                return response.status_code == 200
        except Exception:
            return False


# Singleton instance
_service_client: Optional[ServiceClient] = None


def get_service_client() -> ServiceClient:
    """Get or create service client singleton"""
    global _service_client
    if _service_client is None:
        _service_client = ServiceClient()
    return _service_client
