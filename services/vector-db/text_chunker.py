"""
Text chunking utilities
"""
from typing import List, Dict, Optional, Any
from config import settings


class TextChunker:
    """Utility for splitting text into chunks for embedding"""
    
    def __init__(self, chunk_size: Optional[int] = None, chunk_overlap: Optional[int] = None):
        """
        Initialize the chunker
        
        Args:
            chunk_size: Maximum characters per chunk
            chunk_overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
    
    def chunk_text(self, text: str, section: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Text to chunk
            section: Section name (abstract, introduction, etc.)
            
        Returns:
            List of dictionaries with chunk data
        """
        if not text or not text.strip():
            return []
        
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(text):
            # Calculate end position
            end = start + self.chunk_size
            
            # If this is not the last chunk, try to break at a sentence or word boundary
            if end < len(text):
                # Look for sentence boundary (. ! ?)
                for delimiter in ['. ', '! ', '? ', '\n\n', '\n']:
                    last_delimiter = text.rfind(delimiter, start, end)
                    if last_delimiter != -1 and last_delimiter > start:
                        end = last_delimiter + len(delimiter)
                        break
                else:
                    # No sentence boundary found, try word boundary
                    last_space = text.rfind(' ', start, end)
                    if last_space != -1 and last_space > start:
                        end = last_space
            
            # Extract chunk
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                chunks.append({
                    'chunk_index': chunk_index,
                    'text': chunk_text,
                    'section': section,
                    'chunk_type': 'text'
                })
                chunk_index += 1
            
            # Move start position (with overlap)
            start = end - self.chunk_overlap if end < len(text) else end
            
            # Prevent infinite loop
            if start <= 0:
                start = end
        
        return chunks
    
    def chunk_sections(self, sections: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Chunk multiple sections from a document
        
        Args:
            sections: Dictionary of section_name -> text
            
        Returns:
            List of chunk dictionaries
        """
        all_chunks = []
        global_chunk_index = 0
        
        for section_name, section_text in sections.items():
            if not section_text or not section_text.strip():
                continue
            
            section_chunks = self.chunk_text(section_text, section_name)
            
            # Update chunk indices to be global
            for chunk in section_chunks:
                chunk['chunk_index'] = global_chunk_index
                global_chunk_index += 1
                all_chunks.append(chunk)
        
        return all_chunks
    
    def chunk_with_metadata(self, full_text: str, sections: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """
        Smart chunking that tries to use sections if available, falls back to full text
        
        Args:
            full_text: Complete document text
            sections: Optional dictionary of sections
            
        Returns:
            List of chunk dictionaries
        """
        if sections and any(text.strip() for text in sections.values()):
            # Use section-based chunking
            return self.chunk_sections(sections)
        else:
            # Fall back to chunking the full text
            return self.chunk_text(full_text, section='full_text')


def get_chunker() -> TextChunker:
    """Get a text chunker instance"""
    return TextChunker()
