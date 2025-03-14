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

def create_processing_time_plot(df_2023, df_historical, bundesland, dark_mode=True):
    """Create a line plot showing processing times for postal and online submissions."""
    # Get output directory for this Bundesland
    output_dir = get_bundesland_output_dir(bundesland)
    os.makedirs(output_dir, exist_ok=True)

    # Filter data for the specific Bundesland
    df_2023_bl = df_2023[df_2023["Bundesland_pretty"] == bundesland].copy()
    df_hist_bl = df_historical[df_historical["Bundesland_pretty"] == bundesland].copy()

    # Merge the dataframes
    df_2023_bl["Date"] = pd.to_datetime(df_2023_bl["Date"])
    df_hist_bl["Date"] = pd.to_datetime(df_hist_bl["Date"])

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
        df_2023_bl
    ]).sort_values("Date")

    # Create figure
    fig, ax = plt.subplots(figsize=(15, 8))

    # Setup style
    text_color, bg_color, grid_alpha = setup_plot_style(dark_mode)
    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)

    # Get dates for x-axis
    dates = df_combined["Date"].unique()

    # Setup colors
    base_colors = create_base_colors()[0]  # Use first color set
    postal_color = base_colors[0]
    online_color = base_colors[1]
    online_new_color = base_colors[2]

    # Plot lines with dots
    # Postal
    ax.plot(range(len(dates)), df_combined["Postal"], 
            color=postal_color, marker='o', markersize=4, 
            label="Postal", linewidth=2, linestyle='-')

    # Online (MeineÖGK)
    ax.plot(range(len(dates)), df_combined["OnlineMeine"], 
            color=online_color, marker='o', markersize=4, 
            label="Online (MeineÖGK)", linewidth=2, linestyle='--')

    # Online (WAH) - only after May 2023
    mask_new_online = ~df_combined["OnlineWAH"].isna()
    if mask_new_online.any():
        dates_idx = np.where(mask_new_online)[0]
        ax.plot(dates_idx, df_combined[mask_new_online]["OnlineWAH"], 
                color=online_new_color, marker='o', markersize=4, 
                label="Online (WAH)", linewidth=2, linestyle=':')

    # Customize plot
    plt.title(
        f"ÖGK Durchschnittliche Bearbeitungszeit pro Monat - {bundesland}",
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

    # Add legend
    setup_legend(ax, dark_mode, bg_color, text_color)

    # Save plot
    output_filename = os.path.join(output_dir, "oegk_bearbeitungszeit_dark.png" if dark_mode else "oegk_bearbeitungszeit.png")
    save_plot(fig, output_filename, dark_mode, bg_color)

def create_combined_processing_time_plot(df_2023, df_historical, dark_mode=True):
    """Create a line plot showing processing times for all Bundesländer together."""
    # Create output directory
    output_dir = BASE_OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)

    # Prepare data
    df_2023["Date"] = pd.to_datetime(df_2023["Date"])
    df_historical["Date"] = pd.to_datetime(df_historical["Date"])

    # Combine the data
    overlap_start = df_2023["Date"].min()
    df_combined = pd.concat([
        df_historical[df_historical["Date"] < overlap_start],
        df_2023
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

def create_grid_processing_time_plot(df_2023, df_historical, dark_mode=True):
    """Create a 3x3 grid of subplots showing processing times for all Bundesländer."""
    # Create output directory
    output_dir = BASE_OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)

    # Prepare data
    df_2023["Date"] = pd.to_datetime(df_2023["Date"])
    df_historical["Date"] = pd.to_datetime(df_historical["Date"])

    # Combine the data
    overlap_start = df_2023["Date"].min()
    df_combined = pd.concat([
        df_historical[df_historical["Date"] < overlap_start],
        df_2023
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
        "D:/DEV/WU/WARRA/data/csv/07_OEGK_Durchschnittliche_Bearbeitungszeit_pro_Monat_2023_postal_online_online_pro_Bundesland.csv"
    )
    df_historical = pd.read_csv(
        "D:/DEV/WU/WARRA/data/csv/07a_OEGK_Durchschnittliche_Bearbeitungszeit_pro_Monat_2021_bis_Mai_2023_postal_online_online_pro_Bundesland.csv"
    )
    
    # Print column names to debug
    print("2023 columns:", df_2023.columns.tolist())
    print("Historical columns:", df_historical.columns.tolist())
    
    # Create grid plots first
    print("Creating grid plots...")
    create_grid_processing_time_plot(df_2023, df_historical, dark_mode=True)
    create_grid_processing_time_plot(df_2023, df_historical, dark_mode=False)
    
    # Create combined plots
    print("Creating combined plots...")
    create_combined_processing_time_plot(df_2023, df_historical, dark_mode=True)
    create_combined_processing_time_plot(df_2023, df_historical, dark_mode=False)
    
    # Get unique Bundesländer
    bundeslaender = df_2023["Bundesland_pretty"].unique()
    
    # Create individual plots for each Bundesland
    for bundesland in bundeslaender:
        print(f"Creating plots for {bundesland}...")
        
        # Create plots in both dark and light mode
        create_processing_time_plot(df_2023, df_historical, bundesland, dark_mode=True)
        create_processing_time_plot(df_2023, df_historical, bundesland, dark_mode=False)

if __name__ == "__main__":
    main() 