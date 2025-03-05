import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import colorsys  # Add this import at the top

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

# Placeholder VPI data (to be replaced with actual data)
VPI_DATA = {
    "2019": 106.7,  # Base year
    "2020": 108.2,
    "2021": 111.2,
    "2022": 120.7,
    "2023": 130.1,
    "2024Q1-Q3": 133.7,
    "2024": 134.0,
    "2025": 136.8,
}

# Placeholder insured population data (to be replaced with actual data)
INSURED_POPULATION = {
    "ÖGK-W": 1800000,
    "ÖGK-N": 1600000,
    "ÖGK-B": 300000,
    "ÖGK-O": 1400000,
    "ÖGK-S": 500000,
    "ÖGK-K": 500000,
    "ÖGK-ST": 1100000,
    "ÖGK-T": 700000,
    "ÖGK-V": 350000,
    "Gesamt": 7750000,
}


def adjust_for_inflation(value, year, base_year=2024):
    """Adjust value for inflation using VPI data"""
    return value * (VPI_DATA[str(base_year)] / VPI_DATA[str(year)])


def create_plot(input_file, dark_mode=True, is_updated=False, plot_type="betraege"):
    """
    Create a plot showing either billing amounts or personal loss.

    Args:
        input_file: Path to the input CSV file
        dark_mode: Whether to use dark mode styling
        is_updated: Whether this is using updated 2025 data
        plot_type: Either "betraege" or "personal_loss" to determine plot type
    """
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Read the CSV file
    df = pd.read_csv(input_file)

    # Adjust values for inflation
    df["Rechnungsbeträge_adj"] = df.apply(
        lambda row: adjust_for_inflation(row["Rechnungsbeträge"], row["Year"]), axis=1
    )
    df["Refundierungen_adj"] = df.apply(
        lambda row: adjust_for_inflation(row["Refundierungen"], row["Year"]), axis=1
    )

    # Weight by insured population
    df["Weight"] = df["LST"].map(INSURED_POPULATION) / INSURED_POPULATION["Gesamt"]
    df["Rechnungsbeträge_weighted"] = df["Rechnungsbeträge_adj"] / df["Weight"]
    df["Refundierungen_weighted"] = df["Refundierungen_adj"] / df["Weight"]

    # Calculate personal loss if needed
    if plot_type == "personal_loss":
        df["Personal_loss"] = np.where(
            df["Refundierungen"].notna(),
            -(df["Rechnungsbeträge_weighted"] - df["Refundierungen_weighted"]),
            np.nan
        )

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

    # Add placeholder text
    placeholder_text = "PLATZHALTER: Versichertenzahlen sind Beispieldaten"
    fig.text(
        0.5,
        0.95,
        placeholder_text,
        ha="center",
        va="center",
        fontsize=20,
        color="gray",
        alpha=0.3,
        rotation=30,
    )

    # Get unique years and states
    years = sorted(df["Year"].unique())
    states = sorted(df["LST"].unique())

    # Create x-axis positions
    x = np.arange(len(states))
    bar_width = 0.85 / len(years)  # Adjust bar width based on number of years

    # Add special grid line at 0 for personal loss plot before plotting bars
    # Set grid alpha to 0.2 for dark mode and 0.7 for light mode
    grid_alpha = 0.2 if dark_mode else 0.7
    if dark_mode:
        ax.axhline(y=0, color='black', linestyle='-', linewidth=2, alpha=1, zorder=1)
    else:
        ax.axhline(y=0, color='black', linestyle='-', linewidth=2, alpha=1, zorder=1)

    # Create bars
    bars = []
    for i, state in enumerate(states):
        state_data = df[df["LST"] == state]
        for j, year in enumerate(years):
            year_data = state_data[state_data["Year"] == year]
            if not year_data.empty:
                if plot_type == "betraege":
                    # Get the values for billing amounts plot
                    rechnungsbetrag = year_data["Rechnungsbeträge_weighted"].iloc[0]
                    refundierung = year_data["Refundierungen_weighted"].iloc[0]

                    # Calculate base color for this year
                    base_color = plt.cm.viridis(0.2 + 0.6 * (j / len(years)))

                    # Convert RGB to HSV, rotate hue, and convert back to RGB for Rechnungsbeträge
                    hsv = colorsys.rgb_to_hsv(base_color[0], base_color[1], base_color[2])
                    hue_shift = 0.2  # Rotate hue by 15% of the color wheel
                    new_hue = (hsv[0] + hue_shift) % 1.0  # Keep hue in [0,1] range
                    rgb = colorsys.hsv_to_rgb(new_hue, hsv[1], hsv[2])
                    rechnungsbetraege_color = np.array([*rgb, base_color[3]])  # Keep original alpha

                    # Plot Rechnungsbeträge with modified color
                    bars.append(
                        ax.bar(
                            i + (j - 1) * bar_width,
                            rechnungsbetrag,
                            bar_width,
                            color=rechnungsbetraege_color,
                            alpha=0.7,
                            label=f"Rechnungsbeträge {year}" if i == 0 else "",
                        )
                    )
                    # Plot Refundierungen with lighter shade of original color
                    refund_color = np.array(base_color) * 1.3  # Make it lighter
                    refund_color[3] = base_color[3]  # Keep original alpha
                    refund_color = np.clip(refund_color, 0, 1)  # Ensure values are in valid range

                    bars.append(
                        ax.bar(
                            i + (j - 1) * bar_width,
                            refundierung,
                            bar_width,
                            color=refund_color,
                            label=f"Refundierungen {year}" if i == 0 else "",
                        )
                    )
                else:  # personal_loss
                    # Get the personal loss value and check if it's valid
                    if not year_data.empty and not year_data["Personal_loss"].isna().iloc[0]:
                        personal_loss = year_data["Personal_loss"].iloc[0]
                        bars.append(
                            ax.bar(
                                i + (j - 1) * bar_width,
                                personal_loss,
                                bar_width,
                                color=plt.cm.viridis(0.2 + 0.6 * (j / len(years))),
                                alpha=1,
                                label=f"{year}" if i == 0 else "",
                            )
                        )

    # Customize the plot
    text_color = "white" if dark_mode else "black"

    # Set title and labels based on plot type
    if plot_type == "betraege":
        title_prefix = (
            "ÖGK - Inflationsbereinigte Wahlarzt Honorarnoten und Refundierungen pro Versicherter"
        )
        ylabel = "Beträge pro Versicherter (in 2024 Euro)"
    else:
        title_prefix = (
            "ÖGK - Inflationsbereinigte, durchschnittliche, nicht erstattete Wahlarzt-Kosten pro Versicherter"
        )
        ylabel = "nicht erstattete Kosten pro Versicherter (in 2024 Euro)"

    if is_updated:
        title_prefix += " (Aktualisiert 2025)"
    plt.title(
        title_prefix,
        fontsize=16,
        pad=20,
        color=text_color,
    )
    plt.xlabel("Bundesland", fontsize=12, color=text_color)
    plt.ylabel(ylabel, fontsize=12, labelpad=10, color=text_color)

    xticks = x + (len(years) - 3) * bar_width / 2
    plt.xticks(
        xticks, map(prettify_LST.get, states), rotation=0, ha="center", color=text_color
    )
    plt.yticks(color=text_color)

    # Format y-axis with thousands separator, € symbol, and 10€ steps
    def format_yticks(x, p):
        value = int(x / INSURED_POPULATION["Gesamt"])
        return f"{value:,} €"

    ax.yaxis.set_major_formatter(plt.FuncFormatter(format_yticks))

    # Set y-axis ticks in 10€ steps
    ymin, ymax = ax.get_ylim()
    if plot_type == "personal_loss":
        # For personal loss, we need to handle negative values
        # Round to nearest 10 for cleaner tick marks
        ymin_rounded = np.floor(ymin / (10 * INSURED_POPULATION["Gesamt"])) * (10 * INSURED_POPULATION["Gesamt"])
        ymax_rounded = np.ceil(ymax / (10 * INSURED_POPULATION["Gesamt"])) * (10 * INSURED_POPULATION["Gesamt"])
        yticks = np.arange(ymin_rounded, ymax_rounded + (10 * INSURED_POPULATION["Gesamt"]), 10 * INSURED_POPULATION["Gesamt"])
    else:
        # For regular betraege plot, only positive values
        ymax_rounded = np.ceil(ymax / (10 * INSURED_POPULATION["Gesamt"])) * (10 * INSURED_POPULATION["Gesamt"])
        yticks = np.arange(0, ymax_rounded + (10 * INSURED_POPULATION["Gesamt"]), 10 * INSURED_POPULATION["Gesamt"])
    ax.set_yticks(yticks)

    # Add grid with appropriate opacity for each mode
    ax.grid(True, axis="y", linestyle="--", alpha=grid_alpha, color=text_color, zorder=1)

    # Add legend
    handles, labels = ax.get_legend_handles_labels()
    # Remove duplicate labels
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), title="Jahr", loc="upper left")

    # Add note about missing data for original dataset
    if not is_updated:
        if plot_type == "personal_loss":
            y_pos = 0.02
            va = "bottom"
        else:
            y_pos = 0.98
            va = "top"
        ax.text(0.98, y_pos, 
                "Hinweis: Refundierungen 2020 für Vorarlberg\nliegen nicht vor",
                transform=ax.transAxes,
                ha='right',
                va=va,
                fontsize=10,
                color=text_color,
                bbox=dict(facecolor='none', edgecolor=text_color, alpha=0.5, pad=5))

    # Set the axis limits
    ax.set_xlim(-0.6, len(states) - 0.1)
    # Let matplotlib automatically determine the y-axis limit based on the data

    # Adjust layout to prevent label cutoff
    plt.tight_layout()

    # Set output filename based on mode and data source
    if plot_type == "betraege":
        filename = os.path.join(
            OUTPUT_DIR,
            f"oegk_betraege_weighted_{'updated' if is_updated else 'original'}_{'dark' if dark_mode else 'light'}.png",
        )
    else:
        filename = os.path.join(
            OUTPUT_DIR,
            f"oegk_personal_loss_{'updated' if is_updated else 'original'}_{'dark' if dark_mode else 'light'}.png",
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
        plot_type="betraege",
    )
    create_plot(
        "../data/csv/manually_extracted/OEGK_Betraege.csv",
        dark_mode=False,
        is_updated=False,
        plot_type="betraege",
    )

    # Updated data
    create_plot(
        "../data/csv/manually_extracted/OEGK_Betraege_updated2025.csv",
        dark_mode=True,
        is_updated=True,
        plot_type="betraege",
    )
    create_plot(
        "../data/csv/manually_extracted/OEGK_Betraege_updated2025.csv",
        dark_mode=False,
        is_updated=True,
        plot_type="betraege",
    )

    # Personal loss plots
    create_plot(
        "../data/csv/manually_extracted/OEGK_Betraege.csv",
        dark_mode=True,
        is_updated=False,
        plot_type="personal_loss",
    )
    create_plot(
        "../data/csv/manually_extracted/OEGK_Betraege.csv",
        dark_mode=False,
        is_updated=False,
        plot_type="personal_loss",
    )

    # Updated personal loss plots
    create_plot(
        "../data/csv/manually_extracted/OEGK_Betraege_updated2025.csv",
        dark_mode=True,
        is_updated=True,
        plot_type="personal_loss",
    )
    create_plot(
        "../data/csv/manually_extracted/OEGK_Betraege_updated2025.csv",
        dark_mode=False,
        is_updated=True,
        plot_type="personal_loss",
    )


if __name__ == "__main__":
    main()
