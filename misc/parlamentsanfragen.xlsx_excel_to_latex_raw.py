import pandas as pd
import os
import numpy as np
from datetime import datetime

def escape_latex(text):
    """Escape special LaTeX characters."""
    if not isinstance(text, str):
        return str(text)
    if pd.isna(text):
        return ''
    
    chars = {
        '&': '\\&',
        '%': '\\%',
        '$': '\\$',
        '#': '\\#',
        '_': '\\_',
        '{': '\\{',
        '}': '\\}',
        '~': '\\textasciitilde{}',
        '^': '\\textasciicircum{}',
        '\\': '\\textbackslash{}',
    }
    for char, replacement in chars.items():
        text = text.replace(char, replacement)
    return text

def create_hyperlink(url):
    """Create a LaTeX hyperlink."""
    if not isinstance(url, str):
        return str(url)
    if url.startswith('http'):
        # Shorten the displayed URL to make it more compact
        display_url = url.split('/')[-1]
        return f'\\href{{{url}}}{{{display_url}}}'
    return url

def format_date(date_str):
    """Format date to YYYY-MM-DD."""
    if pd.isna(date_str):
        return ''
    try:
        date = pd.to_datetime(date_str)
        return date.strftime('%Y-%m-%d')
    except:
        return str(date_str)

# Read the Excel file
excel_path = '../raw_data/alle_Anfragen_Beantwortungen/Parlamentsanfragen.xlsx'
df = pd.read_excel(excel_path)

# Get the first row as actual headers if they are more meaningful
first_row = df.iloc[0]
df = df.iloc[1:]  # Remove the first row from the data
df.columns = [str(first_row[i]) if not pd.isna(first_row[i]) else col for i, col in enumerate(df.columns)]

# Clean column names by removing 'Unnamed: ' prefix and numbers
df.columns = [col.replace('Unnamed: ', '') if 'Unnamed: ' in col else col for col in df.columns]

# Remove columns that contain only NaN values
df = df.dropna(axis=1, how='all')

# Remove rows that contain only NaN values
df = df.dropna(axis=0, how='all')

# Define column widths (in cm)
col_widths = {
    'Nummer': '1.5cm',
    'Name': '4cm',
    'Einlangen': '2cm',
    'Link': '2.5cm',
    'Beantwortung': '1.5cm',
    'Beantwortungslink': '2.5cm',
    'Beantwortungseinlangen': '2cm'
}

# Start creating the LaTeX content
latex_content = [
    '\\documentclass[landscape]{article}',
    '\\usepackage[utf8]{inputenc}',
    '\\usepackage[T1]{fontenc}',
    '\\usepackage{longtable}',
    '\\usepackage{booktabs}',
    '\\usepackage{hyperref}',
    '\\usepackage[landscape,margin=1cm]{geometry}',
    '\\usepackage{array}',
    '\\begin{document}',
    '',
    '\\small  % Make table smaller',
    '% Table content begins',
]

# Create column format string
col_format = '@{}'
for col in df.columns:
    width = col_widths.get(col, '2cm')  # default 2cm if not specified
    col_format += f'p{{{width}}}'
col_format += '@{}'

latex_content.append(f'\\begin{{longtable}}{{{col_format}}}')
latex_content.extend([
    '\\toprule',
])

# Add header
header = ' & '.join(escape_latex(col) for col in df.columns) + ' \\\\'
latex_content.append(header)
latex_content.append('\\midrule')
latex_content.append('\\endhead')

# Add data rows
for _, row in df.iterrows():
    row_content = []
    for col, item in row.items():
        if 'einlangen' in col.lower():
            escaped_item = format_date(item)
        else:
            escaped_item = escape_latex(item)
            if isinstance(item, str) and item.startswith('http'):
                escaped_item = create_hyperlink(item)
        row_content.append(escaped_item)
    latex_content.append(' & '.join(row_content) + ' \\\\')

# Close the table and document
latex_content.extend([
    '\\bottomrule',
    '\\end{longtable}',
    '\\end{document}'
])

# Write to file
output_path = 'table_output.tex'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(latex_content))

print(f"LaTeX table has been created and saved to {output_path}") 