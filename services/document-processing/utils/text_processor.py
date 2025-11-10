import re
from typing import Dict, Optional, List

class TextProcessor:
    """Process extracted text to identify sections and structure"""
    
    def __init__(self, text: str):
        self.text = text
        self.lines = text.split('\n')
    
    def extract_sections(self) -> Dict[str, Optional[str]]:
        """
        Extract common research paper sections with improved accuracy
        
        Returns dictionary with sections: abstract, introduction, methodology, 
        results, conclusion, references
        
        Improvements:
        - Multiple pattern variations for each section
        - Roman numeral and numbered section detection
        - Fuzzy matching for common variations
        - Layout-based detection (all caps, spacing)
        """
        sections: Dict[str, Optional[str]] = {
            'abstract': None,
            'introduction': None,
            'methodology': None,
            'results': None,
            'conclusion': None,
            'references': None
        }
        
        # Enhanced section patterns with variations
        section_patterns = {
            'abstract': [
                r'^abstract\s*$',
                r'^summary\s*$',
                r'^\d+\.?\s*abstract\s*$',
                r'^[ivx]+\.?\s*abstract\s*$',
            ],
            'introduction': [
                r'^introduction\s*$',
                r'^background\s*$',
                r'^\d+\.?\s*introduction\s*$',
                r'^[ivx]+\.?\s*introduction\s*$',
                r'^1\.?\s+introduction\s*$',
                r'^i\.?\s+introduction\s*$',
            ],
            'methodology': [
                r'^methodology\s*$',
                r'^methods?\s*$',
                r'^materials?\s+and\s+methods?\s*$',
                r'^experimental\s+(setup|design|methods?)\s*$',
                r'^\d+\.?\s*(methodology|methods?)\s*$',
                r'^\d+\.?\s*materials?\s+and\s+methods?\s*$',
                r'^[ivx]+\.?\s*(methodology|methods?)\s*$',
                r'^[ivx]+\.?\s*materials?\s+and\s+methods?\s*$',
            ],
            'results': [
                r'^results?\s*$',
                r'^findings?\s*$',
                r'^experimental\s+results?\s*$',
                r'^\d+\.?\s*results?\s*$',
                r'^[ivx]+\.?\s*results?\s*$',
                r'^results?\s+and\s+discussion\s*$',
            ],
            'conclusion': [
                r'^conclusions?\s*$',
                r'^discussion\s*$',
                r'^concluding\s+remarks?\s*$',
                r'^summary\s+and\s+conclusions?\s*$',
                r'^\d+\.?\s*conclusions?\s*$',
                r'^\d+\.?\s*discussion\s*$',
                r'^[ivx]+\.?\s*conclusions?\s*$',
                r'^[ivx]+\.?\s*discussion\s*$',
                r'^discussion\s+and\s+conclusions?\s*$',
            ],
            'references': [
                r'^references?\s*$',
                r'^bibliography\s*$',
                r'^works?\s+cited\s*$',
                r'^literature\s+cited\s*$',
                r'^\d+\.?\s*references?\s*$',
                r'^[ivx]+\.?\s*references?\s*$',
            ]
        }
        
        # Find section boundaries with improved detection
        section_indices = self._find_section_headers(section_patterns)
        
        # Extract text between sections
        sorted_sections = sorted(section_indices.items(), key=lambda x: x[1])
        
        for idx, (section_name, start_idx) in enumerate(sorted_sections):
            # Find end index (start of next section or end of document)
            if idx + 1 < len(sorted_sections):
                end_idx = sorted_sections[idx + 1][1]
            else:
                end_idx = len(self.lines)
            
            # Extract section text (skip the header line)
            section_text = '\n'.join(self.lines[start_idx + 1:end_idx]).strip()
            sections[section_name] = section_text if section_text else None
        
        # If abstract not found by header, try heuristic extraction
        if not sections['abstract']:
            sections['abstract'] = self._extract_abstract_heuristic()
        
        # Post-processing: clean up sections
        for key in sections:
            if sections[key] is not None:
                sections[key] = self._clean_section_text(sections[key])
        
        return sections
    
    def _find_section_headers(self, section_patterns: Dict[str, List[str]]) -> Dict[str, int]:
        """
        Find section headers with improved detection logic
        
        Enhancements:
        - Check for ALL CAPS headers
        - Check for headers with special formatting (centered, bold markers)
        - Look for numbered/lettered sections
        - Ignore false positives (headers within sentences)
        """
        section_indices = {}
        
        for i, line in enumerate(self.lines):
            line_stripped = line.strip()
            line_lower = line_stripped.lower()
            
            # Skip very short lines or very long lines (likely not headers)
            if len(line_stripped) < 2 or len(line_stripped) > 100:
                continue
            
            # First, try to match against section patterns
            # If it matches a pattern, check if it looks like a header
            for section_name, patterns in section_patterns.items():
                # Skip if we already found this section
                if section_name in section_indices:
                    continue
                
                for pattern in patterns:
                    if re.match(pattern, line_lower, re.IGNORECASE):
                        # Found a pattern match - now validate it looks like a header
                        is_potential_header = (
                            self._is_all_caps(line_stripped) or  # ALL CAPS
                            self._has_header_formatting(line_stripped) or  # Special formatting
                            self._is_standalone_line(i) or  # Surrounded by blank lines
                            self._has_numbering(line_stripped) or  # Numbered section
                            self._is_short_line(line_stripped)  # Short line (likely header)
                        )
                        
                        # Accept the match
                        if is_potential_header:
                            section_indices[section_name] = i
                            break
                
                if section_name in section_indices:
                    break
        
        return section_indices
    
    def _is_short_line(self, text: str) -> bool:
        """Check if line is short (typical for section headers)"""
        # Section headers are usually less than 60 characters
        # and contain only a few words (up to 6 for compound sections like "Materials and Methods")
        word_count = len(text.split())
        return len(text) < 60 and word_count <= 6
    
    def _is_all_caps(self, text: str) -> bool:
        """Check if text is in ALL CAPS (excluding numbers and punctuation)"""
        letters = [c for c in text if c.isalpha()]
        if not letters:
            return False
        return all(c.isupper() for c in letters) and len(letters) >= 3
    
    def _has_header_formatting(self, text: str) -> bool:
        """Check for common header formatting indicators"""
        # Check for bold markers (**, __, etc.)
        if text.startswith('**') or text.startswith('__'):
            return True
        
        # Check for section numbering patterns
        if re.match(r'^(\d+\.|\d+\)|\([a-z]\)|\([ivx]+\))\s+[A-Z]', text):
            return True
        
        return False
    
    def _is_standalone_line(self, line_idx: int) -> bool:
        """Check if line is surrounded by blank lines (typical for headers)"""
        if line_idx == 0 or line_idx >= len(self.lines) - 1:
            return False
        
        prev_blank = not self.lines[line_idx - 1].strip()
        next_blank = not self.lines[line_idx + 1].strip()
        
        return prev_blank and next_blank
    
    def _has_numbering(self, text: str) -> bool:
        """Check if text starts with section numbering"""
        # Matches: "1.", "1.1", "I.", "A.", "(1)", etc.
        numbering_patterns = [
            r'^\d+\.?\s+',  # 1. or 1
            r'^[IVXLCDM]+\.?\s+',  # Roman numerals
            r'^[A-Z]\.?\s+',  # A. or A
            r'^\(\d+\)\s+',  # (1)
            r'^\([a-z]\)\s+',  # (a)
        ]
        
        for pattern in numbering_patterns:
            if re.match(pattern, text):
                return True
        
        return False
    
    def _clean_section_text(self, text: str) -> str:
        """Clean up section text by removing artifacts"""
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        # Remove page numbers and headers/footers
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line_stripped = line.strip()
            
            # Skip lines that are just page numbers
            if re.match(r'^\d+$', line_stripped):
                continue
            
            # Skip very short lines that might be artifacts
            if len(line_stripped) < 3:
                continue
            
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines).strip()
    
    def _extract_abstract_heuristic(self) -> Optional[str]:
        """
        Try to extract abstract using improved heuristics
        """
        # Look for abstract in first 150 lines (increased range)
        text_beginning = '\n'.join(self.lines[:150])
        
        # Pattern 1: Explicit "Abstract" keyword with content
        abstract_match = re.search(
            r'abstract[:\s]*(.+?)(?=\n\s*\n[A-Z\d]|introduction|keywords|$)',
            text_beginning,
            re.IGNORECASE | re.DOTALL
        )
        
        if abstract_match:
            abstract_text = abstract_match.group(1).strip()
            # Validate: abstract should be reasonable length (50-2000 words)
            word_count = len(abstract_text.split())
            if 50 <= word_count <= 2000:
                return abstract_text
        
        # Pattern 2: Look for summary section
        summary_match = re.search(
            r'summary[:\s]*(.+?)(?=\n\s*\n[A-Z]|introduction|$)',
            text_beginning,
            re.IGNORECASE | re.DOTALL
        )
        
        if summary_match:
            summary_text = summary_match.group(1).strip()
            word_count = len(summary_text.split())
            if 50 <= word_count <= 2000:
                return summary_text
        
        # Pattern 3: Heuristic - text after title/authors but before Introduction
        # This is a last resort approach
        intro_idx = self._find_introduction_index()
        if intro_idx > 10:  # Make sure there's content before introduction
            # Try to extract text between line 10 and introduction
            potential_abstract = '\n'.join(self.lines[10:intro_idx]).strip()
            word_count = len(potential_abstract.split())
            if 50 <= word_count <= 2000:
                return potential_abstract
        
        return None
    
    def _find_introduction_index(self) -> int:
        """Find the line index where introduction starts"""
        intro_patterns = [
            r'^introduction\s*$',
            r'^\d+\.?\s*introduction\s*$',
            r'^[ivx]+\.?\s*introduction\s*$',
        ]
        
        for i, line in enumerate(self.lines):
            line_lower = line.strip().lower()
            for pattern in intro_patterns:
                if re.match(pattern, line_lower):
                    return i
        
        return -1
    
    def extract_title(self) -> Optional[str]:
        """Extract paper title (usually in first few lines with larger font/capitals)"""
        # Simple heuristic: title is often in first 10 lines and may be in ALL CAPS
        for i in range(min(10, len(self.lines))):
            line = self.lines[i].strip()
            # Title is usually longer than 10 characters and not a URL or metadata
            if len(line) > 10 and not line.startswith('http') and '@' not in line:
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
            lines = [line.strip() for line in references_section.split('\n') if line.strip()]
            return len(lines)
        
        return numbered_refs
