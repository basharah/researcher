"""
Service Client - Proxy to microservices
"""
import httpx  # type: ignore
import logging
from typing import Optional, Dict, Any, BinaryIO
from config import settings

logger = logging.getLogger(__name__)


class ServiceClient:
    """Client for communicating with microservices"""
    
    def __init__(self):
        self.document_url = settings.document_service_url
        self.vector_url = settings.vector_service_url
        self.llm_url = settings.llm_service_url
        self.default_timeout = settings.request_timeout
    
    # ===== Document Processing Service =====
    
    async def upload_document(self, file_content: bytes, filename: str) -> Optional[Dict[str, Any]]:
        """Upload document to Document Processing Service"""
        try:
            async with httpx.AsyncClient(timeout=settings.upload_timeout) as client:
                files = {"file": (filename, file_content, "application/pdf")}
                response = await client.post(
                    f"{self.document_url}/api/v1/upload",
                    files=files
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error uploading document: {e}")
            raise
    
    async def get_document(self, document_id: int) -> Optional[Dict[str, Any]]:
        """Get document details"""
        try:
            async with httpx.AsyncClient(timeout=self.default_timeout) as client:
                response = await client.get(
                    f"{self.document_url}/api/v1/documents/{document_id}"
                )
                if response.status_code == 200:
                    return response.json()
                return None
        except Exception as e:
            logger.error(f"Error getting document {document_id}: {e}")
            return None
    
    async def list_documents(self, skip: int = 0, limit: int = 10) -> Optional[Dict[str, Any]]:
        """List all documents"""
        try:
            async with httpx.AsyncClient(timeout=self.default_timeout) as client:
                response = await client.get(
                    f"{self.document_url}/api/v1/documents",
                    params={"skip": skip, "limit": limit}
                )
                response.raise_for_status()
                docs = response.json()
                return {
                    "documents": docs,
                    "total": len(docs),
                    "skip": skip,
                    "limit": limit
                }
        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            raise
    
    async def delete_document(self, document_id: int) -> bool:
        """Delete document"""
        try:
            async with httpx.AsyncClient(timeout=self.default_timeout) as client:
                response = await client.delete(
                    f"{self.document_url}/api/v1/documents/{document_id}"
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            return False
    
    async def search_documents(self, search_request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Search documents using Vector DB"""
        try:
            async with httpx.AsyncClient(timeout=self.default_timeout) as client:
                response = await client.post(
                    f"{self.document_url}/api/v1/search",
                    json=search_request
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            raise
    
    async def get_document_sections(self, document_id: int) -> Optional[Dict[str, Any]]:
        """Get document sections"""
        try:
            async with httpx.AsyncClient(timeout=self.default_timeout) as client:
                response = await client.get(
                    f"{self.document_url}/api/v1/documents/{document_id}/sections"
                )
                if response.status_code == 200:
                    return response.json()
                return None
        except Exception as e:
            logger.error(f"Error getting sections for document {document_id}: {e}")
            return None
    
    async def get_document_tables(self, document_id: int) -> Optional[Dict[str, Any]]:
        """Get document tables"""
        try:
            async with httpx.AsyncClient(timeout=self.default_timeout) as client:
                response = await client.get(
                    f"{self.document_url}/api/v1/documents/{document_id}/tables"
                )
                if response.status_code == 200:
                    return response.json()
                return None
        except Exception as e:
            logger.error(f"Error getting tables for document {document_id}: {e}")
            return None
    
    # ===== Vector DB Service =====
    
    async def get_document_chunks(self, document_id: int) -> Optional[Dict[str, Any]]:
        """Get chunks for a document"""
        try:
            async with httpx.AsyncClient(timeout=self.default_timeout) as client:
                response = await client.get(
                    f"{self.vector_url}/documents/{document_id}/chunks"
                )
                if response.status_code == 200:
                    return response.json()
                return None
        except Exception as e:
            logger.error(f"Error getting chunks for document {document_id}: {e}")
            return None
    
    # ===== LLM Service =====
    
    async def analyze_document(self, analysis_request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze document using LLM"""
        try:
            async with httpx.AsyncClient(timeout=settings.analysis_timeout) as client:
                response = await client.post(
                    f"{self.llm_url}/api/v1/analyze",
                    json=analysis_request
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error analyzing document: {e}")
            raise
    
    async def answer_question(self, question_request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Answer question using LLM"""
        try:
            async with httpx.AsyncClient(timeout=settings.analysis_timeout) as client:
                response = await client.post(
                    f"{self.llm_url}/api/v1/question",
                    json=question_request
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            raise
    
    async def compare_documents(self, compare_request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Compare documents using LLM"""
        try:
            async with httpx.AsyncClient(timeout=settings.analysis_timeout) as client:
                response = await client.post(
                    f"{self.llm_url}/api/v1/compare",
                    json=compare_request
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error comparing documents: {e}")
            raise
    
    async def chat(self, chat_request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Chat with LLM"""
        try:
            async with httpx.AsyncClient(timeout=settings.analysis_timeout) as client:
                response = await client.post(
                    f"{self.llm_url}/api/v1/chat",
                    json=chat_request
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            raise
    
    # ===== Health Checks =====
    
    async def check_document_service(self) -> Dict[str, Any]:
        """Check Document Processing Service health"""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.document_url}/health")
                if response.status_code == 200:
                    return {"status": "healthy", "details": response.json()}
                return {"status": "unhealthy", "error": f"Status {response.status_code}"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def check_vector_service(self) -> Dict[str, Any]:
        """Check Vector DB Service health"""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.vector_url}/health")
                if response.status_code == 200:
                    return {"status": "healthy", "details": response.json()}
                return {"status": "unhealthy", "error": f"Status {response.status_code}"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def check_llm_service(self) -> Dict[str, Any]:
        """Check LLM Service health"""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.llm_url}/api/v1/health")
                if response.status_code == 200:
                    return {"status": "healthy", "details": response.json()}
                return {"status": "unhealthy", "error": f"Status {response.status_code}"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


# Singleton instance
_service_client: Optional[ServiceClient] = None


def get_service_client() -> ServiceClient:
    """Get or create service client singleton"""
    global _service_client
    if _service_client is None:
        _service_client = ServiceClient()
    return _service_client
