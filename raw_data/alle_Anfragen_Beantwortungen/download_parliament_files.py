import json
import os
import requests
from datetime import datetime
import glob
import re

# Base URL for the parliament website
base_url = "https://www.parlament.gv.at"

# Create directories to store the downloaded files
antwort_dir = "Beantwortungen"
anfrage_dir = "Anfragen"
os.makedirs(os.path.join(antwort_dir, "pdfs"), exist_ok=True)
os.makedirs(os.path.join(anfrage_dir, "pdfs"), exist_ok=True)

def download_file(url, filename):
    """Download a file from the given URL and save it to the specified filename."""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"Downloaded: {filename}")
            return True
        else:
            print(f"Failed to download: {url} (Status code: {response.status_code})")
            return False
    except Exception as e:
        print(f"Error downloading {url}: {str(e)}")
        return False

def create_safe_filename(title):
    """Create a safe filename from the given title."""
    # Remove special characters and replace spaces with underscores
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
    return safe_title.replace(' ', '_')

def process_json_file(json_path):
    """Process a single JSON file and download its associated PDFs and HTMLs."""
    try:
        with open(json_path, "r", encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading JSON file {json_path}: {str(e)}")
        return

    # Get basic information
    inr = data.get('inr')
    update_date = data.get('einlangen', '').split('T')[0]
    citation = data.get('zitation', '').replace('/', '')
    
    if not inr or not update_date:
        print(f"Missing required data in {json_path}")
        return

    # Determine if this is an answer or question based on the directory structure
    is_answer = "Beantwortungen" in json_path
    base_dir = antwort_dir if is_answer else anfrage_dir
    pdf_dir = os.path.join(base_dir, "pdfs")
    html_dir = os.path.join(base_dir, "htmls")
    os.makedirs(html_dir, exist_ok=True)

    # Get reference information for answers and questions
    reference_citation = ""
    answer_citation = ""
    
    if "reference" in data:
        for ref in data["reference"]:
            if ref.get("art") == "BA":  # BA indicates it's answering a question
                reference_citation = ref.get("zitation", "").replace('/', '')
            elif ref.get("art") == "AB":  # AB indicates it's an answer to this question
                answer_citation = ref.get("zitation", "").replace('/', '')

    # If no answer citation found in references, try to find it in stages
    if not is_answer and not answer_citation and "stages" in data:
        for stage in data["stages"]:
            text = stage.get("text", "")
            # Look for pattern like "14952/AB" in the text
            match = re.search(r'(\d+)/AB', text)
            if match:
                answer_citation = match.group(1)
                break

    # Create folder name with citations
    if is_answer and reference_citation:
        inquiry_dir = os.path.join(pdf_dir, f"{update_date}_INR_{inr}_beantwortet_{reference_citation}")
        inquiry_html_dir = os.path.join(html_dir, f"{update_date}_INR_{inr}_beantwortet_{reference_citation}")
    elif not is_answer and answer_citation:
        inquiry_dir = os.path.join(pdf_dir, f"{update_date}_INR_{inr}_beantwortet_mit_{answer_citation}")
        inquiry_html_dir = os.path.join(html_dir, f"{update_date}_INR_{inr}_beantwortet_mit_{answer_citation}")
    else:
        inquiry_dir = os.path.join(pdf_dir, f"{update_date}_INR_{inr}_{citation}")
        inquiry_html_dir = os.path.join(html_dir, f"{update_date}_INR_{inr}_{citation}")
    
    os.makedirs(inquiry_dir, exist_ok=True)
    os.makedirs(inquiry_html_dir, exist_ok=True)

    # Download PDFs and HTMLs
    for doc in data.get("documents", []):
        for file in doc.get("documents", []):
            file_url = base_url + file["link"]
            safe_title = create_safe_filename(doc['title'])
            
            # Download PDF
            if file["type"] == "PDF":
                file_name = os.path.join(inquiry_dir, f"{safe_title}.pdf")
                download_file(file_url, file_name)
            # Download HTML
            elif file["type"] == "HTML":
                file_name = os.path.join(inquiry_html_dir, f"{safe_title}.html")
                download_file(file_url, file_name)


def main(directory):
    # Find all JSON files in the parliament_json_exports directory
    json_files = glob.glob(os.path.join(directory, "parliament_json_exports", "*.json"))
    
    if not json_files:
        print(f"No JSON files found in {directory}/parliament_json_exports")
        return

    print(f"Found {len(json_files)} JSON files to process in {directory}")
    
    for json_file in json_files:
        print(f"\nProcessing: {json_file}")
        process_json_file(json_file)

    print(f"\nAll files have been downloaded for {directory}")

if __name__ == "__main__":
    main(antwort_dir)
    main(anfrage_dir)
