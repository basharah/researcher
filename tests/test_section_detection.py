#!/usr/bin/env python3
"""
Test script for improved section detection in TextProcessor

Tests various section header formats:
- Basic headers (Abstract, Introduction)
- Numbered sections (1. Introduction, 2. Methods)
- Roman numerals (I. Introduction, II. Methods)
- ALL CAPS headers
- Common variations (Materials and Methods, Results and Discussion)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'services/document-processing'))

from utils.text_processor import TextProcessor

def test_basic_headers():
    """Test basic section headers"""
    text = """
    Title of Paper
    
    Author Names
    
    Abstract
    This is the abstract of the paper. It contains a summary of the research.
    
    Introduction
    This is the introduction section with background information.
    
    Methods
    This section describes the methodology used.
    
    Results
    Here are the experimental results.
    
    Conclusion
    Final thoughts and conclusions.
    
    References
    [1] First reference
    [2] Second reference
    """
    
    processor = TextProcessor(text)
    sections = processor.extract_sections()
    
    print("Test 1: Basic Headers")
    print("-" * 50)
    for section_name, content in sections.items():
        if content:
            print(f"{section_name.upper()}: ✓ Found ({len(content.split())} words)")
        else:
            print(f"{section_name.upper()}: ✗ Not found")
    print()
    
    assert sections['abstract'] is not None, "Abstract should be found"
    assert sections['introduction'] is not None, "Introduction should be found"
    assert sections['methodology'] is not None, "Methods should be found"
    assert sections['results'] is not None, "Results should be found"
    assert sections['conclusion'] is not None, "Conclusion should be found"
    assert sections['references'] is not None, "References should be found"
    print("✓ All basic sections detected\n")

def test_numbered_sections():
    """Test numbered section headers"""
    text = """
    Title of Paper
    
    Abstract
    This is the abstract.
    
    1. Introduction
    This is the introduction section.
    
    2. Materials and Methods
    This section describes the experimental setup.
    
    3. Results and Discussion
    Here are the results with discussion.
    
    4. Conclusions
    Final conclusions of the study.
    
    5. References
    [1] Reference one
    """
    
    processor = TextProcessor(text)
    sections = processor.extract_sections()
    
    print("Test 2: Numbered Sections")
    print("-" * 50)
    for section_name, content in sections.items():
        if content:
            print(f"{section_name.upper()}: ✓ Found ({len(content.split())} words)")
        else:
            print(f"{section_name.upper()}: ✗ Not found")
    print()
    
    assert sections['introduction'] is not None, "Numbered introduction should be found"
    assert sections['methodology'] is not None, "Materials and Methods should be found"
    assert sections['results'] is not None, "Results and Discussion should be found"
    assert sections['conclusion'] is not None, "Conclusions should be found"
    print("✓ All numbered sections detected\n")

def test_roman_numerals():
    """Test Roman numeral section headers"""
    text = """
    A Research Paper
    
    Abstract
    Summary of the paper.
    
    I. Introduction
    Background and motivation.
    
    II. Methodology
    Research methods employed.
    
    III. Results
    Experimental findings.
    
    IV. Discussion
    Analysis of results.
    
    V. References
    Bibliography
    """
    
    processor = TextProcessor(text)
    sections = processor.extract_sections()
    
    print("Test 3: Roman Numeral Sections")
    print("-" * 50)
    for section_name, content in sections.items():
        if content:
            print(f"{section_name.upper()}: ✓ Found ({len(content.split())} words)")
        else:
            print(f"{section_name.upper()}: ✗ Not found")
    print()
    
    assert sections['introduction'] is not None, "Roman numeral introduction should be found"
    assert sections['methodology'] is not None, "Roman numeral methodology should be found"
    print("✓ Roman numeral sections detected\n")

def test_all_caps_headers():
    """Test ALL CAPS section headers"""
    text = """
    TITLE OF RESEARCH
    
    ABSTRACT
    This paper presents a novel approach to machine learning.
    
    INTRODUCTION
    Machine learning has become increasingly important.
    
    EXPERIMENTAL METHODS
    We used the following experimental setup.
    
    RESULTS
    The experiments showed significant improvements.
    
    CONCLUSIONS
    We conclude that our method is effective.
    
    REFERENCES
    List of citations
    """
    
    processor = TextProcessor(text)
    sections = processor.extract_sections()
    
    print("Test 4: ALL CAPS Headers")
    print("-" * 50)
    for section_name, content in sections.items():
        if content:
            print(f"{section_name.upper()}: ✓ Found ({len(content.split())} words)")
        else:
            print(f"{section_name.upper()}: ✗ Not found")
    print()
    
    assert sections['abstract'] is not None, "ALL CAPS abstract should be found"
    assert sections['introduction'] is not None, "ALL CAPS introduction should be found"
    assert sections['methodology'] is not None, "Experimental methods should be found"
    print("✓ ALL CAPS sections detected\n")

def test_heuristic_abstract():
    """Test heuristic abstract extraction when no header present"""
    text = """
    Novel Approach to Deep Learning
    
    John Doe, Jane Smith
    University of Example
    
    This paper presents a comprehensive study of deep learning architectures
    for image classification. We propose a new method that improves accuracy
    by 15% over existing approaches. Our experiments on benchmark datasets
    demonstrate the effectiveness of the proposed technique.
    
    
    1. Introduction
    
    Deep learning has revolutionized computer vision in recent years.
    """
    
    processor = TextProcessor(text)
    sections = processor.extract_sections()
    
    print("Test 5: Heuristic Abstract Extraction")
    print("-" * 50)
    if sections['abstract']:
        print(f"ABSTRACT: ✓ Found ({len(sections['abstract'].split())} words)")
        print(f"Content preview: {sections['abstract'][:100]}...")
    else:
        print("ABSTRACT: ✗ Not found")
    print()
    
    assert sections['abstract'] is not None, "Heuristic abstract should be extracted"
    assert len(sections['abstract'].split()) >= 20, "Abstract should have reasonable length"
    print("✓ Heuristic abstract extraction works\n")

def test_section_variations():
    """Test various section name variations"""
    text = """
    Research Title
    
    Summary
    Brief overview of the paper.
    
    Background
    Historical context and related work.
    
    Experimental Design
    Description of experiments.
    
    Findings
    Key discoveries from experiments.
    
    Concluding Remarks
    Final thoughts and future work.
    
    Bibliography
    Cited works
    """
    
    processor = TextProcessor(text)
    sections = processor.extract_sections()
    
    print("Test 6: Section Variations")
    print("-" * 50)
    for section_name, content in sections.items():
        if content:
            print(f"{section_name.upper()}: ✓ Found ({len(content.split())} words)")
        else:
            print(f"{section_name.upper()}: ✗ Not found")
    print()
    
    assert sections['abstract'] is not None, "Summary should map to abstract"
    assert sections['introduction'] is not None, "Background should map to introduction"
    assert sections['methodology'] is not None, "Experimental Design should map to methodology"
    assert sections['results'] is not None, "Findings should map to results"
    assert sections['conclusion'] is not None, "Concluding Remarks should map to conclusion"
    assert sections['references'] is not None, "Bibliography should map to references"
    print("✓ All section variations detected\n")

def run_all_tests():
    """Run all test cases"""
    print("=" * 60)
    print("SECTION DETECTION IMPROVEMENT TESTS")
    print("=" * 60)
    print()
    
    tests = [
        test_basic_headers,
        test_numbered_sections,
        test_roman_numerals,
        test_all_caps_headers,
        test_heuristic_abstract,
        test_section_variations
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"✗ FAILED: {test_func.__name__}")
            print(f"  Error: {e}\n")
            failed += 1
        except Exception as e:
            print(f"✗ ERROR in {test_func.__name__}: {e}\n")
            failed += 1
    
    print("=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
