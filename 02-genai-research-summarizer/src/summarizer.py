"""
Research Paper Summarizer - Main Pipeline
Orchestrates PDF extraction, AI summarization, and output generation
Author: MSc Chemistry → Data Engineer
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
import logging
from datetime import datetime

from llm_interface import LLMInterface

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ResearchSummarizer:
    """Main pipeline for research paper summarization"""
    
    SUPPORTED_MODES = ['concise', 'teaching', 'key_findings', 'detailed']
    
    def __init__(
        self,
        output_dir: str = "data/summaries",
        api_key: Optional[str] = None
    ):
        """
        Initialize summarizer pipeline
        
        Args:
            output_dir: Directory to save summaries
            api_key: LLM API key (optional, uses env var if not provided)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize LLM interface
        self.llm = LLMInterface(api_key=api_key)
        
        logger.info(f"Summarizer initialized. Output: {self.output_dir}")
    
    def summarize_file(
        self,
        input_path: str,
        mode: str = "concise",
        save_output: bool = True
    ) -> Dict:
        """
        Summarize a single research paper file
        
        Args:
            input_path: Path to text or PDF file
            mode: Summary mode (concise/teaching/key_findings)
            save_output: Whether to save summary to file
            
        Returns:
            Dictionary with summary results
        """
        logger.info(f"Processing: {input_path}")
        
        # Validate mode
        if mode not in self.SUPPORTED_MODES:
            logger.warning(f"Unknown mode '{mode}', using 'concise'")
            mode = 'concise'
        
        # Read input file
        try:
            text = self._read_file(input_path)
        except Exception as e:
            logger.error(f"Failed to read file: {e}")
            return {'status': 'error', 'error': str(e)}
        
        # Generate summary
        logger.info(f"Generating {mode} summary...")
        summary = self.llm.summarize_text(text, mode=mode)
        
        # Save if requested
        output_path = None
        if save_output:
            output_path = self._save_summary(
                summary, 
                input_path, 
                mode
            )
        
        # Return results
        result = {
            'status': 'success',
            'input_file': input_path,
            'mode': mode,
            'summary': summary,
            'output_file': str(output_path) if output_path else None,
            'timestamp': datetime.now().isoformat(),
            'text_length': len(text),
            'summary_length': len(summary)
        }
        
        logger.info(f"✅ Summary complete! ({len(text)} → {len(summary)} chars)")
        
        return result
    
    def batch_summarize(
        self,
        input_files: List[str],
        mode: str = "concise",
        save_output: bool = True
    ) -> List[Dict]:
        """
        Summarize multiple papers in batch
        
        Args:
            input_files: List of file paths
            mode: Summary mode
            save_output: Whether to save summaries
            
        Returns:
            List of result dictionaries
        """
        logger.info(f"Batch processing {len(input_files)} files...")
        
        results = []
        for i, file_path in enumerate(input_files, 1):
            logger.info(f"\n{'='*60}")
            logger.info(f"Paper {i}/{len(input_files)}")
            logger.info('='*60)
            
            result = self.summarize_file(file_path, mode, save_output)
            results.append(result)
        
        # Generate batch report
        successful = sum(1 for r in results if r['status'] == 'success')
        failed = len(results) - successful
        
        logger.info(f"\n{'='*60}")
        logger.info("BATCH SUMMARY")
        logger.info('='*60)
        logger.info(f"Total papers: {len(results)}")
        logger.info(f"Successful: {successful}")
        logger.info(f"Failed: {failed}")
        logger.info('='*60)
        
        return results
    
    def _read_file(self, file_path: str) -> str:
        """
        Read text from file (supports .txt and .pdf)
        
        Args:
            file_path: Path to input file
            
        Returns:
            Extracted text content
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Handle different file types
        if path.suffix.lower() == '.pdf':
            return self._extract_pdf_text(file_path)
        elif path.suffix.lower() in ['.txt', '.md']:
            return path.read_text(encoding='utf-8')
        else:
            raise ValueError(f"Unsupported file type: {path.suffix}")
    
    def _extract_pdf_text(self, pdf_path: str) -> str:
        """
        Extract text from PDF file
        
        Args:
            pdf_path: Path to PDF
            
        Returns:
            Extracted text
        """
        try:
            from PyPDF2 import PdfReader
            
            reader = PdfReader(pdf_path)
            text = ""
            
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            logger.info(f"Extracted {len(text)} chars from PDF")
            return text
            
        except ImportError:
            logger.error("PyPDF2 not installed. Install with: pip install PyPDF2")
            raise
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            raise
    
    def _save_summary(
        self,
        summary: str,
        input_path: str,
        mode: str
    ) -> Path:
        """
        Save summary to markdown file
        
        Args:
            summary: Summary text
            input_path: Original input file path
            mode: Summary mode
            
        Returns:
            Path to saved file
        """
        # Generate output filename
        input_name = Path(input_path).stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{input_name}_{mode}_{timestamp}.md"
        output_path = self.output_dir / output_filename
        
        # Add metadata header
        metadata = f"""---
source: {input_path}
mode: {mode}
generated: {datetime.now().isoformat()}
---

"""
        
        # Write file
        output_path.write_text(metadata + summary, encoding='utf-8')
        logger.info(f"💾 Saved to: {output_path}")
        
        return output_path
    
    def generate_comparison(
        self,
        input_path: str,
        modes: List[str] = ['concise', 'teaching', 'key_findings']
    ) -> Dict:
        """
        Generate summaries in multiple modes for comparison
        
        Args:
            input_path: Path to input file
            modes: List of modes to generate
            
        Returns:
            Dictionary with all summaries
        """
        logger.info(f"Generating comparison summaries for: {input_path}")
        
        results = {}
        for mode in modes:
            result = self.summarize_file(input_path, mode, save_output=True)
            results[mode] = result
        
        logger.info(f"✅ Generated {len(modes)} comparison summaries")
        return results


def main():
    """Demo usage of the summarizer"""
    
    print("=" * 60)
    print("GenAI Research Summarizer - Demo")
    print("=" * 60)
    
    # Initialize summarizer
    summarizer = ResearchSummarizer()
    
    # Check for sample data
    sample_file = Path("data/sample_paper.txt")
    
    if not sample_file.exists():
        print("\n⚠️  Sample file not found!")
        print("Creating demo sample...")
        
        sample_file.parent.mkdir(parents=True, exist_ok=True)
        sample_file.write_text("""
Novel Synthesis of Aspirin Derivatives Using Catalytic Hydrogenation

Abstract
We report a novel catalytic method for synthesizing aspirin derivatives with 
significantly improved efficiency. Using palladium on carbon (Pd/C) catalyst 
in ethanol solvent at 85°C, we achieved 94% yield compared to traditional 
methods yielding only 78%.

Introduction
Aspirin and its derivatives are among the most widely used pharmaceutical 
compounds globally. Traditional synthesis methods suffer from low yields, 
long reaction times, and environmental concerns due to excessive solvent use.

Methods
We employed a catalytic hydrogenation approach using 5% Pd/C in ethanol at 
85°C under 2 bar hydrogen pressure. Reaction progress was monitored by HPLC.

Results
- Yield: 94% (vs. 78% traditional)
- Reaction time: 2.5 hours (vs. 4.5 hours traditional)
- Cost: £8/kg (vs. £15/kg traditional)
- Solvent waste: 30% reduction

The optimized temperature of 85°C was critical; higher temperatures led to 
decomposition, while lower temperatures slowed the reaction significantly.

Discussion
This method represents a significant improvement in pharmaceutical synthesis. 
The 45% reduction in reaction time combined with improved yield makes this 
approach economically attractive for industrial scale-up.

Conclusion
We have developed a superior catalytic method for aspirin derivative synthesis 
with clear advantages in yield, cost, and environmental impact. Patent 
application UK-2024-12345 has been filed.
""", encoding='utf-8')
        print(f"✅ Created: {sample_file}")
    
    # Test all modes
    print("\n" + "=" * 60)
    print("Testing All Summary Modes")
    print("=" * 60)
    
    modes = ['concise', 'teaching', 'key_findings']
    
    for mode in modes:
        print(f"\n{'='*60}")
        print(f"MODE: {mode.upper()}")
        print('='*60)
        
        result = summarizer.summarize_file(
            str(sample_file),
            mode=mode,
            save_output=True
        )
        
        if result['status'] == 'success':
            print(result['summary'][:500] + "...")  # Show first 500 chars
            print(f"\n✅ Saved to: {result['output_file']}")
    
    print("\n" + "=" * 60)
    print("✅ Demo Complete!")
    print(f"📁 Check summaries in: {summarizer.output_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()
