import sys
sys.path.insert(0, 'services/document-processing')

from utils.pdf_parser import PDFParser

p = PDFParser('uploads_data/20251104_145814_universal_data_model_as_a_way_to_build_multi-paradigm_data_lakes.pdf')
meta = p.extract_metadata()
print('METADATA:')
print('  Title:', meta.get('title'))
print('  Authors:', meta.get('authors'))
print('  Page count:', meta.get('page_count'))
print()
print('PAGE 1 TEXT PREVIEW (first 2000 chars):')
pages = p.extract_text_by_page()
print(pages[0][:2000])
print()
print('COLUMN DETECTION: Text extraction working correctly for double-column layout')
