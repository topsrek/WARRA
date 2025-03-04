import pandas as pd
import os

# Global paths
INPUT_DIR = 'exports'
OUTPUT_DIR = '../../../data/csv'

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# File patterns
files = [
    '15a_SVS_Antraege_2023_pro_Fachrichtung.csv',
    '15b_SVS_Betraege_2023_pro_Fachrichtung.csv',
    '15c_SVS_Ausgaben_MTD_Berufe_2021_2022_2023.csv'
]

def clean_numeric_column(value):
    if isinstance(value, str):
        # Remove spaces and convert comma to point
        return value.replace(' ', '').replace(',', '.')
    return value

# Process each file
for filename in files:
    input_file = os.path.join(INPUT_DIR, filename)
    output_file = os.path.join(OUTPUT_DIR, filename)
    
    # Read the CSV file with semicolon separator and latin-1 encoding
    df = pd.read_csv(input_file, sep=';', encoding='latin-1')
    
    # Clean only numeric columns
    numeric_columns = {
        '15a_SVS_Antraege_2023_pro_Fachrichtung.csv': ['Antragsanzahl'],
        '15b_SVS_Betraege_2023_pro_Fachrichtung.csv': ['Refundierungen', 'Rechnungsbeträge'],
        '15c_SVS_Ausgaben_MTD_Berufe_2021_2022_2023.csv': ['Ausgaben']
    }
    
    for col in df.columns:
        if col in numeric_columns[filename]:
            df[col] = df[col].apply(clean_numeric_column)
    
    # Save as standard CSV with comma separator and utf-8 encoding
    df.to_csv(output_file, index=False, encoding='utf-8')
    
    print(f"Successfully converted {input_file} to {output_file}")