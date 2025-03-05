import pandas as pd
import re

def clean_number(value):
    # Remove € symbol, spaces, and replace comma with dot
    return float(value.replace('€', '').replace(' ', '').replace(',', '.'))

def process_table(text, start_marker, end_marker=None):
    # Extract the table between markers
    start_idx = text.find(start_marker)
    if start_idx == -1:
        print(f"Warning: Could not find start marker '{start_marker}'")
        return None
    
    # If no end marker provided, use the next start marker or end of file
    if end_marker:
        end_idx = text.find(end_marker, start_idx)
    else:
        # Find the next occurrence of any of the table titles
        next_markers = [
            text.find('Beträge der eingereichten Honorarnoten', start_idx + len(start_marker)),
            text.find('Beträge der geleisteten Kostenerstattung', start_idx + len(start_marker))
        ]
        # Filter out -1 (not found) and get the minimum positive index
        valid_indices = [idx for idx in next_markers if idx != -1]
        end_idx = min(valid_indices) if valid_indices else len(text)
    
    if end_idx == -1:
        end_idx = len(text)
    
    table_text = text[start_idx:end_idx]
    
    # Split into lines and clean
    lines = [line.strip() for line in table_text.split('\n') if line.strip()]
    
    if len(lines) < 2:
        print(f"Warning: Not enough lines found in table starting with '{start_marker}'")
        return None
    
    # Skip the title line and get the header line
    header = lines[1]
    years = []
    for year in header.split('\t')[1:]:
        if 'Jän.- Sep.' in year:
            years.append('2024Q1-Q3')
        else:
            years.append(year)
    
    # Process data rows (skip the title and header lines)
    data = []
    for line in lines[2:]:
        parts = line.split('\t')
        if len(parts) < 2:  # Skip empty lines
            continue
        
        # Handle special cases for Bundesländer codes
        code = parts[0]
        if code == 'Gesamt':
            lst = 'Gesamt'
        elif code == 'NÖ':
            lst = 'ÖGK-N'
        elif code == 'OÖ':
            lst = 'ÖGK-O'
        else:
            lst = f"ÖGK-{code}"
            
        try:
            values = [clean_number(val) for val in parts[1:]]
            for year, value in zip(years, values):
                data.append({
                    'Year': year,
                    'LST': lst,
                    'Value': value
                })
        except ValueError as e:
            print(f"Warning: Could not process line: {line}")
            print(f"Error: {e}")
            continue
    
    return pd.DataFrame(data)

# Read the input file
with open('../OEKG_Betraege_updated2025_ugly_from_excel.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# Process both tables
rechnungsbetraege_df = process_table(content, 'Beträge der eingereichten Honorarnoten')
refundierungen_df = process_table(content, 'Beträge der geleisteten Kostenerstattung')

if rechnungsbetraege_df is None or refundierungen_df is None:
    print("Error: Failed to process one or both tables")
    exit(1)

# Merge the dataframes
merged_df = pd.merge(
    rechnungsbetraege_df,
    refundierungen_df,
    on=['Year', 'LST'],
    suffixes=('_rechnung', '_refund')
)

# Rename columns to match target format
merged_df = merged_df.rename(columns={
    'Value_rechnung': 'Rechnungsbeträge',
    'Value_refund': 'Refundierungen'
})

# Sort by Year (descending) and LST
merged_df = merged_df.sort_values(['Year', 'LST'], ascending=[False, True])

# Save to CSV
merged_df.to_csv('../OEGK_Betraege_updated2025.csv', index=False)
print("Successfully created OEGK_Betraege_updated2025.csv")
