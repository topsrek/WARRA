import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import matplotlib.patches as patches

# Output directory for the visualization
OUTPUT_DIR = "../figures/Insurance_Comparison"

# Dictionary to prettify insurance provider names
prettify_insurance = {
    "BVAEB": "BVAEB-Bundesweit",
    "ÖGK": "ÖGK-Bundesweit",
    "SVS": "SVS-Bundesweit",
}


def create_plot(bvaeb_file, oegk_file, svs_file, dark_mode=True):
    """
    Creates a visualization comparing refund ratios across insurance providers by year.
    
    Args:
        bvaeb_file: Path to BVAEB CSV data file
        oegk_file: Path to ÖGK CSV data file
        svs_file: Path to SVS CSV data file
        dark_mode: Whether to use dark mode styling
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Load data from each insurance provider
    # BVAEB data
    bvaeb_df = pd.read_csv(bvaeb_file)
    bvaeb_df = bvaeb_df[bvaeb_df["Bundesland"] == "Gesamt"].copy()
    bvaeb_df["Ratio"] = bvaeb_df["Refundierungen"] / bvaeb_df["Rechnungsbeträge"]
    bvaeb_df["Insurance"] = "BVAEB"
    # Convert Year to string to ensure consistent type
    bvaeb_df["Year"] = bvaeb_df["Year"].astype(str)

    # ÖGK data
    oegk_df = pd.read_csv(oegk_file)
    oegk_df = oegk_df[oegk_df["LST"] == "Gesamt"].copy()
    oegk_df["Ratio"] = oegk_df["Refundierungen"] / oegk_df["Rechnungsbeträge"]
    oegk_df["Insurance"] = "ÖGK"
    # Convert Year to string to ensure consistent type
    oegk_df["Year"] = oegk_df["Year"].astype(str)

    # SVS data
    svs_df = pd.read_csv(svs_file)
    svs_df = svs_df[svs_df["Bundesland"] == "Gesamt"].copy()
    svs_df["Ratio"] = svs_df["Refundierungen"] / svs_df["Rechnungsbeträge"]
    svs_df["Insurance"] = "SVS"
    # Convert Year to string to ensure consistent type
    svs_df["Year"] = svs_df["Year"].astype(str)

    # Combine all data
    combined_df = pd.concat([bvaeb_df, oegk_df, svs_df], ignore_index=True)

    # Initialize figure with landscape format for better comparison
    fig, ax = plt.subplots(figsize=(12, 12))

    # Apply theme based on dark_mode setting
    if dark_mode:
        plt.style.use("dark_background")
        fig.patch.set_facecolor("#1a1a1a")
        ax.set_facecolor("#1a1a1a")
        box_edge_color = "white"
        box_face_color = "#333333"
    else:
        plt.style.use("default")
        fig.patch.set_facecolor("white")
        ax.set_facecolor("white")
        box_edge_color = "black"
        box_face_color = "#f0f0f0"

    # Prepare data organization - sort years in a way that handles strings properly
    # Custom sorting function to handle years with Q1-Q3 suffix
    def year_sort_key(year_str):
        if "Q1-Q3" in year_str:
            # Extract the year part and add .75 to place Q1-Q3 between years
            return float(year_str.split("Q")[0]) + 0.75
        else:
            # Regular years are just converted to float
            return float(year_str)

    # Get unique years and sort them
    all_years = combined_df["Year"].unique()
    years = sorted(all_years, key=year_sort_key, reverse=False)

    # Reorder insurances to put BVAEB in the middle
    insurances = ["ÖGK", "BVAEB", "SVS"]

    # Calculate positions for visualization
    total_entities = len(insurances)
    total_positions = total_entities * len(years)
    y_positions = np.arange(total_positions)

    # Generate year labels for y-axis
    y_labels = []
    for insurance in insurances:
        for year in years:
            # Skip 2024 for SVS as it doesn't have data
            if insurance == "SVS" and "2024" in str(year):
                y_labels.append("")
            else:
                y_labels.append(f"{year}")

    # Prepare insurance labels and their positions
    insurance_labels = [prettify_insurance[ins] for ins in insurances]
    insurance_positions = [
        len(years) / 2 - 0.5 + i * len(years) for i in range(len(insurances))
    ]

    # Create alternating background for better readability
    for i in range(total_entities):
        y_start = i * len(years)
        y_end = (i + 1) * len(years)
        if i % 2 == 1:
            if dark_mode:
                ax.axhspan(y_start - 0.5, y_end - 0.5, color="#2a2a2a", alpha=0.8)
            else:
                ax.axhspan(y_start - 0.5, y_end - 0.5, color="#e0e0e0", alpha=0.9)

    # Plot data points
    colors = {"BVAEB": "blue", "ÖGK": "green", "SVS": "purple"}

    for i, insurance in enumerate(insurances):
        insurance_data = combined_df[combined_df["Insurance"] == insurance]
        for j, year in enumerate(years):
            year_data = insurance_data[insurance_data["Year"] == year]
            if not year_data.empty:
                ratio = year_data["Ratio"].iloc[0]
                y_pos = i * len(years) + j

                # Plot the insurance's data point
                ax.plot(
                    ratio, 
                    y_pos, 
                    "D", 
                    color=colors[insurance], 
                    markersize=18, 
                    zorder=2,
                    label=f"{insurance} {year}" if j == 0 else ""
                )

                # Add text label with percentage in a box
                label_text = f"{ratio:.1%}"
                text_x = ratio + 0.02 #if i != 1 else ratio - 0.02

                # Create text object to get its dimensions
                text = ax.text(
                    text_x, 
                    y_pos, 
                    label_text, 
                    fontsize=16, 
                    color="white" if dark_mode else "black",
                    verticalalignment="center",
                    horizontalalignment="center",
                    zorder=4
                )

                # Get text dimensions to create box
                bbox = text.get_window_extent(renderer=fig.canvas.get_renderer())
                bbox = bbox.transformed(ax.transData.inverted())

                # Create a fixed-size box with proper proportions
                box_width = 0.015  # Fixed width
                box_height = 0.5  # Fixed height

                # Center the box on the text
                box_x = text_x - box_width/2
                box_y = y_pos - box_height/2

                # Create box around text with rounded corners
                rect = patches.FancyBboxPatch(
                    (box_x, box_y), 
                    box_width, 
                    box_height, 
                    boxstyle=patches.BoxStyle("Round", pad=0.002, rounding_size=0),
                    linewidth=1, 
                    edgecolor=box_edge_color, 
                    facecolor=box_face_color,
                    alpha=0.8,
                    zorder=3
                )
                ax.add_patch(rect)

                # Bring text to front
                text.set_zorder(5)

    # Style and formatting
    text_color = "white" if dark_mode else "black"

    # Set title and labels - move title higher
    plt.suptitle(
        "Wahlarzt Refundierungsquote im Vergleich (Bundesweit)",
        fontsize=25,
        y=0.97,  # Moved up from 0.95
        color=text_color,
    )
    ax.set_xlabel(
        "Verhältnis (Refundierungen / Rechnungsbeträge)", fontsize=20, color=text_color
    )

    # Configure y-axis (years)
    ax.set_yticks(y_positions)
    ax.set_yticklabels(y_labels, color=text_color, fontsize=16)

    # Configure x-axis (ratio values)
    # Find min and max values to set appropriate range
    min_ratio = combined_df["Ratio"].min() * 0.95  # Add 5% padding
    max_ratio = combined_df["Ratio"].max() * 1.1  # Add 5% padding

    # Round to nice values
    # min_ratio = np.floor(min_ratio * 20) / 20  # Round down to nearest 0.05
    # max_ratio = np.ceil(max_ratio * 20) / 20   # Round up to nearest 0.05

    ax.set_ylim(-0.5, total_positions - 0.5)
    # ax.set_xlim(min_ratio, max_ratio)
    ax.set_xlim(0.33, 0.60)

    # Create nice tick spacing
    x_ticks = np.arange(min_ratio, max_ratio, 0.04)
    ax.set_xticks(x_ticks)
    ax.set_xticklabels([f"{x:.1%}" for x in x_ticks], color=text_color, fontsize=16)

    # Add duplicate x-axis at the top for better readability
    ax2 = ax.twiny()
    ax2.set_xlim(ax.get_xlim())
    ax2.set_xticks(x_ticks)
    ax2.set_xticklabels([f"{x:.1%}" for x in x_ticks], color=text_color, fontsize=16)

    # Add insurance provider labels - moved further left
    for i in range(len(insurances)):
        y_pos = insurance_positions[i]
        label = insurance_labels[i]
        # Split the label into name and "Bundesweit"
        name = label.split("-")[0]
        # Calculate x position in the middle of the data range
        x_pos = (min_ratio + max_ratio) / 2
        # Add the name
        ax.text(
            x_pos,  # Center horizontally in the data range
            y_pos,
            name,
            fontsize=48,  # Increased font size further
            fontweight="bold",
            color=text_color,
            alpha=0.7,  # Add transparency
            verticalalignment="center",
            horizontalalignment="center",
            zorder=1,
        )
        # Add "Bundesweit" underneath
        ax.text(
            x_pos,  # Center horizontally in the data range
            y_pos + 0.8,  # Move down more to be below the insurance name (positive value since y-axis is inverted)
            "Bundesweit",
            fontsize=24,  # Reduced font size
            color=text_color,
            alpha=0.7,  # Add transparency
            verticalalignment="center",
            horizontalalignment="center",
            zorder=1,
        )

    # Add grid
    grid_alpha = 0.2 if dark_mode else 0.7
    ax.grid(True, axis="x", linestyle="--", alpha=grid_alpha, color=text_color)
    ax.grid(True, axis="y", linestyle="--", alpha=grid_alpha, color=text_color)

    # Add legend for insurance providers
    legend_elements = [
        plt.Line2D(
            [0], [0], marker="D", color="w", markerfacecolor="green", markersize=17, label="ÖGK"
        ),
        plt.Line2D(
            [0], [0], marker="D", color="w", markerfacecolor="blue", markersize=17, label="BVAEB"
        ),
        plt.Line2D(
            [0], [0], marker="D", color="w", markerfacecolor="purple", markersize=17, label="SVS"
        ),
    ]
    ax.legend(handles=legend_elements, loc="lower right", fontsize=17)

    # Reverse y-axis for chronological order
    ax.invert_yaxis()

    # Configure output filename
    filename = os.path.join(
        OUTPUT_DIR,
        f"insurance_comparison_ratio_{'dark' if dark_mode else 'light'}.png",
    )

    # Configure save parameters
    save_kwargs = {"dpi": 300, "bbox_inches": "tight"}
    if dark_mode:
        save_kwargs.update({"facecolor": "#1a1a1a", "edgecolor": "none"})
    else:
        save_kwargs.update({"facecolor": "white", "edgecolor": "none"})

    # Adjust layout
    plt.tight_layout()
    plt.subplots_adjust(top=0.88)  # Adjusted to make room for higher title
    plt.subplots_adjust(left=0.05)  # Increased from 0.15 to make room for labels

    # Add background elements in figure coordinates
    # Background rectangles for odd-numbered insurances
    for i in range(len(insurances)):
        if i % 2 == 1:
            y_pos = insurance_positions[i]
            y_start = (
                ax.get_position().y0
                + (total_positions - (y_pos + len(years) / 2) - 0.5)
                / total_positions
                * ax.get_position().height
            )
            height = len(years) / total_positions * ax.get_position().height

            rect = plt.Rectangle(
                (0.05, y_start),
                0.8,
                height,
                facecolor="#2a2a2a" if dark_mode else "#e0e0e0",
                alpha=1.0,
                transform=fig.transFigure,
                zorder=-2,
            )
            fig.patches.append(rect)

    # Add separator lines between insurance providers
    for i in range(total_entities + 1):
        y_pos = i * len(years) - 0.5
        fig_y = (
            ax.get_position().y0
            + (total_positions - y_pos - 0.5)
            / total_positions
            * ax.get_position().height
        )
        line = plt.Line2D(
            [0.05, 0.987],
            [fig_y, fig_y],
            transform=fig.transFigure,
            color=text_color,
            alpha=1.0,
            linewidth=1,
            zorder=100,
        )
        fig.lines.append(line)

    plt.savefig(filename, **save_kwargs)
    plt.close()


def main():
    """Generate plots in both dark and light mode comparing insurance providers."""
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Generate dark mode plot
    create_plot(
        "../data/csv/manually_extracted/BVAEB_Betraege_updated.csv",
        "../data/csv/manually_extracted/OEGK_Betraege_updated2025.csv",
        "../data/csv/manually_extracted/SVS_Betraege_updated.csv",
        dark_mode=True,
    )
    
    # Generate light mode plot
    create_plot(
        "../data/csv/manually_extracted/BVAEB_Betraege_updated.csv",
        "../data/csv/manually_extracted/OEGK_Betraege_updated2025.csv",
        "../data/csv/manually_extracted/SVS_Betraege_updated.csv",
        dark_mode=False,
    )


if __name__ == "__main__":
    main() 

