import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

# Read the data
df_beträge = pd.read_csv('../data/csv/02_OEGK_Betraege_pro_Fachrichtung_2023.csv')
df_anträge = pd.read_csv('../data/csv/03_OEGK_Antraege_pro_Monat_2023_pro_Fachrichtung_online_postal_Bundesweit.csv')

# Calculate average number of applications per specialty
monthly_avg = df_anträge.groupby('Fachrichtung')['Gesamt'].mean().reset_index()

# Merge the data
df = pd.merge(df_beträge, monthly_avg, on='Fachrichtung', how='left')

# Calculate ratios
df['Refundierungsrate'] = (df['Refundierungen'] / df['Rechnungsbeträge']) * 100
df['Durchschnittlicher_Rechnungsbetrag'] = df['Rechnungsbeträge'] / df['Gesamt']

# Sort by FG-Code (except Gesamt)
df_sorted = df[df['Fachrichtung'] != 'Gesamt'].sort_values('FG-Code')
df_gesamt = df[df['Fachrichtung'] == 'Gesamt']

# Combine sorted data with Gesamt at the top and remove empty rows
df_final = pd.concat([df_gesamt, df_sorted])
df_final = df_final.dropna(subset=['Refundierungen', 'Rechnungsbeträge'])

# Create shortened names with specific replacements
def shorten_name(name):
    replacements = {
        'FA für ': '',
        'Arzt für ': '',
        'Frauenheilkunde und Geburtshilfe': 'Gynäkologie',
        'Haut- und Geschlechtskrankheiten': 'Dermatologie',
        'Kinder- und Jugendheilkunde': 'Pädiatrie',
        'Innere Medizin': 'Innere Med.',
        'Orthopädie und orthopädische Chirurgie': 'Orthopädie',
        'Physikalische Medizin': 'Phys. Med.',
        'medizinische und chemische Labordiagnostik': 'Labordiagnostik',
        'Mund-, Kiefer- und Gesichtschirurgie': 'MKG-Chirurgie',
        'Strahlentherapie - Radioonkologie': 'Strahlentherapie',
        'Hygiene und Mikrobiologie bzw. Labordiagnostik': 'Hygiene & Mikrobiologie',
        'Neurologie und Psychiatrie/ Psychiatrie und Neurologie': 'Neuro. & Psych.',
        'Hals-, Nasen- und Ohrenerkrankungen': 'HNO',
        'Anästhesiologie und Intensivmedizin': 'Anästhesiologie & Intensivmed.',
        'Augenheilkunde und Optometrie': 'Augenheilkunde',
        'Kinder- und Jugendpsychiatrie': 'Kinder- & Jugendpsych.',
        'Pathologie und Histologie': 'Pathologie & Histologie',
        'und': '&'
    }
    for old, new in replacements.items():
        name = name.replace(old, new)
    return name

df_final['Kurzname'] = df_final['Fachrichtung'].apply(shorten_name)

# Calculate min/max values for scales
refund_min = 10  # Start at 10%
refund_max = 90  # Increased maximum for better scale
betrag_min = 0   # Start at 0 for money
betrag_max = 5000  # Fixed maximum for better scale

# Set figure style
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = 'white'
plt.rcParams['font.family'] = 'sans-serif'

# Create the plot with adjusted column widths
fig, ax = plt.subplots(figsize=(13, 16))  # Adjusted height
ax.set_xlim(-0.2, 4.2)  # Wider range for better spacing
ax.set_ylim(-1, len(df_final))  # Reduced bottom space

# Remove axes
ax.axis('off')

# Add title
plt.title('ÖGK Beträge und Refundierungsraten pro Fachrichtung 2023', 
          pad=10, fontsize=18, fontweight='bold', y=1.03)

# Column headers with adjusted positions
headers = ['Fachrichtung', 'FG-Code', 'Refundierungsrate', 'Durchschnittl. Rechnungsbetrag']
positions = [-0.1, 1.2, 2.0, 3.4]  # Moved FG-Code from 0.8 to 1.0
for i, (header, pos) in enumerate(zip(headers, positions)):
    ax.text(pos, len(df_final), header, ha='left' if i == 0 else 'center', 
            va='bottom', fontweight='bold', fontsize=14)

# Add scale backgrounds and grid
def draw_scale_background(x, y, width=1.2, height=len(df_final), color='gray', alpha=0.05):
    ax.add_patch(plt.Rectangle((x-width/2, -0.5), width, height, 
                              facecolor=color, alpha=alpha, edgecolor='none'))
    # Add vertical grid lines
    for i in range(5):  # 5 grid lines
        grid_x = x - width/2 + (width * i/4)
        ax.vlines(grid_x, -0.5, height-0.5, color='gray', alpha=0.15, linestyle='-')

draw_scale_background(2.0, -0.5)  # Refundierungsrate background
draw_scale_background(3.4, -0.5)  # Rechnungsbetrag background

# Plot data
for idx, row in df_final.iterrows():
    y_pos = len(df_final) - df_final.index.get_loc(idx) - 1
    
    # Background for alternating rows
    if idx % 2 == 0:
        ax.axhspan(y_pos-0.5, y_pos+0.5, color='gray', alpha=0.05)
    
    # Fachrichtung (adjusted position)
    ax.text(-0.1, y_pos, row['Kurzname'], ha='left', va='center', fontsize=12)
    
    # FG-Code (adjusted position) - as integer
    if pd.notna(row['FG-Code']):
        ax.text(1.2, y_pos, f"{int(row['FG-Code'])}", ha='center', va='center', fontsize=12)
    else:
        ax.text(1.2, y_pos, "—", ha='center', va='center', fontsize=12)
    
    # Horizontal guide lines (dotted)
    ax.hlines(y_pos, 1.4, 4.0, color='gray', alpha=0.2, linestyle=':')
    
    # Refundierungsrate (diamond on scale)
    rate = row['Refundierungsrate']
    if not pd.isna(rate):
        # Calculate x position based on value
        x_pos = 2.0 - 0.6 + (1.2 * (rate - refund_min) / (refund_max - refund_min))
        ax.plot(x_pos, y_pos, 'D', color='royalblue', markersize=14)
        # Add white background to text for better readability
        ax.text(x_pos, y_pos, f"{rate:.1f}%", ha='center', va='center',
                color='black', fontsize=11, fontweight='bold',
                bbox=dict(facecolor='white', edgecolor='none', alpha=0.8, pad=1))
    
    # Durchschnittlicher Rechnungsbetrag (diamond on scale)
    avg_amount = row['Durchschnittlicher_Rechnungsbetrag']
    if not pd.isna(avg_amount):
        # Calculate x position based on value
        x_pos = 3.4 - 0.6 + (1.2 * (avg_amount - betrag_min) / (betrag_max - betrag_min))
        ax.plot(x_pos, y_pos, 'D', color='forestgreen', markersize=14)
        formatted_amount = f"{avg_amount:,.0f}€".replace(",", ".")
        # Add white background to text for better readability
        ax.text(x_pos, y_pos, formatted_amount, ha='center', va='center',
                color='black', fontsize=11, fontweight='bold',
                bbox=dict(facecolor='white', edgecolor='none', alpha=0.8, pad=1))

# Add scale indicators with background
def add_scale_label(x, text, ha='center', va='top', y=-0.7):
    ax.text(x, y, text, ha=ha, va=va, fontsize=12,
            bbox=dict(facecolor='white', edgecolor='lightgray', alpha=1, pad=3))

# Refundierungsrate scale with intermediate values
add_scale_label(2.0-0.6, "10%", ha='center')
add_scale_label(2.0, "50%", ha='center')
add_scale_label(2.0+0.6, "90%", ha='center')

# Rechnungsbetrag scale with intermediate values
add_scale_label(3.4-0.6, "0€", ha='center')
add_scale_label(3.4, "2.500€", ha='center')
add_scale_label(3.4+0.6, "5.000€", ha='center')

# Save the plot
plt.savefig('../figures/OEGK/Betraege/oegk_betraege_pro_fachrichtung.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close() 