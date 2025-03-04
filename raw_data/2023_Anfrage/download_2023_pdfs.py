import json
import os
import requests

# Load the JSON data
with open('export_Gegenstand_Refundierung von Wahlarztkosten und Hilfsmitteln 2023.json', 'r') as f:
    data = json.load(f)

# Base URL for the parliament website
base_url = 'https://www.parlament.gv.at'

# Create a directory to store the downloaded files
output_dir = 'downloaded_files'
os.makedirs(output_dir, exist_ok=True)

# Function to download a file
def download_file(url, filename):
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded: {filename}")
    else:
        print(f"Failed to download: {url}")

# Iterate through the documents and download each file
for doc in data['documents']:
    for file in doc['documents']:
        file_url = base_url + file['link']
        file_name = os.path.join(output_dir, f"{doc['title'].replace(' ', '_')}.pdf")
        download_file(file_url, file_name)

print("All files have been downloaded.")
