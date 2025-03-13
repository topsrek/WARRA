import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Global settings
OUTPUT_DIR = "../figures/OEGK/Betraege"  # Output directory for the plot

# Dictionary to convert abbreviated state names to full names
prettify_LST = {
    "ÖGK-W": "ÖGK-Wien",
    "ÖGK-N": "ÖGK-Niederösterreich",
    "ÖGK-B": "ÖGK-Burgenland",
    "ÖGK-O": "ÖGK-Oberösterreich",
    "ÖGK-S": "ÖGK-Salzburg",
    "ÖGK-K": "ÖGK-Kärnten",
    "ÖGK-ST": "ÖGK-Steiermark",
    "ÖGK-T": "ÖGK-Tirol",
    "ÖGK-V": "ÖGK-Vorarlberg",
    "Gesamt": "ÖGK-Bundesweit",
}


def create_plot(input_file, dark_mode=True, is_updated=False):
    """
    Creates a visualization of ÖGK refund ratios by state and year.
    
    Args:
        input_file: Path to CSV data file
        dark_mode: Whether to use dark mode styling
        is_updated: Whether this is using updated data
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Read the CSV file and calculate refund ratio
    df = pd.read_csv(input_file)
    df["Ratio"] = df["Refundierungen"] / df["Rechnungsbeträge"]

    # Create figure with portrait format
    fig, ax = plt.subplots(figsize=(11, 15))

    # Apply styling based on dark/light mode
    if dark_mode:
        plt.style.use("dark_background")
        fig.patch.set_facecolor("#1a1a1a")
        ax.set_facecolor("#1a1a1a")
    else:
        plt.style.use("default")
        fig.patch.set_facecolor("white")
        ax.set_facecolor("white")

    # Get unique years and states
    years = sorted(df["Year"].unique())
    states = sorted(df["LST"].unique())

    # Move "Gesamt" to the beginning of the list
    gesamt = "Gesamt"
    states = [s for s in states if s != gesamt]
    states = [gesamt] + states

    # Get Gesamt data for baseline comparison
    gesamt_data = df[df["LST"] == gesamt]

    # Calculate positions for visualization
    total_entities = len(states)
    total_positions = total_entities * len(years)
    y_positions = np.arange(total_positions)

    # Create labels for y-axis (years only)
    y_labels = []
    for state in states:
        for year in years:
            y_labels.append(f"{year}")

    # Create Bundesland labels and positions
    bundesland_labels = [prettify_LST[state] for state in states]
    bundesland_positions = [
        len(years) / 2 - 0.5 + i * len(years) for i in range(len(states))
    ]

    # Add alternating background colors for states
    for i in range(total_entities):
        y_start = i * len(years)
        y_end = (i + 1) * len(years)
        if i % 2 == 1:  # Shade odd-numbered states
            if dark_mode:
                ax.axhspan(y_start - 0.5, y_end - 0.5, color="#2a2a2a", alpha=0.8)
            else:
                ax.axhspan(y_start - 0.5, y_end - 0.5, color="#e0e0e0", alpha=0.9)

    # Plot data points for all states and years
    for i, state in enumerate(states):
        state_data = df[df["LST"] == state]
        for j, year in enumerate(years):
            year_data = state_data[state_data["Year"] == year]
            if not year_data.empty:
                ratio = year_data["Ratio"].iloc[0]
                y_pos = i * len(years) + j

                # Get corresponding national average for comparison
                gesamt_year_data = gesamt_data[gesamt_data["Year"] == year]
                if not gesamt_year_data.empty:
                    gesamt_ratio = gesamt_year_data["Ratio"].iloc[0]
                
                # For non-Gesamt states, plot comparison to national average
                if state != gesamt:
                    # Plot baseline point (national average)
                    ax.plot(
                        gesamt_ratio,
                        y_pos,
                        "D",
                        color="gray",
                        alpha=0.4,
                        markersize=11,
                        zorder=2,
                    )

                    # Calculate visual properties based on distance from national average
                    distance = abs(ratio - gesamt_ratio)
                    scaling_factor = 8
                    line_color = "blue" if ratio > gesamt_ratio else "red"

                    # Create wedge-shaped polygon to connect points
                    half_width = distance * scaling_factor
                    vertices = np.array(
                        [
                            [gesamt_ratio, y_pos],  # Start point (no width)
                            [ratio, y_pos + half_width],  # End point top
                            [ratio, y_pos - half_width],  # End point bottom
                        ]
                    )

                    # Draw polygon with edge
                    polygon = plt.Polygon(
                        vertices,
                        facecolor=line_color,
                        edgecolor=line_color,
                        linewidth=0,
                        alpha=0.8,
                        zorder=1,
                    )
                    ax.add_patch(polygon)

                # Plot state point
                point_color = "black"
                ax.plot(ratio, y_pos, "D", color=point_color, markersize=11, zorder=2)

    # Style settings
    text_color = "white" if dark_mode else "black"

    # Set title and labels
    title_prefix = "Wahlarzt Refundierungsquote nach Verrechnungsstelle und Jahr"
    plt.suptitle(
        title_prefix,
        fontsize=22,
        y=0.95,
        color=text_color,
    )
    ax.set_xlabel(
        "Verhältnis (Refundierungen / Rechnungsbeträge)", fontsize=16, color=text_color
    )

    # Configure y-axis (years)
    ax.set_yticks(y_positions)
    ax.set_yticklabels(y_labels, color=text_color, fontsize=14)

    # Set axis limits
    ax.set_ylim(-0.5, total_positions - 0.5)
    ax.set_xlim(0.30, 0.43)  # Range from 30% to 43%
    
    # Configure x-axis ticks
    x_ticks = np.arange(0.30, 0.43, 0.02)
    ax.set_xticks(x_ticks)
    ax.set_xticklabels([f"{x:.1%}" for x in x_ticks], color=text_color, fontsize=14)

    # Add duplicate x-axis at the top of the plot
    ax2 = ax.twiny()
    ax2.set_xlim(ax.get_xlim())
    ax2.set_xticks(x_ticks)
    ax2.set_xticklabels([f"{x:.1%}" for x in x_ticks], color=text_color, fontsize=14)

    # Add state labels on the left side
    for i in range(len(states)):
        y_pos = bundesland_positions[i]
        label = bundesland_labels[i]
        ax.text(
            0.22,
            y_pos,
            label,
            fontsize=16,
            fontweight="bold",
            color=text_color,
            verticalalignment="center",
            horizontalalignment="left",
            zorder=1,
        )

    # Add grid
    grid_alpha = 0.2 if dark_mode else 0.7
    ax.grid(True, axis="x", linestyle="--", alpha=grid_alpha, color=text_color)
    ax.grid(True, axis="y", linestyle="--", alpha=grid_alpha, color=text_color)

    # Add legend
    legend_elements = [
        plt.Line2D(
            [0],
            [0],
            marker="D",
            color="w",
            markerfacecolor="blue",
            markersize=14,
            label="Wert",
        ),
        plt.Line2D(
            [0],
            [0],
            marker="D",
            color="w",
            markerfacecolor="gray",
            markersize=12,
            alpha=0.3,
            label="ÖGK-Gesamt",
        ),
    ]
    ax.legend(handles=legend_elements, loc="lower right", fontsize=14)

    # Reverse y-axis to show newest years at the top
    ax.invert_yaxis()

    # Set output filename based on mode and data source
    filename = os.path.join(
        OUTPUT_DIR,
        f"oegk_betraege_ratio_points_{'updated' if is_updated else 'original'}_{'dark' if dark_mode else 'light'}.png",
    )

    # Configure save parameters
    save_kwargs = {"dpi": 300, "bbox_inches": "tight"}
    if dark_mode:
        save_kwargs.update({"facecolor": "#1a1a1a", "edgecolor": "none"})
    else:
        save_kwargs.update({"facecolor": "white", "edgecolor": "none"})

    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    plt.subplots_adjust(top=0.895)  # Make room for the title
    plt.subplots_adjust(left=0.43)  # Make room for state labels

    # Add background elements for visual separation
    # Add background rectangles for odd-numbered states
    for i in range(len(states)):
        if i % 2 == 1:
            y_pos = bundesland_positions[i]
            # Convert axis coordinates to figure coordinates
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

    # Add horizontal separator lines between states
    for i in range(total_entities + 1):  # +1 to add a line at the bottom
        y_pos = i * len(years) - 0.5
        # Convert axis y-coordinate to figure coordinates
        fig_y = (
            ax.get_position().y0
            + (total_positions - y_pos - 0.5)
            / total_positions
            * ax.get_position().height
        )
        line = plt.Line2D(
            [0.05, 0.985],
            [fig_y, fig_y],
            transform=fig.transFigure,
            color=text_color,
            alpha=1.0,
            linewidth=1,
            zorder=100,
        )
        fig.lines.append(line)

    # Add vertical line connecting left ends of top and bottom custom lines
    top_y = (
        ax.get_position().y0
        + (total_positions)
        / total_positions
        * ax.get_position().height
    )
    bottom_y = (
        ax.get_position().y0
        + (total_positions - (total_entities * len(years)))
        / total_positions
        * ax.get_position().height
    )
    vertical_line = plt.Line2D(
        [0.05, 0.05],
        [top_y, bottom_y],
        transform=fig.transFigure,
        color=text_color,
        alpha=1.0,
        linewidth=1,
        zorder=100,
    )
    fig.lines.append(vertical_line)

    plt.savefig(filename, **save_kwargs)
    plt.close()


def main():
    """Generate all plot variants (original/updated data in dark/light mode)"""
    # Original data
    create_plot(
        "../data/csv/manually_extracted/OEGK_Betraege.csv",
        dark_mode=True,
        is_updated=False,
    )
    create_plot(
        "../data/csv/manually_extracted/OEGK_Betraege.csv",
        dark_mode=False,
        is_updated=False,
    )

    # Updated data
    create_plot(
        "../data/csv/manually_extracted/OEGK_Betraege_updated2025.csv",
        dark_mode=True,
        is_updated=True,
    )
    create_plot(
        "../data/csv/manually_extracted/OEGK_Betraege_updated2025.csv",
        dark_mode=False,
        is_updated=True,
    )


if __name__ == "__main__":
    main()
