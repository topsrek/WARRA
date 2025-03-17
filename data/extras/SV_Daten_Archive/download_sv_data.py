import os
import requests
from datetime import datetime
import re
from bs4 import BeautifulSoup
import time
from pathlib import Path

# Configuration for all categories
CATEGORIES = {
    "Beschaeftigte_Oesterreich": {
        "base_url": "https://www.sozialversicherung.at/cdscontent/?contentid=10007.894921&portal=svportal",
        "description": "Beschäftigte in Österreich",
        "link_class": "esvlink_excel"
    },
    "Geringfuegig_Beschaeftigte": {
        "base_url": "https://www.sozialversicherung.at/cdscontent/?contentid=10007.894922&portal=svportal",
        "description": "Geringfügig Beschäftigte / Geringfügig freie Dienstverträge in Österreich",
        "link_class": "esvlink_excel"
    },
    "Monatsberichte": {
        "base_url": "https://www.sozialversicherung.at/cdscontent/?contentid=10007.894919&portal=svportal",
        "description": "Monatsberichte der österreichischen Sozialversicherung",
        "link_class": "esvlink_excel"
    },
    "Jahresergebnisse": {
        "base_url": "https://www.sozialversicherung.at/cdscontent/?contentid=10007.894876&portal=svportal",
        "description": "Versicherte, Pensionen, Renten - Jahresergebnisse",
        "link_class": "esvlink_excel"
    },
    "Sozialversicherung_Zahlen": {
        "base_url": "https://www.sozialversicherung.at/cdscontent/?contentid=10007.892165&portal=svportal",
        "description": "Die österreichische Sozialversicherung in Zahlen",
        "link_class": "esvlink_pdf"
    },
    "Statistisches_Handbuch": {
        "base_url": "https://www.sozialversicherung.at/cdscontent/?contentid=10007.888557&portal=svportal",
        "description": "Statistisches Handbuch der österreichischen Sozialversicherung",
        "link_class": ["esvlink_pdf", "esvlink_zip"]
    }
}

def create_directory_structure():
    """Create the necessary directory structure for storing the data."""
    base_dir = Path(".")
    for category in CATEGORIES.keys():
        category_dir = base_dir / category
        category_dir.mkdir(exist_ok=True)
    return base_dir

def download_file(url, filename, category_dir):
    """Download a file from the given URL and save it to the specified directory."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        filepath = category_dir / filename
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return True
    except Exception as e:
        print(f"Error downloading {filename}: {str(e)}")
        return False

def extract_file_info(link_element, category):
    """Extract file information from a link element."""
    url = link_element.get('href', '')
    if not url.startswith('http'):
        url = 'https://www.sozialversicherung.at' + url
    
    # Extract filename and size from the link text
    link_text = link_element.get_text(strip=True)
    size_match = re.search(r'\((.*?)\)', link_text)
    size = size_match.group(1) if size_match else "Unknown size"
    
    # Extract filename from the data-ppdlvalue attribute or generate from link text
    filename = link_element.get('data-ppdlvalue', '').split('(')[0].strip()
    if not filename:
        # Generate filename from link text
        filename = link_text.split('(')[0].strip()
        filename = re.sub(r'[^a-zA-Z0-9]', '_', filename).lower()
        if category == "Sozialversicherung_Zahlen":
            filename = f"{filename}.pdf"
        elif category == "Statistisches_Handbuch":
            if "esvlink_zip" in link_element.get('class', []):
                filename = f"{filename}.zip"
            else:
                filename = f"{filename}.pdf"
        else:
            filename = f"{filename}.xlsx"
    
    # Extract year and month from filename or link text
    year_match = re.search(r'20\d{2}', filename)
    year = year_match.group(0) if year_match else "Unknown"
    
    month_match = re.search(r'(Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)', link_text)
    month_map = {
        "Januar": 1, "Februar": 2, "März": 3, "April": 4, "Mai": 5, "Juni": 6,
        "Juli": 7, "August": 8, "September": 9, "Oktober": 10, "November": 11, "Dezember": 12
    }
    month = month_map.get(month_match.group(1), 0) if month_match else 0
    
    return {
        "url": url,
        "filename": filename,
        "size": size,
        "year": year,
        "month": month,
        "category": category
    }

def get_last_update_date(soup):
    """Extract the last update date from the webpage."""
    date_div = soup.find('div', class_='date')
    if date_div:
        date_text = date_div.get_text(strip=True)
        # Extract date from text like "Zuletzt aktualisiert am 24. Oktober 2024"
        date_match = re.search(r'Zuletzt aktualisiert am (\d{1,2}\. [A-Za-zäöüß]+ \d{4})', date_text)
        if date_match:
            return date_match.group(1)
    return None

def scrape_file_links(category):
    """Scrape file links from the webpage for a specific category."""
    try:
        response = requests.get(CATEGORIES[category]["base_url"])
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all file links based on category
        if category == "Statistisches_Handbuch":
            # For Handbuch, we need both PDF and ZIP files
            file_links = []
            for link_class in CATEGORIES[category]["link_class"]:
                file_links.extend(soup.find_all('a', class_=link_class))
        else:
            # For other categories, use the single link class
            file_links = soup.find_all('a', class_=CATEGORIES[category]["link_class"])
        
        files_info = []
        for link in file_links:
            file_info = extract_file_info(link, category)
            files_info.append(file_info)
        
        # Get last update date
        last_update = get_last_update_date(soup)
        
        return files_info, last_update
    except Exception as e:
        print(f"Error scraping webpage for {category}: {str(e)}")
        return [], None

def create_markdown_documentation(base_dir, all_files_info, last_updates):
    """Create a markdown file documenting all downloaded files."""
    md_content = """# Austrian Social Insurance Data Archive

This directory contains various data files downloaded from the Austrian Social Insurance website.

## Categories

"""
    
    # Add category sections
    for category, info in CATEGORIES.items():
        category_files = [f for f in all_files_info if f['category'] == category]
        last_update = last_updates.get(category)
        md_content += f"""### [{info['description']}](./{category})
Data source: [{info['description']}]({info['base_url']})
"""
        if last_update:
            md_content += f"Last updated on website: {last_update}\n\n"
        else:
            md_content += "\n"
        
        md_content += "#### Files by Year\n\n"
        
        # Organize files by year
        files_by_year = {}
        for file_info in category_files:
            year = file_info['year']
            if year not in files_by_year:
                files_by_year[year] = []
            files_by_year[year].append(file_info)
        
        # Add files for each year
        for year in sorted(files_by_year.keys(), reverse=True):
            md_content += f"##### {year}\n"
            for file_info in sorted(files_by_year[year], key=lambda x: x['month']):
                md_content += f"- {file_info['filename']} ({file_info['size']})\n"
            md_content += "\n"
    
    # Add download information
    md_content += f"""## Download Information
- Download date: {datetime.now().strftime('%Y-%m-%d')}
- Total files: {len(all_files_info)}
- Categories: {len(CATEGORIES)}

## Directory Structure
```
SV_Daten_Archive/
├── Beschaeftigte_Oesterreich/     # Employment data
├── Geringfuegig_Beschaeftigte/    # Marginally employed workers
├── Monatsberichte/                # Monthly reports
├── Jahresergebnisse/              # Annual results
├── Sozialversicherung_Zahlen/     # Key figures
├── Statistisches_Handbuch/        # Statistical handbook
└── README.md                      # This file
```

## Usage
To download all data:
1. Run the download script: `python download_sv_data.py`
2. Check the README.md file for documentation
"""
    
    # Write the markdown file
    with open(base_dir / "README.md", "w", encoding="utf-8") as f:
        f.write(md_content)

def main():
    # Create directory structure
    base_dir = create_directory_structure()
    all_files_info = []
    last_updates = {}
    
    # Process each category
    for category in CATEGORIES.keys():
        print(f"\nProcessing category: {category}")
        
        # Scrape file links
        print(f"Scraping file links from webpage...")
        files_info, last_update = scrape_file_links(category)
        
        if not files_info:
            print(f"No files found for {category}. Skipping...")
            continue
        
        if last_update:
            last_updates[category] = last_update
        
        # Download files
        category_dir = base_dir / category
        print(f"\nStarting downloads of {len(files_info)} files for {category}...")
        for file_info in files_info:
            print(f"Downloading {file_info['filename']}...")
            success = download_file(file_info['url'], file_info['filename'], category_dir)
            if success:
                print(f"Successfully downloaded {file_info['filename']}")
            else:
                print(f"Failed to download {file_info['filename']}")
            time.sleep(1)  # Add a small delay between downloads
        
        all_files_info.extend(files_info)
    
    # Create markdown documentation
    create_markdown_documentation(base_dir, all_files_info, last_updates)
    print("\nDownload process completed. Check the README.md file for documentation.")

if __name__ == "__main__":
    main() 