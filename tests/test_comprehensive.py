import sys
sys.path.insert(0, 'services/document-processing')

from utils.pdf_parser import PDFParser

p = PDFParser('uploads_data/20251104_145814_universal_data_model_as_a_way_to_build_multi-paradigm_data_lakes.pdf')

print("="*60)
print("METADATA EXTRACTION")
print("="*60)
meta = p.extract_metadata()
print('Title:', meta.get('title'))
print('Authors:', meta.get('authors'))
print('Pages:', meta.get('page_count'))
print()

print("="*60)
print("TABLE EXTRACTION")
print("="*60)
tables = p.extract_tables()
print(f"Found {len(tables)} tables")
for table in tables[:3]:  # Show first 3 tables
    print(f"\nTable on page {table['page']}, {table['row_count']}x{table['col_count']}")
    if table['caption']:
        print(f"Caption: {table['caption']}")
    if table['data'] and len(table['data']) > 0:
        print(f"First row: {table['data'][0][:3]}...")  # First 3 cells
print()

print("="*60)
print("FIGURE EXTRACTION")
print("="*60)
figures = p.extract_figures()
print(f"Found {len(figures)} figures")
for fig in figures[:5]:  # Show first 5 figures
    print(f"\nFigure on page {fig['page']}")
    if fig['caption']:
        print(f"Caption: {fig['caption']}")
    if fig['file_path']:
        print(f"Saved to: {fig['file_path']}")
    print(f"Size: {fig.get('width')}x{fig.get('height')}")
print()

print("="*60)
print("REFERENCES EXTRACTION")
print("="*60)
references = p.extract_references()
print(f"Found {len(references)} references")
for ref in references[:5]:  # Show first 5 references
    print(f"\n[{ref['index']}] {ref['text'][:100]}...")
    if ref['year']:
        print(f"   Year: {ref['year']}")
print()

print("="*60)
print("TEXT PREVIEW (Column-aware extraction)")
print("="*60)
pages = p.extract_text_by_page()
print(pages[0][:800])
