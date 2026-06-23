"""
LLM Interface - Wrapper for AI API integration
Supports OpenAI, Anthropic, Google Gemini with demo mode fallback
Author: MSc Chemistry → Data Engineer
"""

import os
from typing import Dict, Optional, List
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMInterface:
    """Unified interface for Large Language Model APIs"""
    
    DEMO_RESPONSES = {
        'concise': """
# Summary: Novel Pharmaceutical Synthesis Method

## Key Findings
- New catalytic approach reduces reaction time by 45%
- Yield improvement: 78% → 94%
- Cost reduction: £15/kg → £8/kg

## Methodology
- Catalyst: Palladium on carbon (Pd/C)
- Solvent: Ethanol
- Temperature: 85°C, 2 bar pressure

## Significance
- Scalable for industrial production
- More environmentally sustainable
- Applicable to aspirin derivative synthesis
""",
        'teaching': """
# Student-Friendly Summary: Better Drug Manufacturing

## What The Scientists Did
Researchers discovered a faster and cheaper way to make important medicines.

## Why This Matters
- **Cheaper Medicine**: Saves £7 for every kilogram produced
- **Faster Process**: 45% quicker than old methods
- **Better Quality**: More pure medicine (94% vs 78%)
- **Greener**: Better for the environment

## Simple Chemistry Explanation
Think of catalysts like a helpful friend who speeds up your work:
- Old way: Slow reaction, takes many hours
- New way: Add special catalyst (Pd/C), reaction finishes much faster
- Temperature matters: 85°C is the "sweet spot" for best results

## Real-World Impact
This means pharmaceutical companies can:
1. Make medicine faster
2. Charge patients less
3. Reduce environmental waste
""",
        'key_findings': """
## Key Research Findings

### Main Results
1. **Reaction Time Reduction**: 45% faster synthesis
2. **Yield Improvement**: 78% → 94% (16% increase)
3. **Cost Efficiency**: £15/kg → £8/kg (47% reduction)
4. **Temperature Optimization**: 85°C identified as optimal
5. **Pressure Control**: 2 bar pressure maintains stability

### Technical Details
- Catalyst: 5% Pd/C in ethanol solvent
- Reaction mechanism: Hydrogenation pathway
- Scale-up tested: Lab (10g) → Pilot (1kg) successful

### Industrial Implications
- Patent application filed (UK-2024-12345)
- Estimated market impact: £50M annually
- Environmental benefit: 30% reduction in solvent waste
"""
    }
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        model: str = "gpt-3.5-turbo",
        provider: str = "openai"
    ):
        """
        Initialize LLM interface
        
        Args:
            api_key: API key (uses env var if not provided)
            model: Model name (gpt-3.5-turbo, gpt-4, etc.)
            provider: API provider (openai, anthropic, google)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model
        self.provider = provider
        self.demo_mode = self.api_key in [None, '', 'demo_mode']
        
        if self.demo_mode:
            logger.info("🎭 Running in DEMO mode (no API key)")
        else:
            logger.info(f"✅ Connected to {provider} API")
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the appropriate API client"""
        try:
            if self.provider == "openai":
                import openai
                self.client = openai.OpenAI(api_key=self.api_key)
            elif self.provider == "anthropic":
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
            elif self.provider == "google":
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.client = genai
        except ImportError as e:
            logger.error(f"Missing library for {self.provider}: {e}")
            logger.info("Install with: pip install openai (or anthropic/google-generativeai)")
            self.demo_mode = True
    
    def summarize_text(
        self, 
        text: str, 
        mode: str = "concise",
        max_tokens: int = 500
    ) -> str:
        """
        Generate summary of research text
        
        Args:
            text: Input research paper text
            mode: Summary mode (concise/teaching/key_findings)
            max_tokens: Maximum response length
            
        Returns:
            Formatted summary string
        """
        if self.demo_mode:
            logger.info(f"📋 Returning DEMO summary (mode: {mode})")
            return self.DEMO_RESPONSES.get(mode, self.DEMO_RESPONSES['concise'])
        
        # Build prompt based on mode
        prompts = {
            'concise': self._build_concise_prompt(text),
            'teaching': self._build_teaching_prompt(text),
            'key_findings': self._build_key_findings_prompt(text)
        }
        
        prompt = prompts.get(mode, prompts['concise'])
        
        try:
            return self._call_api(prompt, max_tokens)
        except Exception as e:
            logger.error(f"API call failed: {e}")
            logger.info("Falling back to DEMO mode")
            return self.DEMO_RESPONSES.get(mode, self.DEMO_RESPONSES['concise'])
    
    def _call_api(self, prompt: str, max_tokens: int) -> str:
        """Make actual API call to LLM"""
        if self.provider == "openai":
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a pharmaceutical research analyst."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            return response.choices[0].message.content
        
        elif self.provider == "anthropic":
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        
        elif self.provider == "google":
            model = self.client.GenerativeModel(self.model)
            response = model.generate_content(prompt)
            return response.text
        
        raise ValueError(f"Unsupported provider: {self.provider}")
    
    def _build_concise_prompt(self, text: str) -> str:
        """Build prompt for concise technical summary"""
        return f"""
Analyze this pharmaceutical research paper excerpt and provide a concise technical summary.

Research Text:
{text[:3000]}

Format your response as:
# Summary: [Paper Title]

## Key Findings
- [3-5 bullet points of main results]

## Methodology
- [Brief description of methods used]

## Significance
- [Why this research matters]
"""
    
    def _build_teaching_prompt(self, text: str) -> str:
        """Build prompt for student-friendly summary"""
        return f"""
Convert this pharmaceutical research into a student-friendly summary suitable for undergraduate chemistry students.

Research Text:
{text[:3000]}

Format your response as:
# Student-Friendly Summary

## What The Scientists Did
[Simple explanation in plain English]

## Why This Matters
- [Practical implications]
- [Real-world benefits]

## Simple Chemistry Explanation
[Break down complex concepts with analogies]

## Real-World Impact
[How this affects people's lives]
"""
    
    def _build_key_findings_prompt(self, text: str) -> str:
        """Build prompt for extracting key findings"""
        return f"""
Extract the key findings and technical details from this pharmaceutical research.

Research Text:
{text[:3000]}

Format as:
## Key Research Findings

### Main Results
1. [Numbered list of results]

### Technical Details
- [Specific parameters, conditions, measurements]

### Industrial Implications
- [Business and commercial impact]
"""
    
    def batch_summarize(
        self, 
        texts: List[str], 
        mode: str = "concise"
    ) -> List[str]:
        """
        Summarize multiple texts in batch
        
        Args:
            texts: List of research paper texts
            mode: Summary mode
            
        Returns:
            List of summaries
        """
        logger.info(f"Batch processing {len(texts)} papers...")
        summaries = []
        
        for i, text in enumerate(texts, 1):
            logger.info(f"Processing paper {i}/{len(texts)}")
            summary = self.summarize_text(text, mode)
            summaries.append(summary)
        
        return summaries


# Demo usage
if __name__ == "__main__":
    print("=" * 60)
    print("GenAI Research Summarizer - LLM Interface Demo")
    print("=" * 60)
    
    # Initialize (will auto-detect demo mode)
    llm = LLMInterface()
    
    # Test sample text
    sample_text = """
    Novel Synthesis of Aspirin Derivatives Using Catalytic Hydrogenation
    
    Abstract: We report a novel catalytic method for synthesizing aspirin 
    derivatives with significantly improved efficiency. Using palladium on 
    carbon (Pd/C) catalyst in ethanol solvent at 85°C, we achieved 94% yield 
    compared to traditional methods yielding only 78%. The reaction time was 
    reduced by 45%, and production costs decreased from £15/kg to £8/kg.
    
    This method is scalable and environmentally friendly, reducing solvent 
    waste by 30%. Industrial applications are promising.
    """
    
    # Test all modes
    modes = ['concise', 'teaching', 'key_findings']
    
    for mode in modes:
        print(f"\n{'='*60}")
        print(f"MODE: {mode.upper()}")
        print('='*60)
        summary = llm.summarize_text(sample_text, mode=mode)
        print(summary)
    
    print("\n" + "="*60)
    print("✅ Demo Complete!")
    print("="*60)
