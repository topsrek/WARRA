import csv
import io
import os
import sys

# Get the input file path from command line or use default
input_file = "data/csv/manually_extracted/BVAEB_Betraege_updated.txt"
if len(sys.argv) > 1:
    input_file = sys.argv[1]

# Generate output file path (same name but with .csv extension)
output_file = os.path.splitext(input_file)[0] + ".csv"

# Read the input data from file
with open(input_file, 'r', encoding='utf-8') as f:
    input_data = f.read()

# Split the input data into lines
lines = input_data.strip().split('\n')

# Find the indices where the sections start
rechnungsbetrage_start = 0  # We know this starts at the beginning
erstattungsbetrage_start = lines.index("Erstattungsbeträge:")

# Extract the years (column headers)
years = []
for i in range(2, 7):  # Years are in lines 2-6 of the first section
    year = lines[i].strip()
    if year == "2020 *)":
        year = "2020"  # Clean up the year with asterisk
    elif year == "2024/1-9":
        year = "2024Q1-Q3"  # Simplify the partial year
    years.append(year)

# Define the list of Bundesländer in the correct order
bundeslaender = ["Wien", "NÖ", "Bgld", "OÖ", "Stmk", "Ktn", "Sbg", "Tirol", "Vbg", "Gesamt"]

# Initialize dictionaries to store the data
rechnungsbetrage = {bl: [] for bl in bundeslaender}
erstattungsbetrage = {bl: [] for bl in bundeslaender}

# Process Rechnungsbeträge section
current_bl_index = 0
i = 7  # Start after the headers
while i < erstattungsbetrage_start and current_bl_index < len(bundeslaender):
    bundesland = lines[i].strip()
    
    # Collect the 5 values for this Bundesland
    values = []
    for j in range(1, 6):  # 5 years of data
        if i + j < len(lines):
            value = lines[i + j].strip().replace('.', '')
            values.append(value)
    
    rechnungsbetrage[bundesland] = values
    i += 6  # Move to the next Bundesland (1 label + 5 values)
    current_bl_index += 1

# Process Erstattungsbeträge section
current_bl_index = 0
i = erstattungsbetrage_start + 7  # Start after the headers
while i < len(lines) and current_bl_index < len(bundeslaender):
    bundesland = lines[i].strip()
    
    # Collect the 5 values for this Bundesland
    values = []
    for j in range(1, 6):  # 5 years of data
        if i + j < len(lines):
            value = lines[i + j].strip().replace('.', '')
            values.append(value)
    
    erstattungsbetrage[bundesland] = values
    i += 6  # Move to the next Bundesland (1 label + 5 values)
    current_bl_index += 1

# Open the output CSV file for writing
with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
    # Write the CSV header
    csvfile.write("Year,Bundesland,Rechnungsbeträge,Refundierungen\n")
    
    # Generate and write the reformatted CSV data
    for bundesland in bundeslaender:
        for idx, year in enumerate(years):
            if idx < len(rechnungsbetrage.get(bundesland, [])) and idx < len(erstattungsbetrage.get(bundesland, [])):
                csvfile.write(f"{year},{bundesland},{rechnungsbetrage[bundesland][idx]},{erstattungsbetrage[bundesland][idx]}\n")

print(f"CSV data has been reformatted and saved to {output_file}")

# Also print to console for verification
print("\nCSV Content:")
print("Year,Bundesland,Rechnungsbeträge,Refundierungen")
for bundesland in bundeslaender:
    for idx, year in enumerate(years):
        if idx < len(rechnungsbetrage.get(bundesland, [])) and idx < len(erstattungsbetrage.get(bundesland, [])):
            print(f"{year},{bundesland},{rechnungsbetrage[bundesland][idx]},{erstattungsbetrage[bundesland][idx]}") 