"""
PDF Text Extractor - Utility for extracting text from PDF research papers
Author: MSc Chemistry → Data Engineer
"""

from pathlib import Path
from typing import Optional, Dict
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFExtractor:
    """Extract and clean text from PDF files"""
    
    def __init__(self):
        """Initialize PDF extractor"""
        try:
            from PyPDF2 import PdfReader
            self.PdfReader = PdfReader
            self.available = True
        except ImportError:
            logger.warning("PyPDF2 not installed. Install with: pip install PyPDF2")
            self.available = False
    
    def extract_text(self, pdf_path: str) -> str:
        """
        Extract raw text from PDF
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text content
        """
        if not self.available:
            raise RuntimeError("PyPDF2 not available. Install it first.")
        
        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        logger.info(f"Extracting text from: {pdf_path}")
        
        try:
            reader = self.PdfReader(pdf_path)
            
            text = ""
            page_count = len(reader.pages)
            
            for i, page in enumerate(reader.pages, 1):
                page_text = page.extract_text()
                text += page_text + "\n"
                
                if i % 10 == 0:
                    logger.info(f"Processed {i}/{page_count} pages...")
            
            logger.info(f"✅ Extracted {len(text)} characters from {page_count} pages")
            return text
            
        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            raise
    
    def extract_and_clean(self, pdf_path: str) -> str:
        """
        Extract text and apply cleaning
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Cleaned text content
        """
        raw_text = self.extract_text(pdf_path)
        cleaned_text = self.clean_text(raw_text)
        
        logger.info(f"Cleaning: {len(raw_text)} → {len(cleaned_text)} chars")
        return cleaned_text
    
    def clean_text(self, text: str) -> str:
        """
        Clean extracted text (remove artifacts, fix spacing)
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page numbers (common pattern)
        text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
        
        # Fix common PDF artifacts
        text = text.replace('ﬁ', 'fi')  # Ligature fix
        text = text.replace('ﬂ', 'fl')
        text = text.replace('–', '-')   # En dash
        text = text.replace('—', '-')   # Em dash
        
        # Remove lines with only special characters
        lines = text.split('\n')
        cleaned_lines = [
            line for line in lines 
            if len(line.strip()) > 0 and not re.match(r'^[\W_]+$', line)
        ]
        
        text = '\n'.join(cleaned_lines)
        
        return text.strip()
    
    def extract_metadata(self, pdf_path: str) -> Dict:
        """
        Extract PDF metadata
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with metadata
        """
        if not self.available:
            return {'error': 'PyPDF2 not available'}
        
        try:
            reader = self.PdfReader(pdf_path)
            metadata = reader.metadata
            
            return {
                'title': metadata.get('/Title', 'Unknown'),
                'author': metadata.get('/Author', 'Unknown'),
                'subject': metadata.get('/Subject', 'Unknown'),
                'creator': metadata.get('/Creator', 'Unknown'),
                'producer': metadata.get('/Producer', 'Unknown'),
                'pages': len(reader.pages)
            }
        except Exception as e:
            logger.error(f"Metadata extraction failed: {e}")
            return {'error': str(e)}
    
    def extract_with_metadata(self, pdf_path: str) -> Dict:
        """
        Extract both text and metadata
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with text and metadata
        """
        return {
            'text': self.extract_and_clean(pdf_path),
            'metadata': self.extract_metadata(pdf_path),
            'file_path': pdf_path
        }


def demo():
    """Demo PDF extraction"""
    print("=" * 60)
    print("PDF Extractor Demo")
    print("=" * 60)
    
    extractor = PDFExtractor()
    
    if not extractor.available:
        print("\n⚠️  PyPDF2 not installed!")
        print("Install with: pip install PyPDF2")
        print("\nThis module is optional - the summarizer works with .txt files too!")
        return
    
    # Test with sample text file (PDF would work the same way)
    sample_text = """
This is a sample text to demonstrate the cleaning functionality.

Page   123

Some text with  excessive    whitespace.

Special ligatures: ﬁle, ﬂow, café

Some special dashes: en–dash, em—dash

!!!@@@###  (line with only special chars - will be removed)

Normal text continues here.
"""
    
    print("\n" + "=" * 60)
    print("Text Cleaning Demo")
    print("=" * 60)
    
    print("\nBEFORE:")
    print(sample_text[:200])
    
    cleaned = extractor.clean_text(sample_text)
    
    print("\nAFTER:")
    print(cleaned[:200])
    
    print("\n" + "=" * 60)
    print("✅ PDF Extractor Ready!")
    print("=" * 60)
    print("\nUsage:")
    print("  extractor = PDFExtractor()")
    print("  text = extractor.extract_and_clean('paper.pdf')")
    print("  metadata = extractor.extract_metadata('paper.pdf')")


if __name__ == "__main__":
    demo()
