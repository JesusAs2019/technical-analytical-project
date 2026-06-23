# GenAI Research Summarizer

## Overview

AI-powered research paper summarization tool designed for pharmaceutical and chemistry research. Leverages Large Language Models (LLMs) to extract key findings, generate teaching-friendly summaries, and accelerate literature review workflows.

## Features

- **🤖 AI-Powered Summarization**: OpenAI/Gemini API integration for intelligent text analysis
- **📚 Teaching Mode**: Generate student-friendly explanations from complex research
- **🧪 Chemistry-Aware**: Domain-specific understanding of pharma/chemistry papers
- **📄 PDF Support**: Direct PDF text extraction and processing
- **⚡ Batch Processing**: Summarize multiple papers in one go
- **💾 Export Options**: Save summaries as Markdown files

## Technologies

- Python 3.10+
- OpenAI API (gpt-3.5-turbo / gpt-4)
- PyPDF2 for PDF extraction
- python-dotenv for configuration

## Use Cases

### Before (Manual Process)

- Read 50-page paper: **2 hours**
- Extract key findings: **30 minutes**
- Write summary: **30 minutes**
- **Total: 3 hours per paper**

### After (With This Tool)

- Upload PDF: **10 seconds**
- AI processing: **30 seconds**
- Get summary: **instant**
- **Total: 1 minute per paper** ⚡

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt

### 2. Set Up API Key

Copy# Copy example environment file
cp .env.example .env

# Add your OpenAI API key to .env
OPENAI_API_KEY=your_key_here

### 3. Run Summarizer

Copypython src/summarizer.py --input data/sample_paper.txt --mode concise
Example Output
Input: 20-page chemistry paper on drug synthesis

Output (Concise Mode):

# Summary: Novel Synthesis of Aspirin Derivatives

## Key Findings
- New catalytic method reduces synthesis time by 40%
- Temperature optimization at 85°C yields 94% purity
- Cost reduction: £12/kg → £7/kg

## Methodology

- Catalysts: Pd/C in ethanol
- Reaction conditions: 85°C, 2 bar pressure

## Significance

- Scalable for industrial production
- Environmentally friendly process
Output (Teaching Mode):

# Student-Friendly Summary

## What They Did

Scientists found a faster way to make aspirin-like medicines.

## Why It Matters

- Cheaper medicine (£5 saved per kilogram!)
- Faster production (40% time savings)
- Better for the environment

## Chemistry Concepts

- Catalysis: Using Pd/C to speed up reactions
- Temperature control: 85°C is optimal
Project Structure
02-genai-research-summarizer/
├── README.md
├── requirements.txt
├── .env.example
├── src/
│   ├── llm_interface.py      # AI API wrapper
│   ├── summarizer.py         # Main summarization logic
│   └── pdf_extractor.py      # PDF text extraction
├── data/
│   ├── sample_paper.txt      # Example research paper
│   └── summaries/            # Output folder
├── tests/
│   └── test_summarizer.py
└── docs/
    └── API_SETUP.md
Supported Summarization Modes
Concise - Brief technical summary
Detailed - Comprehensive analysis with methodology
Teaching - Student-friendly explanations
Key Findings - Bullet points of main results
API Cost Estimates
Using OpenAI gpt-3.5-turbo:

Cost per summary: ~$0.002 (0.2 cents)
1000 summaries: ~$2
Very affordable for portfolio/testing!
Why This Project?
Demonstrates:

✅ AI/ML integration skills
✅ API usage and error handling
✅ Domain expertise (chemistry/pharma)
✅ Teaching background application
✅ Production-ready code design
Perfect for:

Data Engineer interviews in pharma/biotech
Showcasing modern AI skills
Differentiating from generic portfolios
Author
MSc Chemistry → Data Engineer

Combining domain expertise in pharmaceutical chemistry with modern AI/ML technologies to build practical data solutions.

License
MIT License - Free to use and modify


