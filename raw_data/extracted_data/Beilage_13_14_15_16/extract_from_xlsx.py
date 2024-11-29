from dataclasses import dataclass
from typing import List, Dict, Any, Tuple, Optional
import pandas as pd
from bs4 import BeautifulSoup
import re
from datetime import datetime
from pathlib import Path
import json


@dataclass
class TableData:
    title: str
    headers: List[str]
    data: List[List[str]]
    start_row: int
    end_row: int


def extract_table_data(
    rows: List[Any], start_marker: str, end_marker: str
) -> Optional[TableData]:
    """Extract a specific table based on markers"""
    table_data = []
    headers = []
    start_row = -1
    end_row = -1

    for i, row in enumerate(rows):
        cells = row.find_all(["td", "th"])
        if not cells:
            continue

        text = " ".join(cell.get_text(strip=True) for cell in cells)

        if start_marker in text and not headers:
            start_row = i
            continue

        if start_row >= 0:
            if not headers and any(cell.get_text(strip=True) for cell in cells):
                headers = [cell.get_text(strip=True) for cell in cells]
                continue

            if headers:
                values = [cell.get_text(strip=True) for cell in cells]
                if end_marker and end_marker in text:
                    end_row = i
                    break
                if any(values):
                    table_data.append(values)

    if start_row >= 0 and headers:
        return TableData(
            title=start_marker,
            headers=headers,
            data=table_data,
            start_row=start_row,
            end_row=end_row if end_row >= 0 else start_row + len(table_data),
        )
    return None


def process_sheet1_refunds(html_content: str) -> Tuple[Dict[str, pd.DataFrame], Dict[str, Any]]:
    """Process refund amounts by federal state"""
    soup = BeautifulSoup(html_content, 'html.parser')
    tables = {}
    
    # Extract yearly data tables (2021, 2022, 2023)
    years = ['2021', '2022', '2023']
    for year in years:
        rows = soup.find_all('tr')
        year_data = []
        headers = None
        
        for row in rows:
            cells = row.find_all(['td'])
            if not cells:
                continue
                
            text = [cell.get_text(strip=True) for cell in cells]
            
            # Skip empty rows
            if not any(text):
                continue
                
            # Find the year marker
            if len(text) > 0 and text[0] == year:
                continue
                
            # Get headers after year marker
            if len(text) > 0 and text[0] == 'Bundesland':
                # Only take non-empty headers
                headers = [col for col in text if col]
                continue
                
            # Get data rows
            if headers and text[0] and text[0] != 'Summe':
                # Only take non-empty values up to the number of headers
                values = [val for val in text[:len(headers)] if val]
                if len(values) == len(headers):
                    year_data.append(values)
        
        if headers and year_data:
            df = pd.DataFrame(year_data, columns=headers)
            tables[f"refunds_{year}"] = df
    
    metadata = {
        "sheet": "Beilage_13",
        "tables": list(tables.keys()),
        "extraction_date": datetime.now().isoformat()
    }
    
    return tables, metadata


def process_sheet2_applications(
    html_content: str,
) -> Tuple[Dict[str, pd.DataFrame], Dict[str, Any]]:
    """Process application statistics"""
    soup = BeautifulSoup(html_content, "html.parser")
    tables = {}

    # Extract monthly applications
    monthly = extract_table_data(soup.find_all("tr"), "Monat", "Gesamt")
    if monthly:
        tables["monthly"] = pd.DataFrame(monthly.data, columns=monthly.headers)

    metadata = {
        "sheet": "Beilage_14",
        "tables": list(tables.keys()),
        "extraction_date": datetime.now().isoformat(),
    }

    return tables, metadata


def process_sheet3_therapy(
    html_content: str,
) -> Tuple[Dict[str, pd.DataFrame], Dict[str, Any]]:
    """Process therapy statistics and costs"""
    soup = BeautifulSoup(html_content, "html.parser")
    tables = {}

    # Extract application counts
    apps = extract_table_data(
        soup.find_all("tr"),
        "Gesamtzahl der Anträge",
        "Durchschnittliche Bearbeitungszeit",
    )
    if apps:
        tables["applications"] = pd.DataFrame(apps.data, columns=apps.headers)

    # Extract therapy costs
    costs = extract_table_data(
        soup.find_all("tr"), "Ausgaben (€)", "Wahl-Physiotherapeuten"
    )
    if costs:
        tables["therapy_costs"] = pd.DataFrame(costs.data, columns=costs.headers)

    metadata = {
        "sheet": "Beilage_15",
        "tables": list(tables.keys()),
        "extraction_date": datetime.now().isoformat(),
    }

    return tables, metadata


def process_sheet4_statistics(
    html_content: str,
) -> Tuple[Dict[str, pd.DataFrame], Dict[str, Any]]:
    """Process BVAEB statistics"""
    soup = BeautifulSoup(html_content, "html.parser")
    tables = {}

    # Extract monthly submissions 2023
    submissions_2023 = extract_table_data(soup.find_all("tr"), "Monat", "Jun.24")
    if submissions_2023:
        tables["submissions_2023"] = pd.DataFrame(
            submissions_2023.data, columns=submissions_2023.headers
        )

    # Extract historical data
    historical = extract_table_data(
        soup.find_all("tr")[submissions_2023.end_row :] if submissions_2023 else [],
        "Jän.21",
        "Jun.24",
    )
    if historical:
        tables["historical"] = pd.DataFrame(historical.data, columns=historical.headers)

    metadata = {
        "sheet": "Beilage_16",
        "tables": list(tables.keys()),
        "extraction_date": datetime.now().isoformat(),
    }

    return tables, metadata


def save_tables(
    tables: Dict[str, pd.DataFrame], metadata: Dict[str, Any], output_dir: Path
):
    """Save extracted tables and metadata"""
    sheet_dir = output_dir / metadata["sheet"]
    sheet_dir.mkdir(parents=True, exist_ok=True)

    for name, df in tables.items():
        df.to_csv(sheet_dir / f"{name}.csv", index=False)

    with open(sheet_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)


def main():
    input_dir = Path(
        "../Beilage_13_14_15_16_manually_extracted.files"
    )
    output_dir = Path("processed_data")

    processors = {
        "sheet001.htm": process_sheet1_refunds,
        "sheet002.htm": process_sheet2_applications,
        "sheet003.htm": process_sheet3_therapy,
        "sheet004.htm": process_sheet4_statistics,
    }

    for sheet_file, processor in processors.items():
        with open(input_dir / sheet_file, "r", encoding="windows-1252") as f:
            content = f.read()

        tables, metadata = processor(content)
        save_tables(tables, metadata, output_dir)


if __name__ == "__main__":
    main()
