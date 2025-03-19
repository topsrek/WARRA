import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from datetime import datetime

# Global settings
BASE_OUTPUT_DIR = "../figures/OEGK/Bearbeitungszeit"  # Base output directory for the plots

def translate_to_german_date(date):
    """Translate a date to German format."""
    month_str = date.strftime("%b %Y")
    return (
        month_str.replace("Jan", "Jän")
        .replace("Feb", "Feb")
        .replace("Mar", "Mär")
        .replace("Apr", "Apr")
        .replace("May", "Mai")
        .replace("Jun", "Jun")
        .replace("Jul", "Jul")
        .replace("Aug", "Aug")
        .replace("Sep", "Sep")
        .replace("Oct", "Okt")
        .replace("Nov", "Nov")
        .replace("Dec", "Dez")
    )

def prettify_bundesland(bundesland):
    """Prettify the Bundesland name."""
    LST_to_bundesland = {
        "B": "Burgenland",
        "K": "Kärnten",
        "N": "Niederösterreich",
        "NÖ": "Niederösterreich",
        "OÖ": "Oberösterreich",
        "S": "Salzburg",
        "ST": "Steiermark",
        "T": "Tirol",
        "V": "Vorarlberg",
        "W": "Wien"
    }
    return LST_to_bundesland[bundesland]

def setup_plot_style(dark_mode=True):
    """Setup the plot style based on dark/light mode."""
    plt.style.use('seaborn-v0_8')  # Use seaborn style as base
    
    if dark_mode:
        text_color = '#E8E8E8'  # Softer white
        bg_color = '#1E1E1E'    # Richer dark background
        grid_alpha = 0.15
        plt.rcParams['figure.facecolor'] = bg_color
        plt.rcParams['axes.facecolor'] = '#252525'  # Slightly lighter than background
    else:
        text_color = '#2F2F2F'  # Softer black
        bg_color = '#FFFFFF'
        grid_alpha = 0.2
        plt.rcParams['figure.facecolor'] = bg_color
        plt.rcParams['axes.facecolor'] = '#F8F8F8'  # Very light gray
    
    # Set global font settings
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial', 'DejaVu Sans']
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['xtick.labelsize'] = 10
    plt.rcParams['ytick.labelsize'] = 10
    
    # Set line styling
    plt.rcParams['axes.linewidth'] = 1.2
    plt.rcParams['grid.linewidth'] = 0.8
    plt.rcParams['lines.linewidth'] = 2.0
    plt.rcParams['lines.markersize'] = 6
    
    return text_color, bg_color, grid_alpha

def setup_plot_axes(ax, dates, text_color, grid_alpha):
    """Setup common plot axes configuration."""
    # Translate month names to German
    german_dates = [translate_to_german_date(d) for d in dates]
    
    # Set x-axis labels with rotation for better readability
    ax.set_xticks(range(len(dates)))
    ax.set_xticklabels(german_dates, rotation=45, ha='right', color=text_color)
    
    # Set y-axis color
    ax.tick_params(colors=text_color)
    
    # Add grid
    ax.grid(True, linestyle="--", alpha=grid_alpha, color=text_color)

def setup_legend(ax, dark_mode, bg_color, text_color):
    """Setup common legend configuration."""
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

def save_plot(fig, output_filename, dark_mode, bg_color):
    """Save plot with common configuration."""
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    
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

def get_bundesland_output_dir(bundesland):
    """Get the output directory for a specific Bundesland."""
    # Create a safe directory name from the Bundesland
    safe_name = bundesland.replace(" ", "_").replace("ö", "oe").replace("ä", "ae").replace("ü", "ue")
    return os.path.join(BASE_OUTPUT_DIR, safe_name)

def create_base_colors():
    """Create distinct color pairs for postal and online submissions."""
    base_colors = [
        # Primary colors with high contrast
        ("#1f77b4", "#7cc7ff", "#3a9edc"),  # Blue variants
        ("#ff7f0e", "#ffb74d", "#ff9b2f"),  # Orange variants
        ("#2ca02c", "#98df8a", "#5fc25f"),  # Green variants
        ("#d62728", "#ff9896", "#e85657"),  # Red variants
        ("#9467bd", "#c5b0d5", "#ab89c9"),  # Purple variants
        ("#8c564b", "#d4a792", "#a67a71"),  # Brown variants
        ("#e6b417", "#ffe169", "#edc645"),  # Yellow variants
        ("#17becf", "#9edae5", "#4cc4d4"),  # Turquoise variants
        ("#7f7f7f", "#c7c7c7", "#a3a3a3"),  # Gray variants
        ("#bcbd22", "#dbdb8d", "#cece55"),  # Olive variants
        ("#ff66b3", "#ffb3d9", "#ff8cc6"),  # Pink variants
        ("#4b0082", "#9b59b6", "#8e44ad"),  # Indigo variants
    ]
    return base_colors

def create_processing_time_plot(df_2023, df_historical, df_beilage6, bundesland, dark_mode=True):
    """Create a line plot showing processing times for postal and online submissions."""
    # Get output directory for this Bundesland
    output_dir = get_bundesland_output_dir(bundesland)
    os.makedirs(output_dir, exist_ok=True)

    # Create safe filename from Bundesland name
    safe_bundesland = bundesland.replace(" ", "_").replace("ö", "oe").replace("ä", "ae").replace("ü", "ue")

    # Filter data for the specific Bundesland
    df_2023_bl = df_2023[df_2023["Bundesland_pretty"] == bundesland].copy()
    df_hist_bl = df_historical[df_historical["Bundesland_pretty"] == bundesland].copy()
    df_beilage6_bl = df_beilage6[df_beilage6["Bundesland_pretty"] == bundesland].copy()

    # Merge the dataframes
    df_2023_bl["Date"] = pd.to_datetime(df_2023_bl["Date"])
    df_hist_bl["Date"] = pd.to_datetime(df_hist_bl["Date"])
    df_beilage6_bl["Date"] = pd.to_datetime(df_beilage6_bl["Date"])

    # Verify that overlapping data matches
    overlap_start = df_2023_bl["Date"].min()
    overlap_end = df_hist_bl["Date"].max()
    overlap_mask_2023 = (df_2023_bl["Date"] <= overlap_end)
    overlap_mask_hist = (df_hist_bl["Date"] >= overlap_start)

    df_overlap_2023 = df_2023_bl[overlap_mask_2023].sort_values("Date")
    df_overlap_hist = df_hist_bl[overlap_mask_hist].sort_values("Date")

    # Assert that overlapping data matches
    pd.testing.assert_frame_equal(
        df_overlap_2023[["Date", "Postal", "OnlineMeine"]].reset_index(drop=True),
        df_overlap_hist[["Date", "Postal", "OnlineMeine"]].reset_index(drop=True),
        check_dtype=False
    )

    # Combine the data
    df_combined = pd.concat([
        df_hist_bl[df_hist_bl["Date"] < overlap_start],
        df_2023_bl,
        df_beilage6_bl[df_beilage6_bl["Date"] > df_2023_bl["Date"].max()]
    ]).sort_values("Date")

    # Create figure with smaller size
    fig, ax = plt.subplots(figsize=(10, 6))

    # Setup style
    text_color, bg_color, grid_alpha = setup_plot_style(dark_mode)
    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)

    # Get dates for x-axis
    dates = df_combined["Date"].unique()
    german_dates = [translate_to_german_date(d) for d in dates]
    
    # Create labels for every third month
    date_labels = []
    for i, date in enumerate(german_dates):
        if i % 3 == 0:
            date_labels.append(date)
        else:
            date_labels.append("")

    # Setup modern color palette
    if dark_mode:
        postal_color = '#00A6FB'      # Bright blue
        online_color = '#51D88A'      # Bright green
        online_new_color = '#FB6107'  # Bright orange
    else:
        postal_color = '#1E88E5'      # Material blue
        online_color = '#43A047'      # Material green
        online_new_color = '#E65100'  # Material orange

    # Plot lines with enhanced styling
    ax.plot(range(len(dates)), df_combined["Postal"], 
            color=postal_color, marker='o', markersize=4, 
            label="Postal", linewidth=2, linestyle='-',
            alpha=0.9)

    ax.plot(range(len(dates)), df_combined["OnlineMeine"], 
            color=online_color, marker='o', markersize=4, 
            label="MeineÖGK", linewidth=2, linestyle='--',
            alpha=0.9)

    # Online (WAH) - only after May 2023
    mask_new_online = ~df_combined["OnlineWAH"].isna()
    if mask_new_online.any():
        dates_idx = np.where(mask_new_online)[0]
        ax.plot(dates_idx, df_combined[mask_new_online]["OnlineWAH"], 
                color=online_new_color, marker='o', markersize=4, 
                label="WAH", linewidth=2, linestyle=':',
                alpha=0.9)

    # Customize plot
    plt.title(
        f"ÖGK Durchschnittliche Bearbeitungszeit pro Monat - {bundesland}",
        fontsize=14,
        pad=20,
        color=text_color,
        fontweight='bold'
    )
    plt.xlabel("Monat", fontsize=12, color=text_color, labelpad=10)
    plt.ylabel("Durchschnittliche Bearbeitungszeit (Kalendertage)", fontsize=12, labelpad=10, color=text_color)

    # Setup axes with every third month
    ax.set_xticks(range(len(dates)))
    ax.set_xticklabels(date_labels, rotation=45, ha='right', color=text_color, fontsize=9)
    
    # Enhanced grid
    ax.grid(True, axis='y', linestyle="--", alpha=grid_alpha, color=text_color)
    
    for i in range(len(dates)):
        if i % 3 == 0:
            ax.axvline(x=i, color=text_color, linestyle='-', alpha=grid_alpha*1.2, linewidth=1.0)
        else:
            ax.axvline(x=i, color=text_color, linestyle='--', alpha=grid_alpha*0.6, linewidth=0.5)

    # Set y-axis limits with some padding
    y_min = min(df_combined[["Postal", "OnlineMeine", "OnlineWAH"]].min().min(), 0)
    y_max = df_combined[["Postal", "OnlineMeine", "OnlineWAH"]].max().max()
    ax.set_ylim(y_min * 0.95, y_max * 1.05)

    # Enhanced legend
    legend_kwargs = {
        "ncol": 1,
        "loc": "upper right",
        "bbox_to_anchor": (1.02, 1),
        "fontsize": 10,
        "handlelength": 2,
        "borderaxespad": 0,
        "frameon": True,
        "edgecolor": 'none',
        "facecolor": plt.rcParams['axes.facecolor'],
        "labelcolor": text_color,
        "columnspacing": 2.0,
        "handletextpad": 0.8,
    }
    
    ax.legend(**legend_kwargs)

    # Save plot with enhanced layout
    output_filename = os.path.join(output_dir, f"oegk_bearbeitungszeit_{safe_bundesland}_dark.png" if dark_mode else f"oegk_bearbeitungszeit_{safe_bundesland}.png")
    plt.tight_layout(rect=[0, 0, 0.85, 1])  # Adjusted layout to leave space for legend on the right
    save_plot(fig, output_filename, dark_mode, bg_color)

def create_combined_processing_time_plot(df_2023, df_historical, df_beilage6, dark_mode=True):
    """Create a line plot showing processing times for all Bundesländer together."""
    # Create output directory
    output_dir = BASE_OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)

    # Prepare data
    df_2023["Date"] = pd.to_datetime(df_2023["Date"])
    df_historical["Date"] = pd.to_datetime(df_historical["Date"])
    df_beilage6["Date"] = pd.to_datetime(df_beilage6["Date"])

    # Combine the data
    overlap_start = df_2023["Date"].min()
    df_combined = pd.concat([
        df_historical[df_historical["Date"] < overlap_start],
        df_2023,
        df_beilage6[df_beilage6["Date"] > df_2023["Date"].max()]
    ]).sort_values(["Date", "Bundesland_pretty"])

    # Create figure with adjusted size for legend
    fig, ax = plt.subplots(figsize=(16, 12))  # Reduced width to make legend more compact

    # Setup style
    text_color, bg_color, grid_alpha = setup_plot_style(dark_mode)
    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)

    # Get dates for x-axis
    dates = df_combined["Date"].unique()

    # Get unique Bundesländer
    bundeslaender = sorted(df_combined["Bundesland_pretty"].unique())

    # Setup colors - one base color per Bundesland
    base_colors = create_base_colors()
    
    # Plot lines for each Bundesland
    for idx, bundesland in enumerate(bundeslaender):
        bl_data = df_combined[df_combined["Bundesland_pretty"] == bundesland].sort_values("Date")
        
        # Get color variants for this Bundesland
        postal_color = base_colors[idx][0]
        online_color = base_colors[idx][1]
        online_new_color = base_colors[idx][2]
        
        # Ensure data is properly aligned with dates
        bl_data_aligned = pd.DataFrame(index=dates)
        bl_data_aligned = bl_data_aligned.join(bl_data.set_index("Date"))
        
        # Plot Postal (solid line)
        ax.plot(range(len(dates)), bl_data_aligned["Postal"], 
                color=postal_color, marker='o', markersize=3, 
                label=f"{bundesland} (Postal)", linewidth=1.5, linestyle='-')

        # Plot Online MeineÖGK (dashed line)
        ax.plot(range(len(dates)), bl_data_aligned["OnlineMeine"], 
                color=online_color, marker='o', markersize=3, 
                label=f"{bundesland} (MeineÖGK)", linewidth=1.5, linestyle='--')

        # Plot Online WAH (dotted line) - only after May 2023
        mask_new_online = ~bl_data_aligned["OnlineWAH"].isna()
        if mask_new_online.any():
            dates_idx = np.where(mask_new_online)[0]
            ax.plot(dates_idx, bl_data_aligned[mask_new_online]["OnlineWAH"], 
                    color=online_new_color, marker='o', markersize=3, 
                    label=f"{bundesland} (WAH)", linewidth=1.5, linestyle=':')

    # Customize plot
    plt.title(
        "ÖGK Durchschnittliche Bearbeitungszeit pro Monat - Alle Bundesländer",
        fontsize=16,
        pad=30,
        color=text_color
    )
    plt.xlabel("Monat", fontsize=12, color=text_color, labelpad=15)
    plt.ylabel("Durchschnittliche Bearbeitungszeit (Tage)", fontsize=12, labelpad=15, color=text_color)

    # Setup axes
    setup_plot_axes(ax, dates, text_color, grid_alpha)

    # Set y-axis limits with some padding
    y_min = min(df_combined[["Postal", "OnlineMeine", "OnlineWAH"]].min().min(), 0)
    y_max = df_combined[["Postal", "OnlineMeine", "OnlineWAH"]].max().max()
    ax.set_ylim(y_min * 0.95, y_max * 1.05)

    # Add legend with more columns and organized by Bundesland
    handles, labels = ax.get_legend_handles_labels()
    
    # Reorganize legend items to group by Bundesland
    n_bundeslaender = len(bundeslaender)
    n_types = 3  # Postal, MeineÖGK, WAH
    new_handles = []
    new_labels = []
    
    for i in range(0, len(handles), n_types):
        new_handles.extend(handles[i:i + n_types])
        new_labels.extend(labels[i:i + n_types])

    legend_kwargs = {
        "bbox_to_anchor": (1.02, 1),
        "loc": "upper left",
        "borderaxespad": 0.0,
        "fontsize": 8,
        "ncol": 1,  # Single column for more compact layout
        "handlelength": 1.5,  # Shorter lines in legend
        "columnspacing": 1.0,  # Less space between columns
    }
    
    if dark_mode:
        legend_kwargs.update({
            "facecolor": bg_color,
            "edgecolor": "white",
            "labelcolor": "white"
        })
    
    ax.legend(new_handles, new_labels, **legend_kwargs)

    # Save plot
    output_filename = os.path.join(output_dir, "oegk_bearbeitungszeit_combined_dark.png" if dark_mode else "oegk_bearbeitungszeit_combined.png")
    save_plot(fig, output_filename, dark_mode, bg_color)

def create_grid_processing_time_plot(df_2023, df_historical, df_beilage6, dark_mode=True):
    """Create a 3x3 grid of subplots showing processing times for all Bundesländer."""
    # Create output directory
    output_dir = BASE_OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)

    # Prepare data
    df_2023["Date"] = pd.to_datetime(df_2023["Date"])
    df_historical["Date"] = pd.to_datetime(df_historical["Date"])
    df_beilage6["Date"] = pd.to_datetime(df_beilage6["Date"])

    # Combine the data
    overlap_start = df_2023["Date"].min()
    df_combined = pd.concat([
        df_historical[df_historical["Date"] < overlap_start],
        df_2023,
        df_beilage6[df_beilage6["Date"] > df_2023["Date"].max()]
    ]).sort_values(["Date", "Bundesland_pretty"])

    # Create figure with subplots
    fig = plt.figure(figsize=(24, 16))  # Slightly reduced height
    gs = fig.add_gridspec(3, 3, hspace=0.35, wspace=0.15, bottom=0.05)  # Added bottom margin control
    axes = gs.subplots()

    # Setup style
    text_color, bg_color, grid_alpha = setup_plot_style(dark_mode)
    fig.patch.set_facecolor(bg_color)

    # Get dates for x-axis
    dates = df_combined["Date"].unique()
    german_dates = [translate_to_german_date(d) for d in dates]
    
    # Create labels for every third month
    date_labels = []
    for i, date in enumerate(german_dates):
        if i % 3 == 0:
            date_labels.append(date)
        else:
            date_labels.append("")

    # Get unique Bundesländer
    bundeslaender = sorted(df_combined["Bundesland_pretty"].unique())

    # Setup modern color palette
    if dark_mode:
        postal_color = '#00A6FB'      # Bright blue
        online_color = '#51D88A'      # Bright green
        online_new_color = '#FB6107'  # Bright orange
    else:
        postal_color = '#1E88E5'      # Material blue
        online_color = '#43A047'      # Material green
        online_new_color = '#E65100'  # Material orange

    # Calculate global y-axis limits
    y_min = float('inf')
    y_max = float('-inf')
    
    for bundesland in bundeslaender:
        bl_data = df_combined[df_combined["Bundesland_pretty"] == bundesland].sort_values("Date")
        bl_data_aligned = pd.DataFrame(index=dates)
        bl_data_aligned = bl_data_aligned.join(bl_data.set_index("Date"))
        
        current_min = min(bl_data_aligned[["Postal", "OnlineMeine", "OnlineWAH"]].min().min(), 0)
        current_max = bl_data_aligned[["Postal", "OnlineMeine", "OnlineWAH"]].max().max()
        
        y_min = min(y_min, current_min)
        y_max = max(y_max, current_max)
    
    y_min = y_min * 0.95
    y_max = y_max * 1.05

    for idx, bundesland in enumerate(bundeslaender):
        row = idx // 3
        col = idx % 3
        ax = axes[row, col]
        
        # Set background and style
        ax.set_facecolor(plt.rcParams['axes.facecolor'])
        
        # Add subtle box around plot
        for spine in ax.spines.values():
            if dark_mode:
                spine.set_color(text_color)
                spine.set_alpha(0.2)
            else:
                spine.set_color('#CCCCCC')
            spine.set_linewidth(0.8)

        # Filter and align data
        bl_data = df_combined[df_combined["Bundesland_pretty"] == bundesland].sort_values("Date")
        bl_data_aligned = pd.DataFrame(index=dates)
        bl_data_aligned = bl_data_aligned.join(bl_data.set_index("Date"))
        
        # Plot lines with enhanced styling
        ax.plot(range(len(dates)), bl_data_aligned["Postal"], 
                color=postal_color, marker='o', markersize=4, 
                label="Postal", linewidth=2, linestyle='-',
                alpha=0.9)

        ax.plot(range(len(dates)), bl_data_aligned["OnlineMeine"], 
                color=online_color, marker='o', markersize=4, 
                label="MeineÖGK", linewidth=2, linestyle='--',
                alpha=0.9)

        mask_new_online = ~bl_data_aligned["OnlineWAH"].isna()
        if mask_new_online.any():
            dates_idx = np.where(mask_new_online)[0]
            ax.plot(dates_idx, bl_data_aligned[mask_new_online]["OnlineWAH"], 
                    color=online_new_color, marker='o', markersize=4, 
                    label="WAH", linewidth=2, linestyle=':',
                    alpha=0.9)

        # Enhanced title and labels
        ax.set_title(bundesland, fontsize=14, pad=15, color=text_color, fontweight='bold')
        
        if col == 0:
            ax.set_ylabel("Bearbeitungszeit (Tage)", fontsize=12, color=text_color, labelpad=10)

        # Improved x-axis styling
        ax.set_xticks(range(len(dates)))
        ax.set_xticklabels(date_labels, rotation=45, ha='right', color=text_color, fontsize=9)
        
        # Enhanced grid
        ax.grid(True, axis='y', linestyle="--", alpha=grid_alpha, color=text_color)
        
        for i in range(len(dates)):
            if i % 3 == 0:
                ax.axvline(x=i, color=text_color, linestyle='-', alpha=grid_alpha*1.2, linewidth=1.0)
            else:
                ax.axvline(x=i, color=text_color, linestyle='--', alpha=grid_alpha*0.6, linewidth=0.5)

        ax.set_ylim(y_min, y_max)

        # Enhanced tick labels
        for label in ax.get_xticklabels():
            pos = int(label.get_position()[0])
            if pos % 3 == 0:
                label.set_fontweight('bold')
            else:
                label.set_visible(False)

    # Enhanced legend
    legend_kwargs = {
        "ncol": 3,
        "loc": "center",
        "bbox_to_anchor": (0.5, -0.02),  # Moved legend much closer to plots
        "fontsize": 12,
        "handlelength": 2,
        "borderaxespad": 0,
        "frameon": True,
        "edgecolor": 'none',
        "facecolor": plt.rcParams['axes.facecolor'],
        "labelcolor": text_color,
        "columnspacing": 2.0,
        "handletextpad": 0.8,
    }
    
    fig.legend(*ax.get_legend_handles_labels(), **legend_kwargs)

    # Enhanced main title
    fig.suptitle(
        "ÖGK Durchschnittliche Bearbeitungszeit pro Monat - Alle Bundesländer",
        fontsize=18,
        color=text_color,
        y=0.98,  # Adjusted title position
        fontweight='bold'
    )

    # Save plot with enhanced layout
    output_filename = os.path.join(output_dir, "oegk_bearbeitungszeit_grid_dark.png" if dark_mode else "oegk_bearbeitungszeit_grid.png")
    plt.tight_layout(rect=[0, 0.02, 1, 0.98])  # Adjusted layout to leave space for legend and title
    save_plot(fig, output_filename, dark_mode, bg_color)

def main():
    # Read the CSV files with absolute paths
    df_2023 = pd.read_csv(
        "../data/csv/07_OEGK_Durchschnittliche_Bearbeitungszeit_pro_Monat_2023_postal_online_online_pro_Bundesland.csv"
    )
    df_historical = pd.read_csv(
        "../data/csv/07a_OEGK_Durchschnittliche_Bearbeitungszeit_pro_Monat_2021_bis_Mai_2023_postal_online_online_pro_Bundesland.csv"
    )
    # Read Beilage_5 and Beilage_6 data
    # Process Excel files by skipping first column and first 5 rows,
    # then taking 14 rows (including header), then skipping 5 rows, etc.
    def process_excel_file(file_path, sheet_name=0):
        # Read all data first
        df_raw = pd.read_excel(file_path, sheet_name=sheet_name, header=None)

        # Drop the first column
        df_raw = df_raw.iloc[:, 1:]

        # Initialize empty list to store chunks
        chunks = []

        # Start from row 5 (skipping first 5 rows)
        row_idx = 6

        # Process in chunks: take 14 rows, skip 5 rows
        while row_idx < len(df_raw):
            # Check if we have enough rows left
            end_idx = min(row_idx + 13, len(df_raw))

            # Extract chunk with header in first row
            chunk = df_raw.iloc[row_idx:end_idx].copy()

            # Set the first row as header
            header = chunk.iloc[0]
            chunk = chunk.iloc[1:]
            # Convert rows that end with "KT" to integers
            for i in range(len(chunk)):
                for col in chunk.columns:
                    if isinstance(chunk.iloc[i, chunk.columns.get_loc(col)], str) and chunk.iloc[i, chunk.columns.get_loc(col)].endswith(" KT"):
                        # Extract the numeric part and convert to int
                        value_str = chunk.iloc[i, chunk.columns.get_loc(col)].rstrip(" KT").strip()
                        try:
                            chunk.iloc[i, chunk.columns.get_loc(col)] = int(value_str)
                        except ValueError:
                            # If conversion fails, keep the original value
                            pass
            chunk.columns = header

            # Add to chunks list
            chunks.append(chunk)

            # Move to next chunk (skip 5 rows after the 14 we just processed)
            row_idx = end_idx + 7

        # Combine all chunks
        if chunks:
            df = pd.concat(chunks, ignore_index=True)
            # Convert numeric columns to numeric type
            numeric_columns = ["postalische KE", "online KE\nMeineÖGK", "online KE\nWAHonline"]
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col].replace("-", pd.NA), errors='coerce')
            return df
        else:
            return pd.DataFrame()

    # Process the Excel files
    df_beilage5 = process_excel_file("../raw_data/2025_Anfrage/Beilage_5.xlsx")
    df_beilage6 = process_excel_file("../raw_data/2025_Anfrage/Beilage_6.xlsx", sheet_name="F3_2024")

    # Print column names to debug
    print("2023 columns:", df_2023.columns.tolist())
    print("Historical columns:", df_historical.columns.tolist())
    print("Beilage 5 columns:", df_beilage5.columns.tolist())
    print("Beilage 6 columns:", df_beilage6.columns.tolist())

    # Verify data consistency between Beilage_5 and existing data
    # First, convert dates to datetime for comparison
    df_2023["Date"] = pd.to_datetime(df_2023["Date"])
    df_historical["Date"] = pd.to_datetime(df_historical["Date"])

    # Convert dates in processed files
    df_beilage5["Date"] = pd.to_datetime(df_beilage5["Monat"])
    df_beilage6["Date"] = pd.to_datetime(df_beilage6["Monat"])

    df_beilage5 = df_beilage5.rename(
        columns={
            "postalische KE": "Postal",
            "online KE\nMeineÖGK": "OnlineMeine",
            "online KE\nWAHonline": "OnlineWAH",
        }
    )
    df_beilage6 = df_beilage6.rename(
        columns={
            "postalische KE": "Postal",
            "online KE\nMeineÖGK": "OnlineMeine",
            "online KE\nWAHonline": "OnlineWAH"
        }
    )

    df_beilage5["Bundesland_pretty"] = df_beilage5["ÖGK-LS"].apply(prettify_bundesland)
    df_beilage6["Bundesland_pretty"] = df_beilage6["ÖGK-LS"].apply(prettify_bundesland)

    # Ensure numeric columns are numeric type
    numeric_columns = ["Postal", "OnlineMeine", "OnlineWAH"]
    for df in [df_2023, df_historical, df_beilage5, df_beilage6]:
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].replace("-", pd.NA), errors='coerce')

    # Find overlapping dates between Beilage_5 and existing data
    overlap_start = df_2023["Date"].min()
    overlap_end = df_2023["Date"].max()

    # Filter overlapping data
    df_2023_overlap = df_2023[(df_2023["Date"] >= overlap_start) & (df_2023["Date"] <= overlap_end)]
    df_beilage5_overlap = df_beilage5[(df_beilage5["Date"] >= overlap_start) & (df_beilage5["Date"] <= overlap_end)]

    # Compare values for overlapping dates
    for date in df_2023_overlap["Date"].unique():
        df_2023_date = df_2023_overlap[df_2023_overlap["Date"] == date]
        df_beilage5_date = df_beilage5_overlap[df_beilage5_overlap["Date"] == date]

        # Compare postal and online values
        postal_2023 = df_2023_date["Postal"].sum()
        online_2023 = df_2023_date["OnlineMeine"].sum()
        online_2023_wah = df_2023_date["OnlineWAH"].sum()
        postal_5 = df_beilage5_date["Postal"].sum()
        online_5 = df_beilage5_date["OnlineMeine"].sum()
        online_5_wah = df_beilage5_date["OnlineWAH"].sum()

        # Assert values match
        assert abs(postal_2023 - postal_5) < 1e-10, f"Postal values don't match for date {date}"
        assert abs(online_2023 - online_5) < 1e-10, f"Online values don't match for date {date}"
        assert abs(online_2023_wah - online_5_wah) < 1e-10, f"Online WAH values don't match for date {date}"

    print("Data consistency check passed: Beilage_5 matches existing data")

    # Create grid plots first
    print("Creating grid plots...")
    create_grid_processing_time_plot(df_2023, df_historical, df_beilage6, dark_mode=True)
    create_grid_processing_time_plot(df_2023, df_historical, df_beilage6, dark_mode=False)

    # Create combined plots
    print("Creating combined plots...")
    create_combined_processing_time_plot(df_2023, df_historical, df_beilage6, dark_mode=True)
    create_combined_processing_time_plot(df_2023, df_historical, df_beilage6, dark_mode=False)

    # Get unique Bundesländer
    bundeslaender = df_2023["Bundesland_pretty"].unique()

    # Create individual plots for each Bundesland
    for bundesland in bundeslaender:
        print(f"Creating plots for {bundesland}...")

        # Create plots in both dark and light mode
        create_processing_time_plot(df_2023, df_historical, df_beilage6, bundesland, dark_mode=True)
        create_processing_time_plot(df_2023, df_historical, df_beilage6, bundesland, dark_mode=False)

if __name__ == "__main__":
    main() 
