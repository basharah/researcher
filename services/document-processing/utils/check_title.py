#!/usr/bin/env python3
import sys
from pathlib import Path
from pdf_parser import PDFParser


def main():
    if len(sys.argv) < 2:
        print("Usage: python utils/check_title.py /path/to/file.pdf")
        sys.exit(1)
    pdf_path = Path(sys.argv[1])
    if not pdf_path.exists():
        print(f"File not found: {pdf_path}")
        sys.exit(2)

    parser = PDFParser(str(pdf_path))
    meta = parser.extract_metadata()
    print("Page count:", meta.get("page_count"))
    print("Authors:", ", ".join(meta.get("authors") or []))
    print("Extracted title:", meta.get("title"))


if __name__ == "__main__":
    main()
