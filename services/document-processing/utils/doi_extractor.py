"""
DOI Extraction Utility
Extracts and validates Digital Object Identifiers from PDFs
"""
import re
import requests
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

# DOI regex patterns
DOI_PATTERNS = [
    # Standard DOI format: 10.xxxx/xxxxx
    r'10\.\d{4,9}/[-._;()/:A-Z0-9]+',
    # With doi: prefix
    r'doi:\s*10\.\d{4,9}/[-._;()/:A-Z0-9]+',
    # With http://doi.org or https://doi.org
    r'(?:https?://)?(?:dx\.)?doi\.org/(10\.\d{4,9}/[-._;()/:A-Z0-9]+)',
]


class DOIExtractor:
    """Extract and validate DOIs from text"""
    
    @staticmethod
    def extract_dois(text: str) -> List[str]:
        """
        Extract all potential DOIs from text
        
        Args:
            text: Input text to search for DOIs
            
        Returns:
            List of unique DOIs found
        """
        dois = set()
        
        for pattern in DOI_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Clean up the DOI
                doi = match.strip()
                # Remove common prefixes
                doi = re.sub(r'^doi:\s*', '', doi, flags=re.IGNORECASE)
                doi = re.sub(r'^(?:https?://)?(?:dx\.)?doi\.org/', '', doi, flags=re.IGNORECASE)
                # Normalize to lowercase for the prefix
                if doi.startswith('10.'):
                    dois.add(doi)
        
        return list(dois)
    
    @staticmethod
    def validate_doi(doi: str, timeout: int = 5) -> Dict[str, Any]:
        """
        Validate a DOI using the CrossRef API
        
        Args:
            doi: DOI to validate
            timeout: Request timeout in seconds
            
        Returns:
            Dict with validation result and metadata
        """
        try:
            # Query CrossRef API
            url = f"https://api.crossref.org/works/{doi}"
            headers = {
                'User-Agent': 'ResearchPaperAnalysis/1.0 (mailto:researcher@example.com)'
            }
            
            response = requests.get(url, headers=headers, timeout=timeout)
            
            if response.status_code == 200:
                data = response.json()
                message = data.get('message', {})
                
                return {
                    'valid': True,
                    'doi': doi,
                    'title': message.get('title', [None])[0],
                    'authors': [
                        f"{author.get('given', '')} {author.get('family', '')}".strip()
                        for author in message.get('author', [])
                    ],
                    'published': message.get('published-print', {}).get('date-parts', [[None]])[0],
                    'publisher': message.get('publisher'),
                    'type': message.get('type'),
                }
            else:
                return {'valid': False, 'doi': doi, 'error': f'HTTP {response.status_code}'}
                
        except requests.RequestException as e:
            logger.warning(f"Failed to validate DOI {doi}: {e}")
            return {'valid': False, 'doi': doi, 'error': str(e)}
        except Exception as e:
            logger.error(f"Unexpected error validating DOI {doi}: {e}")
            return {'valid': False, 'doi': doi, 'error': str(e)}
    
    @staticmethod
    def extract_and_validate(text: str, validate: bool = True) -> Optional[str]:
        """
        Extract DOI from text and optionally validate it
        
        Args:
            text: Input text
            validate: Whether to validate using CrossRef API
            
        Returns:
            The first valid DOI found, or None
        """
        dois = DOIExtractor.extract_dois(text)
        
        if not dois:
            return None
        
        # Try to find a valid DOI
        for doi in dois:
            if validate:
                result = DOIExtractor.validate_doi(doi)
                if result.get('valid'):
                    logger.info(f"Found and validated DOI: {doi}")
                    return doi
            else:
                # Return first DOI without validation
                logger.info(f"Found DOI (not validated): {doi}")
                return doi
        
        # If validation failed for all, return the first one anyway
        if dois:
            logger.warning(f"Found DOIs but validation failed, using first: {dois[0]}")
            return dois[0]
        
        return None
    
    @staticmethod
    def extract_from_pdf_metadata(pdf_info: Dict[str, Any]) -> Optional[str]:
        """
        Extract DOI from PDF metadata dict
        
        Args:
            pdf_info: PDF metadata dictionary
            
        Returns:
            DOI if found in metadata
        """
        # Check common metadata fields
        for field in ['/Subject', '/doi', '/DOI', '/Keywords']:
            if field in pdf_info:
                value = pdf_info[field]
                if isinstance(value, str):
                    dois = DOIExtractor.extract_dois(value)
                    if dois:
                        return dois[0]
        
        return None
