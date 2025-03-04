import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
import os

# Global settings
DARK_MODE = True  # Set to False for light mode
OUTPUT_DIR = "../figures/OEGK/Antraege"  # Output directory for the plot

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Read the CSV file
df = pd.read_csv(
    "../data/csv/03_OEGK_Antraege_pro_Monat_2023_pro_Fachrichtung_online_postal_Bundesweit.csv"
)

# Create a mapping of FG-Code to Fachrichtung
fg_mapping = dict(zip(df["FG-Code"].dropna(), df["Fachrichtung"].dropna()))

# Filter out the 'Gesamt' rows
df = df[df["Fachrichtung"] != "Gesamt"]

# Convert Date to datetime
df["Date"] = pd.to_datetime(df["Date"])

# Sort by Date and FG-Code
df = df.sort_values(["Date", "FG-Code"])

# Create figure with large size
fig, ax = plt.subplots(figsize=(20, 12))

# Set dark mode if enabled
if DARK_MODE:
    plt.style.use('dark_background')
    fig.patch.set_facecolor('#1a1a1a')
    ax.set_facecolor('#1a1a1a')

# Get unique dates and FG-Codes
dates = df["Date"].unique()
fg_codes = df["FG-Code"].dropna().unique()

# Create bottom array for stacking
bottom = np.zeros(len(dates))

# Create distinct color pairs for postal and online
# Using colors that work well in both light and dark mode
base_colors = [
    ("#4e79a7", "#a0cbe8"),  # Blue
    ("#f28e2c", "#ffbe7d"),  # Orange
    ("#59a14f", "#8cd17d"),  # Green
    ("#e15759", "#ff9d9a"),  # Red
    ("#b07aa1", "#d4a6c8"),  # Purple
    ("#9c755f", "#d3b4a8"),  # Brown
    ("#edc949", "#f1ce63"),  # Yellow
    ("#76b7b2", "#b3e4dc"),  # Teal
    ("#ff9da7", "#ffc9c9"),  # Pink
    ("#9c9ede", "#c5cbd3"),  # Gray
    ("#bab0ab", "#d3d3d3"),  # Light gray
    ("#79706e", "#a8a8a8"),  # Dark gray
    ("#d37295", "#f8a5c2"),  # Rose
    ("#b279a2", "#d4a6c8"),  # Mauve
    ("#9d7660", "#d4a6c8"),  # Tan
    ("#a0cbe8", "#b3e4dc"),  # Light blue
    ("#f1ce63", "#edc949"),  # Gold
    ("#ff9da7", "#ffc9c9"),  # Light pink
    ("#76b7b2", "#b3e4dc"),  # Sea green
    ("#9c9ede", "#c5cbd3"),  # Lavender
    ("#4e79a7", "#a0cbe8"),  # Navy
    ("#f28e2c", "#ffbe7d"),  # Coral
    ("#59a14f", "#8cd17d"),  # Forest green
    ("#e15759", "#ff9d9a")   # Crimson
]

# Extend the color list if we have more FG codes than colors
while len(base_colors) < len(fg_codes):
    base_colors.extend(base_colors)

postal_colors = [pair[0] for pair in base_colors[: len(fg_codes)]]
online_colors = [pair[1] for pair in base_colors[: len(fg_codes)]]

# Set bar width
bar_width = 0.8

# Calculate total height for y-axis limit
total_height = df.groupby("Date")["Gesamt"].sum().max()

# Plot stacked bars
for i, fg in enumerate(fg_codes):
    fg_data = df[df["FG-Code"] == fg]

    postal_values = fg_data["postal"].values
    online_values = fg_data["online"].values
    total_values = postal_values + online_values

    for j in range(len(dates)):
        total = total_values[j]
        if total > 0:
            postal_ratio = postal_values[j] / total
            online_ratio = online_values[j] / total

            postal_rect = Rectangle(
                (j - bar_width / 2, bottom[j]),  # (x, y) position
                bar_width * postal_ratio,  # width
                total,  # height
                facecolor=postal_colors[i],
                alpha=0.8,
                label=f"{fg} - {fg_mapping[fg]} (Postal)" if j == 0 else "",
            )
            ax.add_patch(postal_rect)

            # Create online rectangle (right side)
            online_rect = Rectangle(
                (
                    j - bar_width / 2 + bar_width * postal_ratio,
                    bottom[j],
                ),  # (x, y) position
                bar_width * online_ratio,  # width
                total,  # height
                facecolor=online_colors[i],
                alpha=0.8,
                label=f"{fg} - {fg_mapping[fg]} (Online)" if j == 0 else "",
            )
            ax.add_patch(online_rect)

            # Set text color based on mode
            text_color = 'white' if DARK_MODE else 'black'
            ax.text(
                j,
                bottom[j] + total / 2,
                str(int(fg)),
                ha="center",
                va="center",
                fontsize=8,
                color=text_color
            )

    bottom += total_values

# Customize the plot
text_color = 'white' if DARK_MODE else 'black'
plt.title(
    "ÖGK Anträge pro Monat nach Fachrichtung (Postal/Online Split)", 
    fontsize=16, 
    pad=20,
    color=text_color
)
plt.xlabel("Monat", fontsize=12, color=text_color)
plt.ylabel("Anzahl Anträge", fontsize=12, labelpad=10, color=text_color)
plt.xticks(range(len(dates)), [d.strftime("%b %Y") for d in dates], rotation=45, color=text_color)
plt.yticks(color=text_color)

# Add grid with appropriate opacity for each mode
grid_alpha = 0.2 if DARK_MODE else 0.7
ax.grid(True, axis="y", linestyle="--", alpha=grid_alpha, color=text_color)

# Set the axis limits
ax.set_xlim(-0.5, len(dates) - 0.5)
ax.set_ylim(0, total_height * 1.08)  # Add 8% padding at the top

# Add legend outside the plot with appropriate styling
legend_kwargs = {
    "bbox_to_anchor": (1.02, 1),
    "loc": "upper left",
    "borderaxespad": 0.0,
    "fontsize": 8
}

if DARK_MODE:
    legend_kwargs.update({
        "facecolor": "#1a1a1a",
        "edgecolor": "white",
        "labelcolor": "white"
    })

plt.legend(**legend_kwargs)

# Adjust layout to prevent label cutoff
plt.tight_layout()

# Set output filename based on mode
filename = os.path.join(OUTPUT_DIR, "oegk_antraege_stacked_dark.png" if DARK_MODE else "oegk_antraege_stacked.png")

# Save the plot with appropriate background
save_kwargs = {
    "dpi": 300,
    "bbox_inches": "tight"
}

if DARK_MODE:
    save_kwargs.update({
        "facecolor": "#1a1a1a",
        "edgecolor": "none"
    })

plt.savefig(filename, **save_kwargs)
plt.close()
