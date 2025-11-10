"""
OCR Utility for Scanned PDFs
Detects scanned pages and applies Tesseract OCR
"""
import logging
from typing import List, Tuple, Dict, Any
from pathlib import Path
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import PyPDF2

logger = logging.getLogger(__name__)


class OCRProcessor:
    """Handle OCR for scanned PDF documents"""
    
    @staticmethod
    def is_scanned_pdf(pdf_path: str, sample_pages: int = 3) -> Tuple[bool, float]:
        """
        Detect if a PDF is scanned (image-based) vs text-based
        
        Args:
            pdf_path: Path to PDF file
            sample_pages: Number of pages to sample for detection
            
        Returns:
            Tuple of (is_scanned, confidence_score)
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                
                # Sample pages
                pages_to_check = min(sample_pages, total_pages)
                text_char_counts = []
                
                for i in range(pages_to_check):
                    page = pdf_reader.pages[i]
                    text = page.extract_text()
                    text_char_counts.append(len(text.strip()))
                
                # Calculate average text characters per page
                avg_chars = sum(text_char_counts) / len(text_char_counts) if text_char_counts else 0
                
                # Heuristic: if avg chars < 50, likely scanned
                is_scanned = avg_chars < 50
                confidence = 1.0 - min(avg_chars / 500, 1.0)  # 0-1 scale
                
                logger.info(f"Scanned PDF detection: avg_chars={avg_chars:.1f}, is_scanned={is_scanned}, confidence={confidence:.2f}")
                
                return is_scanned, confidence
                
        except Exception as e:
            logger.error(f"Error detecting scanned PDF: {e}")
            return False, 0.0
    
    @staticmethod
    def extract_text_with_ocr(
        pdf_path: str,
        dpi: int = 300,
        lang: str = 'eng',
        page_range: Tuple[int, int] = None
    ) -> Dict[str, Any]:
        """
        Extract text from PDF using OCR
        
        Args:
            pdf_path: Path to PDF file
            dpi: DPI for PDF to image conversion (higher = better quality, slower)
            lang: Tesseract language (eng, fra, deu, etc.)
            page_range: Optional tuple of (start_page, end_page) to process
            
        Returns:
            Dict with extracted text and metadata
        """
        try:
            logger.info(f"Starting OCR extraction for {pdf_path} at {dpi} DPI")
            
            # Convert PDF pages to images
            if page_range:
                first_page, last_page = page_range
                images = convert_from_path(
                    pdf_path,
                    dpi=dpi,
                    first_page=first_page,
                    last_page=last_page
                )
            else:
                images = convert_from_path(pdf_path, dpi=dpi)
            
            # Extract text from each image
            page_texts = []
            total_chars = 0
            
            for i, image in enumerate(images):
                logger.info(f"Processing page {i+1}/{len(images)} with OCR")
                
                # Apply OCR
                text = pytesseract.image_to_string(image, lang=lang)
                page_texts.append(text)
                total_chars += len(text.strip())
            
            # Combine all pages
            full_text = '\n\n'.join(page_texts)
            
            result = {
                'success': True,
                'full_text': full_text,
                'page_count': len(images),
                'total_chars': total_chars,
                'avg_chars_per_page': total_chars / len(images) if images else 0,
                'ocr_confidence': None,  # Tesseract doesn't provide overall confidence easily
            }
            
            logger.info(f"OCR completed: {len(images)} pages, {total_chars} chars")
            return result
            
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'full_text': '',
                'page_count': 0,
                'total_chars': 0
            }
    
    @staticmethod
    def extract_with_fallback(pdf_path: str, force_ocr: bool = False) -> Dict[str, Any]:
        """
        Extract text with automatic OCR fallback for scanned PDFs
        
        Args:
            pdf_path: Path to PDF file
            force_ocr: Force OCR even if text extraction works
            
        Returns:
            Dict with extracted text and metadata
        """
        # First, check if OCR is needed
        is_scanned, confidence = OCRProcessor.is_scanned_pdf(pdf_path)
        
        if force_ocr or (is_scanned and confidence > 0.7):
            logger.info(f"Applying OCR (force_ocr={force_ocr}, is_scanned={is_scanned}, confidence={confidence})")
            result = OCRProcessor.extract_text_with_ocr(pdf_path)
            result['ocr_applied'] = True
            result['scanned_confidence'] = confidence
            return result
        else:
            logger.info("PDF appears text-based, skipping OCR")
            return {
                'success': True,
                'full_text': None,  # Caller should use regular extraction
                'ocr_applied': False,
                'scanned_confidence': confidence,
                'message': 'Text-based PDF, OCR not needed'
            }
