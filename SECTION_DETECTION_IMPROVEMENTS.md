# Section Detection Improvements

## Overview
Enhanced the `TextProcessor.extract_sections()` method to significantly improve section detection accuracy across various research paper formats.

## Key Improvements

### 1. Multiple Pattern Variations
Each section type now supports multiple header formats:
- **Abstract**: "Abstract", "Summary" (with/without numbering)
- **Introduction**: "Introduction", "Background" (numbered, Roman numerals)
- **Methodology**: "Methods", "Methodology", "Materials and Methods", "Experimental Setup/Design/Methods"
- **Results**: "Results", "Findings", "Experimental Results", "Results and Discussion"
- **Conclusion**: "Conclusion", "Conclusions", "Discussion", "Concluding Remarks", "Summary and Conclusions", "Discussion and Conclusions"
- **References**: "References", "Bibliography", "Works Cited", "Literature Cited"

### 2. Numbering Support
Now detects sections with various numbering schemes:
- **Arabic numerals**: `1. Introduction`, `2. Methods`
- **Roman numerals**: `I. Introduction`, `II. Methods`, `III. Results`
- **With/without dots**: `1 Introduction` or `1. Introduction`
- **Lowercase Roman**: `i. Introduction`, `ii. Methods`

### 3. Format Detection
Improved header recognition through multiple heuristics:
- **ALL CAPS headers**: `ABSTRACT`, `INTRODUCTION`, `METHODOLOGY`
- **Short lines**: Headers are typically < 60 chars with ≤ 6 words
- **Standalone lines**: Headers surrounded by blank lines
- **Numbered sections**: Automatic detection of numbering patterns
- **Special formatting**: Detection of bold markers (`**`, `__`)

### 4. Enhanced Heuristic Abstract Extraction
Multi-strategy fallback when explicit "Abstract" header not found:
1. **Pattern 1**: Search for "Abstract" keyword with content validation (50-2000 words)
2. **Pattern 2**: Look for "Summary" section
3. **Pattern 3**: Position-based heuristic - extract text between title/authors and Introduction
4. All strategies validate content length to avoid false positives

### 5. Content Cleaning
Post-processing to improve section quality:
- Remove excessive whitespace (multiple blank lines)
- Filter out page numbers (standalone digits)
- Remove very short lines (likely artifacts)
- Preserve paragraph structure

## Testing

### Test Coverage
Created comprehensive test suite (`test-section-detection.sh`) covering:

1. **Basic Headers** - Standard section names without formatting
2. **Numbered Sections** - Arabic numeral prefixes (1., 2., etc.)
3. **ALL CAPS Headers** - Headers in uppercase
4. **Roman Numeral Sections** - Roman numeral prefixes (I., II., III., etc.)
5. **Section Variations** - Alternative names (Summary, Background, Findings, etc.)

### Test Results
All tests passing ✅:
- ✓ Abstract detection (including heuristic extraction)
- ✓ Introduction detection (all formats)
- ✓ Methodology/Methods detection (including "Materials and Methods")
- ✓ Results detection (including "Results and Discussion")
- ✓ Conclusion/Discussion detection
- ✓ References/Bibliography detection

## Usage Example

```python
from utils.text_processor import TextProcessor

text = """
ABSTRACT
This paper presents a novel approach...

I. INTRODUCTION
Machine learning has become...

II. MATERIALS AND METHODS
We used the following experimental setup...

III. RESULTS AND DISCUSSION
The experiments showed...

IV. CONCLUSIONS
We conclude that...

V. REFERENCES
[1] Smith et al. (2023)
"""

processor = TextProcessor(text)
sections = processor.extract_sections()

# Access sections
print(sections['abstract'])      # Extracted abstract
print(sections['introduction'])  # Introduction section
print(sections['methodology'])   # Methods section
# ... etc.
```

## Impact on Document Processing

These improvements enhance the quality of:
1. **Document indexing** - Better section-based retrieval
2. **Semantic search** - More accurate section filtering
3. **LLM analysis** - Better context extraction for AI analysis
4. **Metadata extraction** - Improved structure understanding

## Technical Details

### Pattern Regex Examples
```python
# Methodology patterns (8 variations)
r'^methodology\s*$'                              # Basic
r'^methods?\s*$'                                 # Method/Methods
r'^materials?\s+and\s+methods?\s*$'              # Materials and Methods
r'^experimental\s+(setup|design|methods?)\s*$'   # Experimental variations
r'^\d+\.?\s*(methodology|methods?)\s*$'          # Numbered
r'^\d+\.?\s*materials?\s+and\s+methods?\s*$'     # Numbered Materials and Methods
r'^[ivx]+\.?\s*(methodology|methods?)\s*$'       # Roman numerals
r'^[ivx]+\.?\s*materials?\s+and\s+methods?\s*$'  # Roman Materials and Methods
```

### Header Detection Heuristics
```python
is_potential_header = (
    _is_all_caps(line) or          # ALL CAPS
    _has_header_formatting(line) or # Bold markers, special chars
    _is_standalone_line(i) or       # Blank lines before/after
    _has_numbering(line) or         # 1., I., etc.
    _is_short_line(line)            # < 60 chars, ≤ 6 words
)
```

## Files Modified
- `services/document-processing/utils/text_processor.py` (334 lines)
  - Enhanced `extract_sections()` method
  - Added `_find_section_headers()` with improved logic
  - Added `_is_all_caps()`, `_has_header_formatting()`, `_is_standalone_line()`, `_has_numbering()`, `_is_short_line()` helper methods
  - Improved `_extract_abstract_heuristic()` with multi-strategy approach
  - Added `_clean_section_text()` for content post-processing

## Performance
- No significant performance impact (still regex-based, O(n) where n = number of lines)
- Header detection happens once per document upload
- Results cached in database (no repeated processing)

## Future Enhancements (Optional)
- Machine learning-based section classification
- Font/style analysis (requires PDF parser updates)
- Subsection detection (2.1, 2.2, etc.)
- Multi-language support (detect sections in different languages)
- Confidence scores for each detected section
