#!/bin/bash
# Quick integration test for improved section detection

echo "Testing improved section detection..."
echo "========================================"
echo ""

# Test 1: Basic headers
echo "Test 1: Basic headers"
docker exec document-processing-service python -c "
from utils.text_processor import TextProcessor

text = '''
Title of Paper

Abstract
This is the abstract of the paper.

Introduction
This is the introduction.

Methods
Research methodology.

Results
Experimental results.

Conclusion
Final thoughts.

References
[1] Reference
'''

processor = TextProcessor(text)
sections = processor.extract_sections()

for name, content in sections.items():
    status = '✓' if content else '✗'
    print(f'{status} {name}')
"
echo ""

# Test 2: Numbered sections
echo "Test 2: Numbered sections"
docker exec document-processing-service python -c "
from utils.text_processor import TextProcessor

text = '''
Abstract
Paper summary.

1. Introduction
Background info.

2. Materials and Methods
Experimental setup.

3. Results
Findings.

4. Conclusions
Final remarks.

5. References
Citations.
'''

processor = TextProcessor(text)
sections = processor.extract_sections()

for name, content in sections.items():
    status = '✓' if content else '✗'
    print(f'{status} {name}')
"
echo ""

# Test 3: ALL CAPS headers
echo "Test 3: ALL CAPS headers"
docker exec document-processing-service python -c "
from utils.text_processor import TextProcessor

text = '''
ABSTRACT
Summary of research.

INTRODUCTION
Background.

METHODOLOGY
Methods used.

RESULTS
Experimental data.

CONCLUSION
Final thoughts.

REFERENCES
Bibliography.
'''

processor = TextProcessor(text)
sections = processor.extract_sections()

for name, content in sections.items():
    status = '✓' if content else '✗'
    print(f'{status} {name}')
"
echo ""

# Test 4: Roman numerals
echo "Test 4: Roman numeral sections"
docker exec document-processing-service python -c "
from utils.text_processor import TextProcessor

text = '''
Abstract
Paper overview.

I. Introduction
Historical context.

II. Methodology
Research design.

III. Results
Data analysis.

IV. Discussion
Interpretation.

V. References
Citations list.
'''

processor = TextProcessor(text)
sections = processor.extract_sections()

for name, content in sections.items():
    status = '✓' if content else '✗'
    print(f'{status} {name}')
"
echo ""

echo "========================================"
echo "Section detection tests complete!"
