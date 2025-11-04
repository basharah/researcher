import PyPDF2
import pdfplumber
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import statistics


class PDFParser:
    """Parse PDF files to extract comprehensive research paper content.

    Features:
    - Text extraction with two-column layout detection
    - Title and authors extraction from layout analysis
    - Table extraction with structure preservation
    - Figure/image extraction with captions
    - References parsing
    """

    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    def extract_metadata(self) -> Dict:
        """Extract metadata and try to populate title/authors using layout heuristics."""
        metadata: Dict[str, Optional[object]] = {
            'title': None,
            'authors': [],
            'page_count': 0,
            'creation_date': None
        }

        try:
            with open(self.pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                metadata['page_count'] = len(pdf_reader.pages)

                # Extract metadata if available
                if pdf_reader.metadata:
                    metadata['title'] = pdf_reader.metadata.get('/Title')
                    author = pdf_reader.metadata.get('/Author')
                    if author:
                        # Authors string may be semicolon/comma separated
                        metadata['authors'] = [a.strip() for a in re_split_authors(author)]
                    metadata['creation_date'] = pdf_reader.metadata.get('/CreationDate')

        except Exception as e:
            print(f"Error extracting basic metadata: {e}")

        # If title/authors missing, attempt layout-based extraction from first page
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                if len(pdf.pages) > 0:
                    first_page = pdf.pages[0]
                    title, authors = self._extract_title_and_authors_from_page(first_page)
                    if not metadata['title'] and title:
                        metadata['title'] = title
                    if not metadata['authors'] and authors:
                        metadata['authors'] = authors

        except Exception as e:
            print(f"Error doing layout-based metadata extraction: {e}")

        return metadata

    def extract_text(self) -> str:
        """Extract all text from PDF, attempting to preserve column reading order."""
        full_text = []

        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = self._extract_text_from_page(page)
                    if page_text:
                        full_text.append(page_text)

        except Exception as e:
            print(f"Error extracting text with pdfplumber: {e}")
            # Fallback to PyPDF2 simple extraction
            try:
                with open(self.pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        txt = page.extract_text() or ""
                        full_text.append(txt)
            except Exception as e2:
                print(f"Fallback extraction also failed: {e2}")

        return "\n\n".join(p for p in full_text if p).strip()

    def extract_text_by_page(self) -> List[str]:
        """Extract text page by page (preserving columns when possible)."""
        pages: List[str] = []

        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for page in pdf.pages:
                    pages.append(self._extract_text_from_page(page) or "")

        except Exception as e:
            print(f"Error extracting text by page: {e}")

        return pages

    def extract_tables(self) -> List[Dict]:
        """Extract all tables from the PDF with structure and metadata.
        
        Returns:
            List of dicts with keys: page, table_num, data, bbox, caption
        """
        tables_data = []
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    # Extract tables from this page
                    page_tables = page.extract_tables()
                    
                    if not page_tables:
                        continue
                    
                    # Get page text for caption detection
                    page_text = page.extract_text() or ""
                    
                    for table_idx, table in enumerate(page_tables, start=1):
                        if not table or not any(table):  # Skip empty tables
                            continue
                        
                        # Try to find caption near this table
                        caption = self._find_table_caption(page_text, table_idx)
                        
                        # Get table bounding box if available
                        bbox = None
                        try:
                            table_settings = page.find_tables()[table_idx - 1]
                            if table_settings:
                                bbox = table_settings.bbox
                        except (IndexError, AttributeError):
                            pass
                        
                        tables_data.append({
                            'page': page_num,
                            'table_num': table_idx,
                            'data': table,  # 2D list: [[row1], [row2], ...]
                            'bbox': bbox,
                            'caption': caption,
                            'row_count': len(table),
                            'col_count': len(table[0]) if table else 0
                        })
        
        except Exception as e:
            print(f"Error extracting tables: {e}")
        
        return tables_data

    def extract_figures(self, output_dir: Optional[Path] = None) -> List[Dict]:
        """Extract images/figures from PDF and save them.
        
        Args:
            output_dir: Directory to save extracted images. If None, uses pdf directory.
            
        Returns:
            List of dicts with keys: page, figure_num, file_path, bbox, caption, type
        """
        if output_dir is None:
            output_dir = self.pdf_path.parent / 'figures'
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        figures_data = []
        pdf_name = self.pdf_path.stem
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    # Get page text for caption detection
                    page_text = page.extract_text() or ""
                    
                    # Extract images from this page
                    images = page.images
                    
                    for img_idx, img in enumerate(images, start=1):
                        try:
                            # Get image bounding box
                            bbox = (img.get('x0'), img.get('top'), 
                                   img.get('x1'), img.get('bottom'))
                            
                            # Try to find caption
                            caption = self._find_figure_caption(page_text, img_idx)
                            
                            # Save image using page.crop and convert to PIL
                            img_bbox = (img['x0'], img['top'], img['x1'], img['bottom'])
                            cropped = page.crop(img_bbox)
                            
                            # Generate filename
                            filename = f"{pdf_name}_p{page_num}_fig{img_idx}.png"
                            file_path = output_dir / filename
                            
                            # Convert to image and save
                            try:
                                im = cropped.to_image(resolution=150)
                                im.save(str(file_path))
                            except Exception as save_error:
                                print(f"Could not save image: {save_error}")
                                file_path = None
                            
                            figures_data.append({
                                'page': page_num,
                                'figure_num': img_idx,
                                'file_path': str(file_path) if file_path else None,
                                'bbox': bbox,
                                'caption': caption,
                                'width': img.get('width'),
                                'height': img.get('height')
                            })
                        
                        except Exception as img_error:
                            print(f"Error processing image {img_idx} on page {page_num}: {img_error}")
                            continue
        
        except Exception as e:
            print(f"Error extracting figures: {e}")
        
        return figures_data

    def extract_references(self) -> List[Dict]:
        """Extract references/bibliography from the paper.
        
        Returns:
            List of dicts with keys: index, text, title, authors, year, venue
        """
        references = []
        
        try:
            # First, extract the full text
            full_text = self.extract_text()
            
            # Find the references section
            ref_section = self._extract_references_section(full_text)
            
            if not ref_section:
                return references
            
            # Parse individual references
            references = self._parse_references(ref_section)
        
        except Exception as e:
            print(f"Error extracting references: {e}")
        
        return references

    def _extract_text_from_page(self, page) -> str:
        """Extract text from a single pdfplumber page, handling 1- or 2-column layouts.

        Strategy:
        - Use character density projection across the width to find a large vertical gap.
        - If a gap exists (likely two-column), crop and extract each column separately.
        - Otherwise fall back to page.extract_text().
        """
        try:
            # Quick path: if page has no chars, fallback
            if not getattr(page, 'chars', None):
                return page.extract_text() or ""

            page_width = page.width
            # Build horizontal projection: count chars per 10px bin
            bin_size = max(8, int(page_width / 100))
            bins = [0] * (int(page_width // bin_size) + 1)
            for ch in page.chars:
                x_center = (ch['x0'] + ch['x1']) / 2
                idx = int(x_center // bin_size)
                bins[idx] += 1

            # Smooth bins by simple moving average
            smoothed = []
            w = 3
            for i in range(len(bins)):
                window = bins[max(0, i - w):min(len(bins), i + w + 1)]
                smoothed.append(sum(window) / max(1, len(window)))

            max_density = max(smoothed) if smoothed else 0

            # Find a low-density gap near the middle third of the page
            gap_idx = None
            start_search = int(len(smoothed) * 0.25)
            end_search = int(len(smoothed) * 0.75)
            for i in range(start_search, end_search):
                if smoothed[i] < 0.08 * max_density:  # threshold
                    gap_idx = i
                    break

            if gap_idx is not None:
                gap_x = gap_idx * bin_size
                # Crop left and right columns (add small padding)
                padding = bin_size // 2
                left_bbox = (0, 0, max(0, gap_x + padding), page.height)
                right_bbox = (min(page_width, gap_x - padding), 0, page_width, page.height)

                left = page.crop(left_bbox).extract_text() or ""
                right = page.crop(right_bbox).extract_text() or ""

                # Join columns in natural reading order: top-to-bottom left then right
                combined = (left.strip() + "\n\n" + right.strip()).strip()
                # If combined is empty fall back
                if combined:
                    return combined

            # No obvious two-column gap found, use default extraction
            return page.extract_text() or ""

        except Exception as e:
            print(f"_extract_text_from_page error: {e}")
            try:
                return page.extract_text() or ""
            except Exception:
                return ""

    def _extract_title_and_authors_from_page(self, page) -> Tuple[Optional[str], List[str]]:
        """Attempt to extract a title and list of authors from the first page using layout.

        Heuristics:
        - Group characters into text lines by their vertical 'top' coordinate (with tolerance).
        - Compute average font size per line; the title usually has the largest avg font size near the top.
        - Authors are often the next one or two lines after the title and contain commas / 'and' / affiliation words.
        """
        try:
            if not getattr(page, 'chars', None):
                return None, []

            # Group chars into lines by rounded top coordinate
            line_map = {}
            for ch in page.chars:
                top_key = int(round(ch['top']))
                if top_key not in line_map:
                    line_map[top_key] = []
                line_map[top_key].append(ch)

            # Build ordered lines (top -> text, avg_size)
            lines = []
            for top in sorted(line_map.keys()):
                chars = sorted(line_map[top], key=lambda c: c['x0'])
                text = ''.join(c.get('text', '') for c in chars).strip()
                if not text:
                    continue
                sizes = [c.get('size', 0) for c in chars if c.get('size')]
                avg_size = float(statistics.mean(sizes)) if sizes else 0.0
                lines.append({'top': top, 'text': text, 'avg_size': avg_size})

            if not lines:
                return None, []

            # Restrict to top portion of the page (e.g., top 30%)
            page_height = page.height
            top_lines = [line for line in lines if line['top'] < page_height * 0.35]
            if not top_lines:
                top_lines = lines[:8]

            # Title candidate: line with max avg_size in top_lines
            title_candidate = max(top_lines, key=lambda item: item['avg_size'])
            title_text = title_candidate['text'] if title_candidate['avg_size'] > 6 else None

            # Authors: lines after the title line within top_lines
            title_index = None
            for i, line in enumerate(top_lines):
                if line is title_candidate:
                    title_index = i
                    break

            if title_index is None:
                title_index = 0

            # Collect next up to 3 lines after title_index as author block
            author_block_lines = []
            for line in top_lines[title_index + 1:title_index + 4]:
                txt = line['text']
                # skip if looks like short header (e.g., conference, date)
                if len(txt) < 3:
                    continue
                author_block_lines.append(txt)

            # Join and split likely author names by commas, ' and ', semicolons
            joined = ' '.join(author_block_lines)
            candidates = re_split_authors(joined)
            
            # If no separators found or any candidate looks like multiple concatenated names,
            # try to detect and split them
            expanded_candidates = []
            for candidate in candidates:
                if len(candidate.split()) > 5:
                    # Might be multiple names concatenated
                    expanded_candidates.extend(split_concatenated_names(candidate))
                else:
                    expanded_candidates.append(candidate)
            
            candidates = expanded_candidates


            # Filter out lines that look like affiliations or emails
            filtered = []
            for c in candidates:
                low = c.lower()
                if not c.strip():
                    continue
                # More comprehensive affiliation filters
                affiliation_keywords = [
                    '@', 'university', 'institute', 'dept', 'department', 'dep.', 
                    'school', 'laboratory', 'lab', 'college', 'center', 'centre',
                    'inc.', 'llc', 'corp', 'company', 'systems', 'processing',
                    'management', 'technical', 'state', 'national', 'orcid:',
                    'usa', 'russia', 'china', 'moscow', 'beijing', 'london',
                    'new york', 'california', 'email', '.com', '.edu', '.org'
                ]
                is_affiliation = any(keyword in low for keyword in affiliation_keywords)
                
                if is_affiliation:
                    # treat as affiliation, skip as author
                    continue
                    
                # Remove stray footnote markers and punctuation
                cleaned = c.strip().strip('.,;*†‡§¶#')
                
                # Basic name heuristic: should have 2-5 words, each capitalized
                words = cleaned.split()
                if len(words) < 2 or len(words) > 5:
                    continue
                    
                # Check if it looks like a name (most words start with capital)
                capital_words = sum(1 for w in words if w and w[0].isupper())
                if capital_words >= len(words) * 0.6:  # At least 60% capitalized
                    filtered.append(cleaned)

            # If none filtered but we have raw lines, try taking each line as an author entry
            if not filtered and author_block_lines:
                for line in author_block_lines:
                    if len(line.split()) <= 10:
                        # Apply same filters
                        low = line.lower()
                        affiliation_keywords = [
                            '@', 'university', 'institute', 'dept', 'department', 'dep.',
                            'inc.', 'systems', 'processing', 'orcid:'
                        ]
                        if not any(keyword in low for keyword in affiliation_keywords):
                            filtered.append(line.strip())

            return title_text, filtered

        except Exception as e:
            print(f"_extract_title_and_authors_from_page error: {e}")
            return None, []

    def _find_table_caption(self, page_text: str, table_num: int) -> Optional[str]:
        """Find caption for a table on the page."""
        import re
        
        # Look for patterns like "Table 1:", "TABLE I:", "Tab. 1.", etc.
        patterns = [
            rf'Table\s+{table_num}[:\.]?\s*([^\n]+)',
            rf'TABLE\s+{table_num}[:\.]?\s*([^\n]+)',
            rf'Tab\.\s*{table_num}[:\.]?\s*([^\n]+)',
        ]
        
        # Also try Roman numerals for first few tables
        roman = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']
        if table_num <= len(roman):
            patterns.append(rf'Table\s+{roman[table_num-1]}[:\.]?\s*([^\n]+)')
            patterns.append(rf'TABLE\s+{roman[table_num-1]}[:\.]?\s*([^\n]+)')
        
        for pattern in patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                caption = match.group(1).strip()
                # Limit caption length to avoid capturing too much
                if len(caption) > 200:
                    caption = caption[:200] + '...'
                return caption
        
        return None

    def _find_figure_caption(self, page_text: str, fig_num: int) -> Optional[str]:
        """Find caption for a figure on the page."""
        import re
        
        # Look for patterns like "Figure 1:", "Fig. 1:", "FIG. 1.", etc.
        patterns = [
            rf'Figure\s+{fig_num}[:\.]?\s*([^\n]+)',
            rf'Fig\.\s*{fig_num}[:\.]?\s*([^\n]+)',
            rf'FIG\.\s*{fig_num}[:\.]?\s*([^\n]+)',
            rf'FIGURE\s+{fig_num}[:\.]?\s*([^\n]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                caption = match.group(1).strip()
                # Limit caption length
                if len(caption) > 200:
                    caption = caption[:200] + '...'
                return caption
        
        return None

    def _extract_references_section(self, full_text: str) -> Optional[str]:
        """Extract the references/bibliography section from paper text."""
        import re
        
        # Common section headers for references
        ref_headers = [
            r'\n\s*REFERENCES\s*\n',
            r'\n\s*References\s*\n',
            r'\n\s*BIBLIOGRAPHY\s*\n',
            r'\n\s*Bibliography\s*\n',
            r'\n\s*WORKS\s+CITED\s*\n',
        ]
        
        for pattern in ref_headers:
            match = re.search(pattern, full_text)
            if match:
                # Extract from this point to end (or to appendix if exists)
                start_pos = match.end()
                
                # Try to find where references end (appendix, acknowledgments, etc.)
                end_patterns = [
                    r'\n\s*APPENDIX',
                    r'\n\s*Appendix',
                    r'\n\s*ACKNOWLEDGMENTS',
                    r'\n\s*Acknowledgments',
                ]
                
                end_pos = len(full_text)
                for end_pattern in end_patterns:
                    end_match = re.search(end_pattern, full_text[start_pos:])
                    if end_match:
                        end_pos = start_pos + end_match.start()
                        break
                
                return full_text[start_pos:end_pos].strip()
        
        return None

    def _parse_references(self, ref_text: str) -> List[Dict]:
        """Parse individual references from the references section.
        
        This is a basic implementation that splits on common patterns.
        For production, consider using specialized libraries like anystyle or grobid.
        """
        import re
        
        references: List[Dict] = []
        
        # Split references by numbered patterns: [1], [2], etc. or 1. 2. etc.
        # Try bracketed numbers first
        ref_pattern = r'\[(\d+)\]\s*([^\[]+?)(?=\[\d+\]|$)'
        matches = re.findall(ref_pattern, ref_text, re.DOTALL)
        
        if not matches:
            # Try plain numbered list: 1. 2. 3.
            ref_pattern = r'(?:^|\n)(\d+)\.\s*([^\n]+(?:\n(?!\d+\.)[^\n]+)*)'
            matches = re.findall(ref_pattern, ref_text, re.MULTILINE)
        
        if not matches:
            # Fallback: split by double newlines
            parts = [p.strip() for p in ref_text.split('\n\n') if p.strip()]
            matches = [(str(i+1), part) for i, part in enumerate(parts)]
        
        for idx_str, ref_content in matches:
            ref_content = ref_content.strip()
            
            # Basic parsing (very simplified - production would use proper citation parser)
            parsed = {
                'index': int(idx_str) if idx_str.isdigit() else len(references) + 1,
                'text': ref_content,
                'title': self._extract_ref_title(ref_content),
                'authors': self._extract_ref_authors(ref_content),
                'year': self._extract_ref_year(ref_content),
                'venue': None  # Could be extracted with more sophisticated parsing
            }
            
            references.append(parsed)
        
        return references

    def _extract_ref_title(self, ref_text: str) -> Optional[str]:
        """Extract title from a reference (very basic heuristic)."""
        import re
        
        # Look for quoted title
        quoted = re.search(r'"([^"]+)"', ref_text)
        if quoted:
            return quoted.group(1)
        
        # Look for title in italics (if preserved in text)
        # This is a fallback - often titles are just capitalized
        return None

    def _extract_ref_authors(self, ref_text: str) -> List[str]:
        """Extract authors from a reference (very basic)."""
        # Very simplified: take text before first period or comma list before year
        # Production would use citation parsing library
        parts = ref_text.split('.')
        if parts:
            first_part = parts[0].strip()
            # Could be authors
            if len(first_part) < 100:
                return [first_part]
        return []

    def _extract_ref_year(self, ref_text: str) -> Optional[int]:
        """Extract publication year from a reference."""
        import re
        
        # Look for 4-digit year in parentheses or standalone
        year_patterns = [
            r'\((\d{4})\)',  # (2023)
            r'\b(19\d{2}|20\d{2})\b',  # 1990-2099
        ]
        
        for pattern in year_patterns:
            match = re.search(pattern, ref_text)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    pass
        
        return None


def re_split_authors(text: Optional[str]) -> List[str]:
    """Split an authors string into candidate names using common separators."""
    if not text:
        return []
    # Replace newlines with space
    txt = ' '.join(text.splitlines())
    # split by commas, semicolons, ' and '
    parts = []
    for part in [p.strip() for p in re_split_candidates(txt) if p.strip()]:
        parts.append(part)
    return parts


def re_split_candidates(s: str) -> List[str]:
    import re
    # split on comma or semicolon or ' and ' (case-insensitive)
    parts = re.split(r',|;|\band\b', s, flags=re.IGNORECASE)
    return [p.strip() for p in parts if p.strip()]


def split_concatenated_names(text: str) -> List[str]:
    """Split a string that contains multiple names without clear separators.
    
    Heuristic: Look for patterns where multiple capital letters appear
    with spacing that suggests separate names (e.g., "John A. Smith  Mary B. Jones")
    """
    import re
    
    # Pattern: detect boundaries between names by looking for:
    # - Double spaces OR
    # - Pattern: lowercase-letter space Capital-letter (name boundary)
    
    # First try: Split on 2+ spaces (common in multi-column layouts)
    if '  ' in text:
        parts = [p.strip() for p in text.split('  ') if p.strip()]
        # Recursively split each part in case there are more names
        all_names = []
        for part in parts:
            # Check if this part still has multiple names (single space separated)
            subnames = split_single_space_names(part)
            all_names.extend(subnames)
        if all_names:
            return all_names
    
    # No double spaces, try single space pattern matching
    return split_single_space_names(text)


def split_single_space_names(text: str) -> List[str]:
    """Split names separated by single spaces using pattern matching.
    
    Pattern: "FirstName I. LastName FirstName I. LastName"
    """
    import re
    
    # Look for the pattern: Capital-word Initial(s). Capital-word [optional marker]
    # This matches: "Artem A. Sukhobokov" "Yury E. Gapanyuk" "Artem A. Vetoshkin*"
    pattern = r'([A-Z][a-z]+(?:\s+[A-Z]\.)+\s+[A-Z][a-z]+[*†‡§¶]?)'
    matches = re.findall(pattern, text)
    
    if len(matches) >= 2:  # Found multiple names
        return [m.strip('*†‡§¶ ') for m in matches]
    
    # Fallback: check if it looks like a valid single name
    words = text.strip().split()
    if 2 <= len(words) <= 4:
        capital_count = sum(1 for w in words if w and w[0].isupper())
        if capital_count >= len(words) * 0.5:
            return [text.strip('*†‡§¶ ')]
    
    # If all else fails, return as-is
    return [text]

