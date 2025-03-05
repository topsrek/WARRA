import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
import os

# Global settings
OUTPUT_DIR = "../figures/OEGK/Antraege"  # Output directory for the plot

# Group cutoff percentages
TOP_GROUP_CUTOFF = 85  # Top group includes Fachrichtungen responsible for up to 75% of total applications
BOTTOM_GROUP_CUTOFF = 1  # Bottom group includes Fachrichtungen responsible for the last 3% of total applications

def create_base_colors():
    """Create distinct color pairs for postal and online submissions."""
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
    return base_colors

def setup_plot_style(dark_mode=True):
    """Setup the plot style based on dark/light mode."""
    if dark_mode:
        plt.style.use('dark_background')
        text_color = 'white'
        bg_color = '#1a1a1a'
        grid_alpha = 0.2
    else:
        plt.style.use('default')
        text_color = 'black'
        bg_color = 'white'
        grid_alpha = 0.7
    
    return text_color, bg_color, grid_alpha

def create_stacked_plot(df, dark_mode=True, output_filename=None):
    """Create the original stacked bar plot."""
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Create mapping of FG-Code to Fachrichtung
    fg_mapping = dict(zip(df["FG-Code"].dropna(), df["Fachrichtung"].dropna()))
    
    # Filter out the 'Gesamt' rows and create a copy to avoid the warning
    df = df[df["Fachrichtung"] != "Gesamt"].copy()
    
    # Convert Date to datetime and sort
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values(["Date", "FG-Code"])
    
    # Create figure
    fig, ax = plt.subplots(figsize=(20, 20))
    
    # Setup style
    text_color, bg_color, grid_alpha = setup_plot_style(dark_mode)
    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)
    
    # Get unique dates and FG-Codes
    dates = df["Date"].unique()
    fg_codes = df["FG-Code"].dropna().unique()
    
    # Setup colors
    base_colors = create_base_colors()
    while len(base_colors) < len(fg_codes):
        base_colors.extend(base_colors)
    
    postal_colors = [pair[0] for pair in base_colors[: len(fg_codes)]]
    online_colors = [pair[1] for pair in base_colors[: len(fg_codes)]]
    
    # Plot stacked bars
    bar_width = 0.8
    bottom = np.zeros(len(dates))
    total_height = df.groupby("Date")["Gesamt"].sum().max()
    
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
                
                # Postal rectangle
                postal_rect = Rectangle(
                    (j - bar_width / 2, bottom[j]),
                    bar_width * postal_ratio,
                    total,
                    facecolor=postal_colors[i],
                    alpha=0.8,
                    label=f"{fg} - {fg_mapping[fg]} (Postal)" if j == 0 else "",
                )
                ax.add_patch(postal_rect)
                
                # Online rectangle
                online_rect = Rectangle(
                    (j - bar_width / 2 + bar_width * postal_ratio, bottom[j]),
                    bar_width * online_ratio,
                    total,
                    facecolor=online_colors[i],
                    alpha=0.8,
                    label=f"{fg} - {fg_mapping[fg]} (Online)" if j == 0 else "",
                )
                ax.add_patch(online_rect)
                
                # Add FG code text
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
    
    # Customize plot
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
    
    # Add grid
    ax.grid(True, axis="y", linestyle="--", alpha=grid_alpha, color=text_color)
    
    # Set axis limits
    ax.set_xlim(-0.5, len(dates) - 0.5)
    ax.set_ylim(0, total_height * 1.05)
    
    # Add legend
    legend_kwargs = {
        "bbox_to_anchor": (1.02, 1),
        "loc": "upper left",
        "borderaxespad": 0.0,
        "fontsize": 8
    }
    
    if dark_mode:
        legend_kwargs.update({
            "facecolor": bg_color,
            "edgecolor": "white",
            "labelcolor": "white"
        })
    
    plt.legend(**legend_kwargs)
    plt.tight_layout()
    
    # Save plot
    if output_filename is None:
        output_filename = os.path.join(OUTPUT_DIR, "oegk_antraege_stacked_dark.png" if dark_mode else "oegk_antraege_stacked.png")
    
    save_kwargs = {
        "dpi": 300,
        "bbox_inches": "tight"
    }
    
    if dark_mode:
        save_kwargs.update({
            "facecolor": bg_color,
            "edgecolor": "none"
        })
    
    plt.savefig(output_filename, **save_kwargs)
    plt.close()

def create_ranked_grouped_plot(df, dark_mode=True):
    """Create a plot with three subplots based on rank-based grouping."""
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Calculate yearly average applications per Fachrichtung
    yearly_avg = df[df["Fachrichtung"] != "Gesamt"].groupby("Fachrichtung")["Gesamt"].mean()
    yearly_avg = yearly_avg.sort_values(ascending=False)  # Sort by yearly average in descending order
    
    # Calculate cumulative percentage based on yearly averages
    total_sum = yearly_avg.sum()
    cumsum_percentage = yearly_avg.cumsum() / total_sum * 100
    
    # Group Fachrichtungen based on cumulative percentage
    group1_mask = cumsum_percentage <= TOP_GROUP_CUTOFF
    group2_mask = (cumsum_percentage > TOP_GROUP_CUTOFF) & (cumsum_percentage <= (100 - BOTTOM_GROUP_CUTOFF))
    group3_mask = cumsum_percentage > (100 - BOTTOM_GROUP_CUTOFF)
    
    group1_fgs = yearly_avg[group1_mask].index
    group2_fgs = yearly_avg[group2_mask].index
    group3_fgs = yearly_avg[group3_mask].index
    
    # Print group statistics for debugging
    print(f"\nGroup Statistics (based on yearly averages):")
    print(f"Top group ({TOP_GROUP_CUTOFF}%): {len(group1_fgs)} Fachrichtungen")
    print(f"Middle group ({TOP_GROUP_CUTOFF}-{100-BOTTOM_GROUP_CUTOFF}%): {len(group2_fgs)} Fachrichtungen")
    print(f"Bottom group (last {BOTTOM_GROUP_CUTOFF}%): {len(group3_fgs)} Fachrichtungen")
    
    # Print the Fachrichtungen in each group for verification
    print("\nTop group Fachrichtungen:")
    for fg in group1_fgs:
        print(f"- {fg}")
    print("\nMiddle group Fachrichtungen:")
    for fg in group2_fgs:
        print(f"- {fg}")
    print("\nBottom group Fachrichtungen:")
    for fg in group3_fgs:
        print(f"- {fg}")
    
    # Create figure with three subplots
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(20, 30))
    
    # Setup style
    text_color, bg_color, grid_alpha = setup_plot_style(dark_mode)
    fig.patch.set_facecolor(bg_color)
    for ax in [ax1, ax2, ax3]:
        ax.set_facecolor(bg_color)
    
    # Create plots for each group
    create_group_subplot(df, group1_fgs, ax1, f"Top Fachrichtungen (bis {TOP_GROUP_CUTOFF}% der Anträge)", text_color, grid_alpha, dark_mode, bg_color)
    create_group_subplot(df, group2_fgs, ax2, f"Mittlere Fachrichtungen ({TOP_GROUP_CUTOFF}-{100-BOTTOM_GROUP_CUTOFF}% der Anträge)", text_color, grid_alpha, dark_mode, bg_color)
    create_group_subplot(df, group3_fgs, ax3, f"Kleine Fachrichtungen (letzte {BOTTOM_GROUP_CUTOFF}% der Anträge)", text_color, grid_alpha, dark_mode, bg_color)
    
    plt.tight_layout()
    
    # Save plot
    output_filename = os.path.join(OUTPUT_DIR, "oegk_antraege_ranked_groups_dark.png" if dark_mode else "oegk_antraege_ranked_groups.png")
    
    save_kwargs = {
        "dpi": 300,
        "bbox_inches": "tight"
    }
    
    if dark_mode:
        save_kwargs.update({
            "facecolor": bg_color,
            "edgecolor": "none"
        })
    
    plt.savefig(output_filename, **save_kwargs)
    plt.close()

def create_group_subplot(df, fachrichtungen, ax, title, text_color, grid_alpha, dark_mode, bg_color):
    """Create a subplot for a specific group of Fachrichtungen."""
    # Filter data for the group and create a copy to avoid the warning
    group_data = df[df["Fachrichtung"].isin(fachrichtungen)].copy()
    
    # Create mapping of FG-Code to Fachrichtung
    fg_mapping = dict(zip(df["FG-Code"].dropna(), df["Fachrichtung"].dropna()))
    
    # Convert Date to datetime and sort
    group_data["Date"] = pd.to_datetime(group_data["Date"])
    group_data = group_data.sort_values(["Date", "FG-Code"])
    
    # Get unique dates and FG-Codes
    dates = group_data["Date"].unique()
    
    # Calculate yearly average for each FG-Code in this group and sort by it
    yearly_avg = group_data.groupby("FG-Code")["Gesamt"].mean().sort_values(ascending=False)
    fg_codes = yearly_avg.index.dropna().unique()
    
    # Setup colors
    base_colors = create_base_colors()
    while len(base_colors) < len(fg_codes):
        base_colors.extend(base_colors)
    
    postal_colors = [pair[0] for pair in base_colors[: len(fg_codes)]]
    online_colors = [pair[1] for pair in base_colors[: len(fg_codes)]]
    
    # Plot stacked bars
    bar_width = 0.8
    bottom = np.zeros(len(dates))
    total_height = group_data.groupby("Date")["Gesamt"].sum().max()
    
    for i, fg in enumerate(fg_codes):
        fg_data = group_data[group_data["FG-Code"] == fg]
        
        postal_values = fg_data["postal"].values
        online_values = fg_data["online"].values
        total_values = postal_values + online_values
        
        for j in range(len(dates)):
            total = total_values[j]
            if total > 0:
                postal_ratio = postal_values[j] / total
                online_ratio = online_values[j] / total
                
                # Postal rectangle
                postal_rect = Rectangle(
                    (j - bar_width / 2, bottom[j]),
                    bar_width * postal_ratio,
                    total,
                    facecolor=postal_colors[i],
                    alpha=0.8,
                    label=f"{fg} - {fg_mapping[fg]} (Postal)" if j == 0 else "",
                )
                ax.add_patch(postal_rect)
                
                # Online rectangle
                online_rect = Rectangle(
                    (j - bar_width / 2 + bar_width * postal_ratio, bottom[j]),
                    bar_width * online_ratio,
                    total,
                    facecolor=online_colors[i],
                    alpha=0.8,
                    label=f"{fg} - {fg_mapping[fg]} (Online)" if j == 0 else "",
                )
                ax.add_patch(online_rect)
                
                # Add FG code text
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
    
    # Customize subplot
    ax.set_title(title, fontsize=14, pad=20, color=text_color)
    ax.set_xlabel("Monat", fontsize=12, color=text_color)
    ax.set_ylabel("Anzahl Anträge", fontsize=12, labelpad=10, color=text_color)
    ax.set_xticks(range(len(dates)))
    ax.set_xticklabels([d.strftime("%b %Y") for d in dates], rotation=45, color=text_color)
    ax.tick_params(colors=text_color)
    
    # Add grid
    ax.grid(True, axis="y", linestyle="--", alpha=grid_alpha, color=text_color)
    
    # Set axis limits
    ax.set_xlim(-0.5, len(dates) - 0.5)
    ax.set_ylim(0, total_height * 1.05)
    
    # Add legend
    legend_kwargs = {
        "bbox_to_anchor": (1.02, 1),
        "loc": "upper left",
        "borderaxespad": 0.0,
        "fontsize": 8
    }
    
    if dark_mode:
        legend_kwargs.update({
            "facecolor": bg_color,
            "edgecolor": "white",
            "labelcolor": "white"
        })
    
    ax.legend(**legend_kwargs)

def main():
    # Read the CSV file
    df = pd.read_csv(
        "../data/csv/03_OEGK_Antraege_pro_Monat_2023_pro_Fachrichtung_online_postal_Bundesweit.csv"
    )
    
    # Create original plots in both light and dark mode
    create_stacked_plot(df, dark_mode=True)
    create_stacked_plot(df, dark_mode=False)
    
    # Create ranked grouped plots in both light and dark mode
    create_ranked_grouped_plot(df, dark_mode=True)
    create_ranked_grouped_plot(df, dark_mode=False)

if __name__ == "__main__":
    main()
