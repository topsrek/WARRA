import os
import sys
import PyPDF2
import tabula
import pandas as pd
import re
import csv

# Add Java to PATH
java_path = r"C:\Program Files\Java\jdk1.8.0_431\bin"  # Update this path to match your Java installation
os.environ["PATH"] = java_path + os.pathsep + os.environ["PATH"]

def extract_data_from_pdf(pdf_path):
    # Extract all text from the PDF
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() + "\n\n"

    # Extract title (looking for a line starting with "Betreff:")
    title_match = re.search(r'Betreff:\s*(.*)', full_text)
    title = title_match.group(1) if title_match else "Title not found"

    # Extract tables
    try:
        tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)
    except Exception as e:
        print(f"Error extracting tables: {str(e)}")
        tables = []
    
    # Extract other potentially useful information
    date_match = re.search(r'(\d{2}\.\d{2}\.\d{4})', full_text)
    date = date_match.group(1) if date_match else "Date not found"
    
    document_number_match = re.search(r'(\d+/AB)', full_text)
    document_number = document_number_match.group(1) if document_number_match else "Document number not found"
    
    # Extract the name of the person answering
    answerer_match = re.search(r'Der Bundesminister:\s*(.*)', full_text)
    answerer = answerer_match.group(1) if answerer_match else "Answerer not found"

    return {
        'filename': os.path.basename(pdf_path),
        'title': title,
        'date': date,
        'document_number': document_number,
        'answerer': answerer,
        'full_text': full_text,
        'tables': tables
    }

def process_beilage(data):
    # Specific processing for Beilage files
    # Extract relevant information from tables or text
    processed_data = {
        'filename': data['filename'],
        'title': data['title'],
        'date': data['date'],
        'document_number': data['document_number'],
        'answerer': data['answerer'],
    }
    
    # Add more specific processing here
    # For example, extract specific data from tables
    if data['tables']:
        for i, table in enumerate(data['tables']):
            processed_data[f'table_{i+1}'] = table.to_json(orient='records')
    
    return processed_data

def process_anfragebeantwortung(data):
    # Specific processing for Anfragebeantwortung files
    processed_data = {
        'filename': data['filename'],
        'title': data['title'],
        'date': data['date'],
        'document_number': data['document_number'],
        'answerer': data['answerer'],
    }
    
    # Add more specific processing here
    # For example, extract specific text patterns
    question_match = re.search(r'Frage (\d+):(.*?)(?=Frage \d+:|$)', data['full_text'], re.DOTALL)
    if question_match:
        processed_data['question'] = question_match.group(2).strip()
    
    answer_match = re.search(r'Antwort:(.*?)(?=Frage \d+:|$)', data['full_text'], re.DOTALL)
    if answer_match:
        processed_data['answer'] = answer_match.group(1).strip()
    
    return processed_data

# Directory containing the PDFs
pdf_directory = 'downloaded_files'

# Create a directory for the combined CSV file
output_directory = 'extracted_data'
os.makedirs(output_directory, exist_ok=True)

# Prepare a list to store all processed data
all_data = []

# Iterate through all PDF files in the directory
for filename in os.listdir(pdf_directory):
    if filename.endswith('.pdf'):
        pdf_path = os.path.join(pdf_directory, filename)
        
        print(f"Processing: {filename}")
        
        try:
            data = extract_data_from_pdf(pdf_path)
            
            # Process data based on file type
            if 'Beilage' in filename:
                processed_data = process_beilage(data)
            elif 'Anfragebeantwortung' in filename:
                processed_data = process_anfragebeantwortung(data)
            else:
                processed_data = data  # Default processing
            
            all_data.append(processed_data)
            
            print(f"Processed: {filename}")
            print("="*50)
        
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
            print("="*50)

# Save all data to a single CSV file
csv_filename = os.path.join(output_directory, 'all_data.csv')
keys = set().union(*(d.keys() for d in all_data))

with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=keys)
    writer.writeheader()
    for data in all_data:
        writer.writerow(data)

print(f"All data saved to: {csv_filename}")
