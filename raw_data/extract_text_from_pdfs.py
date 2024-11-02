import os
import PyPDF2

def extract_text_from_pdf(pdf_path, output_dir):
    # Extract text from the PDF
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n\n"
    
    # Get the base filename without extension
    base_filename = os.path.splitext(os.path.basename(pdf_path))[0]
    
    # Save the extracted text to a file
    txt_filename = f"{base_filename}_full_text.txt"
    txt_path = os.path.join(output_dir, txt_filename)
    with open(txt_path, 'w', encoding='utf-8') as txt_file:
        txt_file.write(text)
    print(f"Saved text to: {txt_path}")

# Directory containing the PDFs
pdf_directory = 'downloaded_files'

# Directory for saving text files
text_directory = 'extracted_data/text_files'
os.makedirs(text_directory, exist_ok=True)

# Iterate through all PDF files in the directory
for filename in os.listdir(pdf_directory):
    if filename.endswith('.pdf'):
        pdf_path = os.path.join(pdf_directory, filename)
        
        print(f"Processing: {filename}")
        
        try:
            extract_text_from_pdf(pdf_path, text_directory)
            print(f"Finished processing {filename}")
            print("="*50)
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
            print("="*50)

print("Finished extracting text from all PDFs.")
