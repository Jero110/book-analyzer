from flask import render_template, request, jsonify, current_app
import os
from app import app
from .pdf_analyzer import analyze_chapter

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    query = data.get('query')
    start_page = data.get('start_page')
    end_page = data.get('end_page')
    
    pdf_path = "/Users/jeronimo/Downloads/Four Thousand Weeks_ Time Manag - Burkeman, Oliver.pdf"
    
    if not os.path.exists(pdf_path):
        return jsonify({'response': f"Error: PDF file not found. Please ensure the file exists at: {pdf_path}"})
    
    response = analyze_chapter(pdf_path, query, start_page, end_page)
    return jsonify({'response': response}) 