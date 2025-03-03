import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

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

# Get unique dates and FG-Codes
dates = df["Date"].unique()
fg_codes = df["FG-Code"].dropna().unique()

# Create bottom array for stacking
bottom = np.zeros(len(dates))

# Create distinct color pairs for postal and online
# Using highly contrasting colors for each pair
base_colors = [
    ("#1f77b4", "#aec7e8"),  # Blue
    ("#ff7f0e", "#ffbb78"),  # Orange
    ("#2ca02c", "#98df8a"),  # Green
    ("#d62728", "#ff9896"),  # Red
    ("#9467bd", "#c5b0d5"),  # Purple
    ("#8c564b", "#c49c94"),  # Brown
    ("#e377c2", "#f7b6d2"),  # Pink
    ("#7f7f7f", "#c7c7c7"),  # Gray
    ("#bcbd22", "#dbdb8d"),  # Yellow-green
    ("#17becf", "#9edae5"),  # Cyan
    ("#393b79", "#9c9ede"),  # Dark blue
    ("#637939", "#b5cf6b"),  # Olive
    ("#8c6d31", "#e7ba52"),  # Gold
    ("#843c39", "#de9ed6"),  # Burgundy
    ("#7b4173", "#ce6dbd"),  # Magenta
    ("#5254a3", "#6b6ecf"),  # Indigo
    ("#bd9e39", "#edae49"),  # Golden brown
    ("#ad494a", "#fb6a4a"),  # Salmon
    ("#6b6ecf", "#9c9ede"),  # Light purple
    ("#b5cf6b", "#cedb9c"),  # Light green
    ("#8B0000", "#FFB6C1"),  # Dark red to light pink
    ("#006400", "#98FB98"),  # Dark green to light green
    ("#4B0082", "#E6E6FA"),  # Indigo to lavender
    ("#8B4513", "#DEB887"),  # Saddle brown to burlywood
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

            ax.text(
                j,
                bottom[j] + total / 2,
                str(int(fg)),
                ha="center",
                va="center",
                fontsize=8,
            )

    bottom += total_values

# Customize the plot
plt.title(
    "ÖGK Anträge pro Monat nach Fachrichtung (Postal/Online Split)", fontsize=16, pad=20
)
plt.xlabel("Monat", fontsize=12)
plt.ylabel("Anzahl Anträge", fontsize=12, labelpad=10)
plt.xticks(range(len(dates)), [d.strftime("%b %Y") for d in dates], rotation=45)
plt.grid(True, axis="y", linestyle="--", alpha=0.7)

# Set the axis limits
ax.set_xlim(-0.5, len(dates) - 0.5)
ax.set_ylim(0, total_height * 1.08)  # Add 8% padding at the top

# Add legend outside the plot
plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left", borderaxespad=0.0, fontsize=8)

# Adjust layout to prevent label cutoff
plt.tight_layout()

# Save the plot
plt.savefig("oegk_antraege_stacked.png", dpi=300, bbox_inches="tight")
plt.close()
