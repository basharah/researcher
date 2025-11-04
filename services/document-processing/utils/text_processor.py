import re
from typing import Dict, Optional, List

class TextProcessor:
    """Process extracted text to identify sections and structure"""
    
    def __init__(self, text: str):
        self.text = text
        self.lines = text.split('\n')
    
    def extract_sections(self) -> Dict[str, Optional[str]]:
        """
        Extract common research paper sections
        
        Returns dictionary with sections: abstract, introduction, methodology, 
        results, conclusion, references
        """
        sections = {
            'abstract': None,
            'introduction': None,
            'methodology': None,
            'results': None,
            'conclusion': None,
            'references': None
        }
        
        # Common section headers (case-insensitive patterns)
        section_patterns = {
            'abstract': r'^(abstract|summary)\s*$',
            'introduction': r'^(introduction|background)\s*$',
            'methodology': r'^(methodology|methods|materials\s+and\s+methods)\s*$',
            'results': r'^(results|findings)\s*$',
            'conclusion': r'^(conclusion|conclusions|discussion)\s*$',
            'references': r'^(references|bibliography|works\s+cited)\s*$'
        }
        
        # Find section boundaries
        section_indices = {}
        
        for i, line in enumerate(self.lines):
            line_clean = line.strip().lower()
            for section_name, pattern in section_patterns.items():
                if re.match(pattern, line_clean, re.IGNORECASE):
                    section_indices[section_name] = i
                    break
        
        # Extract text between sections
        sorted_sections = sorted(section_indices.items(), key=lambda x: x[1])
        
        for idx, (section_name, start_idx) in enumerate(sorted_sections):
            # Find end index (start of next section or end of document)
            if idx + 1 < len(sorted_sections):
                end_idx = sorted_sections[idx + 1][1]
            else:
                end_idx = len(self.lines)
            
            # Extract section text
            section_text = '\n'.join(self.lines[start_idx + 1:end_idx]).strip()
            sections[section_name] = section_text if section_text else None
        
        # If abstract not found by header, try to extract from beginning
        if not sections['abstract']:
            sections['abstract'] = self._extract_abstract_heuristic()
        
        return sections
    
    def _extract_abstract_heuristic(self) -> Optional[str]:
        """
        Try to extract abstract using heuristics if not found by header matching
        Usually the abstract is at the beginning of the paper
        """
        # Look for abstract in first 100 lines
        text_beginning = '\n'.join(self.lines[:100])
        
        # Look for "Abstract" keyword
        abstract_match = re.search(
            r'abstract[:\s]*(.+?)(?=\n\s*\n|\n[A-Z][a-z]+:)',
            text_beginning,
            re.IGNORECASE | re.DOTALL
        )
        
        if abstract_match:
            return abstract_match.group(1).strip()
        
        return None
    
    def extract_title(self) -> Optional[str]:
        """Extract paper title (usually in first few lines with larger font/capitals)"""
        # Simple heuristic: title is often in first 10 lines and may be in ALL CAPS
        for i in range(min(10, len(self.lines))):
            line = self.lines[i].strip()
            # Title is usually longer than 10 characters and not a URL or metadata
            if len(line) > 10 and not line.startswith('http') and not '@' in line:
                return line
        return None
    
    def extract_keywords(self) -> List[str]:
        """Extract keywords if present"""
        keywords = []
        
        # Look for keywords section
        keywords_match = re.search(
            r'keywords?[:\s]*(.+?)(?=\n\s*\n)',
            self.text,
            re.IGNORECASE
        )
        
        if keywords_match:
            keywords_text = keywords_match.group(1)
            # Split by common separators
            keywords = [k.strip() for k in re.split(r'[;,]', keywords_text)]
        
        return keywords
    
    def count_references(self) -> int:
        """Count number of references in the paper"""
        references_section = self.extract_sections().get('references', '')
        if not references_section:
            return 0
        
        # Count numbered references [1], [2], etc.
        numbered_refs = len(re.findall(r'\[\d+\]', references_section))
        
        # Count line-based references (each line is a reference)
        if numbered_refs == 0:
            lines = [l.strip() for l in references_section.split('\n') if l.strip()]
            return len(lines)
        
        return numbered_refs
