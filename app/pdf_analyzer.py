import os
import requests
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import re

load_dotenv()
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')

def extract_pdf_text(pdf_path, start_page=None, end_page=None):
    """
    Extract text from a PDF with more robust extraction
    """
    try:
        reader = PdfReader(pdf_path)
        
        # Determine page range
        if start_page is None:
            start_page = 1
        if end_page is None:
            end_page = len(reader.pages)
        
        # Ensure page numbers are within bounds
        start_page = max(1, min(start_page, len(reader.pages)))
        end_page = max(start_page, min(end_page, len(reader.pages)))
        
        # Extract text with improved formatting
        text = ""
        for page_num in range(start_page - 1, end_page):
            page_text = reader.pages[page_num].extract_text()
            
            # Basic text cleaning
            page_text = re.sub(r'\s+', ' ', page_text)  # Remove extra whitespaces
            page_text = re.sub(r'(?<=[a-z])\n(?=[A-Z])', ' ', page_text)  # Join lines that look like mid-paragraph
            
            text += page_text + "\n\n"
        
        return text.strip()
    except Exception as e:
        print(f"Error extracting PDF text: {e}")
        return ""

def analyze_chapter(pdf_path, query, start_page=None, end_page=None):
    """
    Analyze a specific chapter or page range in a PDF
    """
    # Extract text from specified page range
    text = extract_pdf_text(pdf_path, start_page, end_page)
    
    # If no text extracted, return an error
    if not text:
        return "Could not extract text from the specified pages."
    
    try:
        # Query using OpenRouter's model
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "meta-llama/llama-3.2-90b-vision-instruct:free",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a precise book analysis assistant. Directly answer the specific query based on the chapter content."
                    },
                    {
                        "role": "user",
                        "content": f"Carefully analyze this book chapter and answer the following query precisely:\n\n{query}\n\nChapter Content:\n{text}"
                    }
                ],
                "temperature": 0.3
            }
        )
        
        result = response.json()
        return result['choices'][0]['message']['content'].strip()
    
    except Exception as e:
        return f"Error analyzing chapter: {e}"