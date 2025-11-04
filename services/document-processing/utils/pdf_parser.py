import PyPDF2
import pdfplumber
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import statistics


class PDFParser:
    """Parse PDF files to extract text and metadata.

    Improvements over a straight `extract_text()`:
    - Detects two-column layouts using a simple horizontal projection heuristic
      and extracts left-then-right column text in reading order.
    - Attempts to extract title and authors from layout (font sizes / positions)
      on the first page when metadata isn't present.
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

