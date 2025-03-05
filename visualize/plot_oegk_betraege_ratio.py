import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Global settings
OUTPUT_DIR = "../figures/OEGK/Betraege"  # Output directory for the plot

prettify_LST = {
    "ÖGK-W": "Wien",
    "ÖGK-N": "Niederösterreich",
    "ÖGK-B": "Burgenland",
    "ÖGK-O": "Oberösterreich",
    "ÖGK-S": "Salzburg",
    "ÖGK-K": "Kärnten",
    "ÖGK-ST": "Steiermark",
    "ÖGK-T": "Tirol",
    "ÖGK-V": "Vorarlberg",
    "Gesamt": "Gesamt",
}


def create_plot(input_file, dark_mode=True, is_updated=False):
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Read the CSV file
    df = pd.read_csv(input_file)

    # Calculate the ratio between refunds and bill amounts
    df["Ratio"] = df["Refundierungen"] / df["Rechnungsbeträge"]

    # Create figure with smaller size
    fig, ax = plt.subplots(figsize=(15, 8))

    # Set dark mode if enabled
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

    # Create x-axis positions
    x = np.arange(len(states))
    bar_width = 0.85 / len(years)  # Adjust bar width based on number of years

    # Create bars
    bars = []
    for i, state in enumerate(states):
        state_data = df[df["LST"] == state]
        for j, year in enumerate(years):
            year_data = state_data[state_data["Year"] == year]
            if not year_data.empty:
                ratio = year_data["Ratio"].iloc[0]
                # Use different shades for each year
                color = plt.cm.viridis(j / len(years))
                # For each year, create two bars: one for the ratio and one for the remaining area
                bars.append(
                    ax.bar(i + (j - 1) * bar_width, ratio, bar_width, color=color)
                )
                # Add the remaining area in a lighter shade
                remaining = 0.5 - ratio
                if remaining > 0:
                    bars.append(
                        ax.bar(
                            i + (j - 1) * bar_width,
                            remaining,
                            bar_width,
                            bottom=ratio,
                            color=plt.cm.viridis(j / len(years), alpha=0.3),
                        )
                    )

    # Customize the plot
    text_color = "white" if dark_mode else "black"

    # Set title and labels
    title_prefix = "ÖGK - Verhältnis Wahlarzt Refundierungen zu Rechnungsbeträgen nach Bundesland und Jahr"
    if is_updated:
        title_prefix += " (Aktualisiert 2025)"
    plt.title(
        title_prefix,
        fontsize=16,
        pad=20,
        color=text_color,
    )
    plt.xlabel("Bundesland", fontsize=12, color=text_color)
    plt.ylabel(
        "Verhältnis (Refundierungen / Rechnungsbeträge)",
        fontsize=12,
        labelpad=10,
        color=text_color,
    )

    xticks = x + (len(years) - 3) * bar_width / 2
    # xticks[0] = xticks[0] - 0.5 * bar_width  # Adjust first x-tick
    # Set x-axis ticks
    plt.xticks(
        xticks, map(prettify_LST.get, states), rotation=0, ha="center", color=text_color
    )
    plt.yticks(color=text_color)

    # Set y-axis ticks as percentages with 5% steps
    ax.set_yticks(np.arange(0, 0.55, 0.05))  # 0 to 55% in 5% steps
    ax.set_yticklabels([f'{int(x*100)}%' for x in ax.get_yticks()])

    # Add grid with appropriate opacity for each mode
    grid_alpha = 0.2 if dark_mode else 0.7
    ax.grid(True, axis="y", linestyle="--", alpha=grid_alpha, color=text_color)

    # Add a horizontal line at ratio = 1
    ax.axhline(y=1, color="red", linestyle="--", alpha=0.5)

    # Add legend for years
    legend_elements = [
        plt.Rectangle((0, 0), 1, 1, facecolor=plt.cm.viridis(i / len(years)))
        for i in range(len(years))
    ]
    ax.legend(legend_elements, years, title="Jahr", loc="lower right")

    # Set the axis limits
    ax.set_xlim(-0.6, len(states) - 0.1)
    ax.set_ylim(0, 0.5)  # Set maximum y-axis to 0.5

    # Adjust layout to prevent label cutoff
    plt.tight_layout()

    # Set output filename based on mode and data source
    filename = os.path.join(
        OUTPUT_DIR,
        f"oegk_betraege_ratio_{'updated' if is_updated else 'original'}_{'dark' if dark_mode else 'light'}.png",
    )

    # Save the plot with appropriate background
    save_kwargs = {"dpi": 300, "bbox_inches": "tight"}

    if dark_mode:
        save_kwargs.update({"facecolor": "#1a1a1a", "edgecolor": "none"})
    else:
        save_kwargs.update({"facecolor": "white", "edgecolor": "none"})

    plt.savefig(filename, **save_kwargs)
    plt.close()


def main():
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
