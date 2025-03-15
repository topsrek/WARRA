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
        "FA für ": "",
        "Arzt für ": "",
        "Frauenheilkunde und Geburtshilfe": "Gynäkologie",
        "Haut- und Geschlechtskrankheiten": "Dermatologie",
        "Kinder- und Jugendheilkunde": "Pädiatrie",
        "Innere Medizin": "Innere Med.",
        "Orthopädie und orthopädische Chirurgie": "Orthopädie",
        "Physikalische Medizin": "Phys. Med.",
        "medizinische und chemische Labordiagnostik": "Labordiagnostik",
        "Mund-, Kiefer- und Gesichtschirurgie": "MKG-Chirurgie",
        "Strahlentherapie - Radioonkologie": "Strahlentherapie",
        "Hygiene und Mikrobiologie bzw. Labordiagnostik": "Hygiene & Mikrobiologie",
        "Neurologie und Psychiatrie/ Psychiatrie und Neurologie": "Neurologie & Psychiatrie",
        "Hals-, Nasen- und Ohrenerkrankungen": "HNO",
        "Anästhesiologie und Intensivmedizin": "Anästhesiologie & Intensivmed.",
        "Augenheilkunde und Optometrie": "Augenheilkunde",
        "Kinder- und Jugendpsychiatrie": "Kinder- & Jugendpsychiatrie",
        "Pathologie und Histologie": "Pathologie & Histologie",
        " und ": " & ",
    }
    for old, new in replacements.items():
        name = name.replace(old, new)
    return name

df_final['Kurzname'] = df_final['Fachrichtung'].apply(shorten_name)

# Layout parameters
FIGURE_WIDTH = 13
FIGURE_HEIGHT = 16
LEFT_MARGIN = -0.1
RIGHT_MARGIN = 3.55
BOTTOM_MARGIN = -0.5
TOP_MARGIN = len(df_final)
SCALE_WIDTH = 1.1
SCALE_SPACING = 1.3

# Column positions
COL_FACHRICHTUNG = -0.1
COL_REFUND = 1.6
COL_BETRAG = 2.9

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
fig, ax = plt.subplots(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT))
ax.set_xlim(LEFT_MARGIN, RIGHT_MARGIN)
ax.set_ylim(BOTTOM_MARGIN, TOP_MARGIN)

# Create twin axis for top scales
ax_top = ax.twiny()
ax_top.set_xlim(LEFT_MARGIN, RIGHT_MARGIN)
ax_top.set_ylim(BOTTOM_MARGIN, TOP_MARGIN)
ax_top.axis('off')

# Remove axes
ax.axis('off')

# Add title
plt.title('ÖGK Refundierungsraten und\nDurchschnittlicher Rechnungsbetrag je Fachrichtung 2023', 
          pad=25, fontsize=18, fontweight='bold', y=1.02)

# Column headers with adjusted positions
headers = ["Fachrichtung", "Refundierungsrate (%)", "Ø Rechnungsbetrag (€)"]
positions = [COL_FACHRICHTUNG, COL_REFUND, COL_BETRAG]
for i, (header, pos) in enumerate(zip(headers, positions)):
    ax_top.text(pos, TOP_MARGIN+0.5, header, ha='left' if i == 0 else 'center', 
                va='bottom', fontweight='bold', fontsize=14)

# Add scale backgrounds and grid
def draw_scale_background(x, y, width=SCALE_WIDTH, height=TOP_MARGIN, color='gray', alpha=0.05):
    ax.add_patch(plt.Rectangle((x-width/2, BOTTOM_MARGIN), width, height, 
                              facecolor=color, alpha=alpha, edgecolor='none'))
    # Add vertical grid lines
    for i in range(5):  # 5 grid lines
        grid_x = x - width/2 + (width * i/4)
        ax.vlines(grid_x, BOTTOM_MARGIN, height-0.5, color='gray', alpha=0.15, linestyle='-')

draw_scale_background(COL_REFUND, BOTTOM_MARGIN)  # Refundierungsrate background
draw_scale_background(COL_BETRAG, BOTTOM_MARGIN)  # Rechnungsbetrag background

# Plot data
for idx, row in df_final.iterrows():
    y_pos = TOP_MARGIN - df_final.index.get_loc(idx) - 1

    # Background for alternating rows
    if idx % 2 == 0:
        ax.axhspan(y_pos-0.5, y_pos+0.5, color='gray', alpha=0.05)

    # Fachrichtung
    ax.text(COL_FACHRICHTUNG, y_pos, row['Kurzname'], ha='left', va='center', fontsize=12)

    # Horizontal guide lines (dotted)
    ax.hlines(y_pos, LEFT_MARGIN+0.1, RIGHT_MARGIN-0.1, color='gray', alpha=0.15, linestyle=':')

    # Refundierungsrate (diamond on scale)
    rate = row['Refundierungsrate']
    if not pd.isna(rate):
        # Calculate x position based on value
        x_pos = COL_REFUND - SCALE_WIDTH/2 + (SCALE_WIDTH * (rate - refund_min) / (refund_max - refund_min))
        ax.add_patch(
            plt.Rectangle(
                (x_pos - 0.02, y_pos -0.5), 0.02, 1, color="royalblue", alpha=1
            )
        )

        # ax.plot(x_pos, y_pos, 'd', color='royalblue', markersize=14)
        # Add white background to text for better readability
        ax.text(
            x_pos+ 0.04,
            y_pos,
            f"{rate:.1f}%".replace(".", ","),
            ha="left",
            va="center",
            color="black",
            fontsize=11,
            bbox=dict(facecolor="white", edgecolor="none", alpha=1, pad=1),
        )

    # Durchschnittlicher Rechnungsbetrag (diamond on scale)
    avg_amount = row['Durchschnittlicher_Rechnungsbetrag']
    if not pd.isna(avg_amount):
        # Calculate x position based on value
        x_pos = COL_BETRAG - SCALE_WIDTH/2 + (SCALE_WIDTH * (avg_amount - betrag_min) / (betrag_max - betrag_min))
        ax.add_patch(
            plt.Rectangle(
                (x_pos - 0.02, y_pos -0.5), 0.02, 1, color="forestgreen", alpha=1
            )
        )
        formatted_amount = f"{avg_amount:,.0f}€".replace(",", ".")
        # Add white background to text for better readability
        ax.text(
            x_pos + 0.04,
            y_pos,
            formatted_amount,
            ha="left",
            va="center",
            color="black",
            fontsize=11,
            bbox=dict(facecolor="white", edgecolor="none", alpha=1, pad=1),
        )

# Add scale indicators with background
def add_scale_label(x, text, ha='center', va='top', y=BOTTOM_MARGIN-0.2):
    ax.text(x, y, text, ha=ha, va=va, fontsize=12,
            bbox=dict(facecolor='white', edgecolor='lightgray', alpha=1, pad=3))

# Add top scale indicators with background
def add_top_scale_label(x, text, ha='center', va='bottom', y=TOP_MARGIN-0.3):
    ax_top.text(x, y, text, ha=ha, va=va, fontsize=12,
                bbox=dict(facecolor='white', edgecolor='lightgray', alpha=1, pad=3))

# Bottom Refundierungsrate scale with intermediate values
add_scale_label(COL_REFUND-SCALE_WIDTH/2, "10%", ha='center')
add_scale_label(COL_REFUND, "50%", ha='center')
add_scale_label(COL_REFUND+SCALE_WIDTH/2, "90%", ha='center')

# Bottom Rechnungsbetrag scale with intermediate values
add_scale_label(COL_BETRAG-SCALE_WIDTH/2, "0€", ha='center')
add_scale_label(COL_BETRAG, "2.500€", ha='center')
add_scale_label(COL_BETRAG+SCALE_WIDTH/2, "5.000€", ha='center')

# Top Refundierungsrate scale with intermediate values
add_top_scale_label(COL_REFUND-SCALE_WIDTH/2, "10%", ha='center')
add_top_scale_label(COL_REFUND, "50%", ha='center')
add_top_scale_label(COL_REFUND+SCALE_WIDTH/2, "90%", ha='center')

# Top Rechnungsbetrag scale with intermediate values
add_top_scale_label(COL_BETRAG-SCALE_WIDTH/2, "0€", ha='center')
add_top_scale_label(COL_BETRAG, "2.500€", ha='center')
add_top_scale_label(COL_BETRAG+SCALE_WIDTH/2, "5.000€", ha='center')

# Save the plot
plt.savefig('../figures/OEGK/Betraege/oegk_betraege_pro_fachrichtung.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close() 
