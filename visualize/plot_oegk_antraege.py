import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
import os
import math

# Global settings
OUTPUT_DIR = "../figures/OEGK/Antraege"  # Output directory for the plot

# Number of groups to create
NUM_GROUPS = 4

def create_base_colors():
    """Create distinct color pairs for postal and online submissions."""
    base_colors = [
        # Primary colors with high contrast
        ("#1f77b4", "#7cc7ff"),  # Blue
        ("#ff7f0e", "#ffb74d"),  # Orange
        ("#2ca02c", "#98df8a"),  # Green
        ("#d62728", "#ff9896"),  # Red
        
        # Secondary vibrant colors
        ("#9467bd", "#c5b0d5"),  # Purple
        ("#8c564b", "#d4a792"),  # Brown
        ("#e6b417", "#ffe169"),  # Yellow
        ("#17becf", "#9edae5"),  # Turquoise
        
        # Additional vibrant colors
        ("#7f7f7f", "#c7c7c7"),  # Gray
        ("#bcbd22", "#dbdb8d"),  # Olive
        ("#434348", "#8c8c96"),  # Charcoal
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

def prepare_dataframe(df):
    """Prepare and clean the DataFrame for plotting."""
    # Get January 2023 data for FG-Code to Fachrichtung mapping
    jan_df = df[(df["Monat.Jahr"] == "Jän.23") & (df["Fachrichtung"] != "Gesamt")]
    fg_mapping = dict(zip(jan_df["FG-Code"].dropna(), jan_df["Fachrichtung"].dropna()))
    
    # Filter out the 'Gesamt' rows and create a copy to avoid the warning
    df = df[df["Fachrichtung"] != "Gesamt"].copy()
    
    # Convert Date to datetime and sort
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values(["Date", "FG-Code"])
    
    return df, fg_mapping

def create_stacked_plot(df, dark_mode=True, output_filename=None):
    """Create the original stacked bar plot."""
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Prepare the DataFrame
    df, fg_mapping = prepare_dataframe(df)

    # Create figure
    fig, ax = plt.subplots(figsize=(20, 30))

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

        postal_values = fg_data["postal"].fillna(0).values
        online_values = fg_data["online"].fillna(0).values
        total_values = postal_values + online_values

        assert total_values.sum() == fg_data["Gesamt"].sum(), f"FG-Code {fg} - Total values don't match"

        for j in range(len(dates)):
            total = total_values[j]
            if total > 0:
                postal_ratio = postal_values[j] / total
                online_ratio = online_values[j] / total
                assert postal_ratio + online_ratio == 1, f"FG-Code {fg} - Postal and online ratios don't add up to 1 for date {dates[j]}"
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
        "ÖGK Anträge nach Fachrichtung pro Monat (Postal/Online Aufteilung)", 
        fontsize=16, 
        pad=30,  # Increased padding
        color=text_color
    )
    plt.xlabel("Monat", fontsize=12, color=text_color, labelpad=15)  # Increased labelpad
    plt.ylabel("Anzahl der Anträge", fontsize=12, labelpad=15, color=text_color)  # Increased labelpad

    # Translate month names to German
    german_dates = []
    for d in dates:
        month_str = d.strftime("%b %Y")
        month_str = (
            month_str.replace("Jan", "Jän")
            .replace("Apr", "Apr")
            .replace("May", "Mai")
            .replace("Jun", "Jun")
            .replace("Jul", "Jul")
            .replace("Aug", "Aug")
            .replace("Sep", "Sep")
            .replace("Oct", "Okt")
            .replace("Dec", "Dez")
        )
        german_dates.append(month_str)

    #ax.set_xticklabels(german_dates, rotation=45, color=text_color)
    plt.xticks(range(len(dates)), german_dates, rotation=45, color=text_color)
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
    # plt.tight_layout()

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

def get_colors_for_group(base_colors, fg_codes, start_color_idx=0):
    """Get colors for a group starting from a specific index."""
    needed_colors = len(fg_codes)
    
    # Extend base colors if needed
    while len(base_colors) < start_color_idx + needed_colors:
        base_colors.extend(base_colors)
    
    # Get color slices
    postal_colors = [pair[0] for pair in base_colors[start_color_idx : start_color_idx + needed_colors]]
    online_colors = [pair[1] for pair in base_colors[start_color_idx : start_color_idx + needed_colors]]
    
    return postal_colors, online_colors, start_color_idx + needed_colors

def create_ranked_grouped_plot(df, dark_mode=True):
    """Create a plot with four subplots based on rank-based grouping."""
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Prepare the DataFrame
    df, fg_mapping = prepare_dataframe(df)
    
    # Calculate yearly average applications per Fachrichtung
    yearly_avg = df.groupby("Fachrichtung")["Gesamt"].mean()
    yearly_avg = yearly_avg.sort_values(ascending=False)  # Sort by yearly average in descending order
    
    # Calculate cumulative percentage based on yearly averages
    total_sum = yearly_avg.sum()
    cumsum_percentage = yearly_avg.cumsum() / total_sum * 100
    
    # Group cutoff percentages
    TOP_GROUP_CUTOFF = 89  # Top group includes Fachrichtungen responsible for up to 75% of total applications
    BOTTOM_GROUP_CUTOFF = 99  # Bottom group includes Fachrichtungen responsible for the last 3% of total applications

    # Group Fachrichtungen based on cumulative percentage
    group1_mask = cumsum_percentage <= TOP_GROUP_CUTOFF
    group2_mask = (cumsum_percentage > TOP_GROUP_CUTOFF)  & (cumsum_percentage <= BOTTOM_GROUP_CUTOFF)
    group3_mask = cumsum_percentage > BOTTOM_GROUP_CUTOFF
    
    group1_fgs = yearly_avg[group1_mask].index
    group2_fgs = yearly_avg[group2_mask].index
    group3_fgs = yearly_avg[group3_mask].index
    
    # Print group statistics for debugging
    print(f"\nGroup Statistics (based on yearly averages):")
    print(f"Group 1 (0-75%): {len(group1_fgs)} Fachrichtungen")
    print(f"Group 2 (50-75%): {len(group2_fgs)} Fachrichtungen")
    print(f"Group 3 (25-50%): {len(group3_fgs)} Fachrichtungen")
    
    # Print the Fachrichtungen in each group for verification
    print("\nGroup 1 Fachrichtungen (Höchstes Volumen):")
    for fg in group1_fgs:
        print(f"- {fg}")
    print("\nGroup 2 Fachrichtungen (Hohes Volumen):")
    for fg in group2_fgs:
        print(f"- {fg}")
    print("\nGroup 3 Fachrichtungen (Mittleres Volumen):")
    for fg in group3_fgs:
        print(f"- {fg}")
    
    # Create figure with four subplots with increased spacing
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(20, 30))
    fig.subplots_adjust(hspace=0.4)  # Increase space between subplots
    
    # Setup style
    text_color, bg_color, grid_alpha = setup_plot_style(dark_mode)
    fig.patch.set_facecolor(bg_color)
    for ax in [ax1, ax2, ax3]:
        ax.set_facecolor(bg_color)
    
    # Track color index across groups
    color_idx = 0
    
    # Create plots for each group with German titles
    color_idx = create_group_subplot(df, group1_fgs, ax1, f"Gruppe 1: Fachrichtungen mit höchstem Volumen (0-75% der Anträge)", 
                                   text_color, grid_alpha, dark_mode, bg_color, color_idx)
    color_idx = create_group_subplot(df, group2_fgs, ax2, f"Gruppe 2: Fachrichtungen mit hohem Volumen (50-75% der Anträge)", 
                                   text_color, grid_alpha, dark_mode, bg_color, color_idx)
    color_idx = create_group_subplot(df, group3_fgs, ax3, f"Gruppe 3: Fachrichtungen mit mittlerem Volumen (25-50% der Anträge)", 
                                   text_color, grid_alpha, dark_mode, bg_color, color_idx)
    
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

def create_group_subplot(df, fachrichtungen, ax, title, text_color, grid_alpha, dark_mode, bg_color, start_color_idx=0):
    """Create a subplot for a specific group of Fachrichtungen."""
    # Filter data for the group
    group_data = df[df["Fachrichtung"].isin(fachrichtungen)]
    
    # Check if group is empty
    if len(group_data) == 0:
        ax.text(0.5, 0.5, "Keine Daten verfügbar", 
                ha='center', va='center', transform=ax.transAxes, 
                color=text_color, fontsize=12)
        ax.set_title(title, fontsize=14, pad=30, color=text_color)
        return start_color_idx
    
    # Get mapping from the original DataFrame
    _, fg_mapping = prepare_dataframe(df)
    
    # Get unique dates and sort data
    dates = group_data["Date"].unique()
    
    # Calculate yearly average for each FG-Code in this group and sort by it
    yearly_avg = group_data.groupby("FG-Code")["Gesamt"].mean().sort_values(ascending=False)
    fg_codes = yearly_avg.index.dropna().unique()
    
    # Check if we have any valid FG codes
    if len(fg_codes) == 0:
        ax.text(0.5, 0.5, "Keine gültigen Fachrichtungen", 
                ha='center', va='center', transform=ax.transAxes, 
                color=text_color, fontsize=12)
        ax.set_title(title, fontsize=14, pad=30, color=text_color)
        return start_color_idx
    
    # Setup colors with continuation from previous groups
    base_colors = create_base_colors()
    postal_colors, online_colors, next_color_idx = get_colors_for_group(base_colors, fg_codes, start_color_idx)
    
    # Plot stacked bars
    bar_width = 0.8
    bottom = np.zeros(len(dates))
    
    # Calculate total height with safety check
    total_height = group_data.groupby("Date")["Gesamt"].sum().max()
    if pd.isna(total_height) or total_height == 0:
        total_height = 1  # Set a default height if no data
    
    for i, fg in enumerate(fg_codes):
        fg_data = group_data[group_data["FG-Code"] == fg]
        
        postal_values = fg_data["postal"].fillna(0).values
        online_values = fg_data["online"].fillna(0).values
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
    ax.set_title(title, fontsize=14, pad=50, color=text_color)  # Increased padding
    ax.set_xlabel("Monat", fontsize=12, color=text_color, labelpad=15)  # Increased labelpad
    ax.set_ylabel("Anzahl der Anträge", fontsize=12, labelpad=15, color=text_color)  # Increased labelpad
    ax.set_xticks(range(len(dates)))
    
    # Translate month names to German
    german_dates = []
    for d in dates:
        month_str = d.strftime("%b %Y")
        month_str = month_str.replace("Jan", "Jän")\
                            .replace("Apr", "Apr")\
                            .replace("May", "Mai")\
                            .replace("Jun", "Jun")\
                            .replace("Jul", "Jul")\
                            .replace("Aug", "Aug")\
                            .replace("Sep", "Sep")\
                            .replace("Oct", "Okt")\
                            .replace("Dec", "Dez")
        german_dates.append(month_str)
    
    ax.set_xticklabels(german_dates, rotation=45, color=text_color)
    ax.tick_params(colors=text_color)
    
    # Add grid
    ax.grid(True, axis="y", linestyle="--", alpha=grid_alpha, color=text_color)
    
    # Set axis limits with safety check
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
    
    return next_color_idx  # Return the next color index for the next group

def create_balanced_grouped_plot(df, dark_mode=True):
    """Create a plot with four subplots with equal number of Fachrichtungen in each group."""
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Prepare the DataFrame
    df, fg_mapping = prepare_dataframe(df)
    
    # Calculate yearly average applications per Fachrichtung
    yearly_avg = df.groupby("Fachrichtung")["Gesamt"].mean()
    yearly_avg = yearly_avg.sort_values(ascending=False)  # Sort by yearly average in descending order
    
    # Get the total number of Fachrichtungen
    total_fgs = len(yearly_avg)
    
    # Calculate the number of Fachrichtungen per group (rounded up to ensure all are included)
    fgs_per_group = math.floor(total_fgs / NUM_GROUPS)
    
    # Create groups with equal number of Fachrichtungen
    groups = []
    group_names = []
    group_descriptions = []
    
    for i in range(NUM_GROUPS):
        start_idx = i * fgs_per_group
        end_idx = min(start_idx + fgs_per_group, total_fgs)
        
        # Get the Fachrichtungen for this group
        group_fgs = yearly_avg.index[start_idx:end_idx]
        groups.append(group_fgs)
        
        # Create group name and description in German
        if i == 0:
            group_names.append(f"Gruppe {i+1}: Höchstes Volumen")
            group_descriptions.append(f"Fachrichtungen mit höchstem Volumen (Rang {start_idx+1}-{end_idx})")
        elif i == 1:
            group_names.append(f"Gruppe {i+1}: Hohes Volumen")
            group_descriptions.append(f"Fachrichtungen mit hohem Volumen (Rang {start_idx+1}-{end_idx})")
        elif i == 2:
            group_names.append(f"Gruppe {i+1}: Mittleres Volumen")
            group_descriptions.append(f"Fachrichtungen mit mittlerem Volumen (Rang {start_idx+1}-{end_idx})")
        else:  # i == 3
            group_names.append(f"Gruppe {i+1}: Niedriges Volumen")
            group_descriptions.append(f"Fachrichtungen mit niedrigem Volumen (Rang {start_idx+1}-{end_idx})")
    
    # Print group statistics for debugging
    print(f"\nBalanced Group Statistics (based on yearly averages):")
    for i, group in enumerate(groups):
        print(f"{group_names[i]}: {len(group)} Fachrichtungen")
        print(f"- Description: {group_descriptions[i]}")
        
        # Print the Fachrichtungen in this group
        print(f"- Fachrichtungen:")
        for fg in group:
            avg_value = yearly_avg[fg]
            print(f"  - {fg} (Avg: {avg_value:.2f})")
    
    # Create figure with four subplots with increased spacing
    fig, axes = plt.subplots(NUM_GROUPS, 1, figsize=(20, 40))
    fig.subplots_adjust(hspace=0.4)  # Increase space between subplots
    
    # Setup style
    text_color, bg_color, grid_alpha = setup_plot_style(dark_mode)
    fig.patch.set_facecolor(bg_color)
    
    # If there's only one group, make axes iterable
    if NUM_GROUPS == 1:
        axes = [axes]
    
    # Track color index across groups
    color_idx = 0
    
    # Create plots for each group
    for i, (group_fgs, ax) in enumerate(zip(groups, axes)):
        ax.set_facecolor(bg_color)
        color_idx = create_group_subplot(df, group_fgs, ax, group_descriptions[i], 
                                       text_color, grid_alpha, dark_mode, bg_color, color_idx)
    
    plt.tight_layout()
    
    # Save plot
    output_filename = os.path.join(OUTPUT_DIR, "oegk_antraege_balanced_groups_dark.png" if dark_mode else "oegk_antraege_balanced_groups.png")
    
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
    
    # Create balanced grouped plots in both light and dark mode
    create_balanced_grouped_plot(df, dark_mode=True)
    create_balanced_grouped_plot(df, dark_mode=False)

if __name__ == "__main__":
    main()
