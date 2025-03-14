import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import colorsys

# Global settings
OUTPUT_DIR = "../figures/BVAEB/Betraege"  # Output directory for the plot

prettify_LST = {
    "Wien": "Wien",
    "NÖ": "Niederösterreich",
    "Bgld": "Burgenland",
    "OÖ": "Oberösterreich",
    "Stmk": "Steiermark",
    "Ktn": "Kärnten",
    "Sbg": "Salzburg",
    "Tirol": "Tirol",
    "Vbg": "Vorarlberg",
    "Gesamt": "Gesamt",
}

# VPI data (from /data/extras/VPI/VPI...ods). Average per time period
VPI_DATA = {
    "2019": 106.7,
    "2020": 108.2,
    "2021": 111.2,
    "2022": 120.7,
    "2023": 130.1,
    "2024Q1-Q3": 133.7, # Average of Q1-Q3 2024
    "2024": 134.0,
    "2025": 136.8,
}

# Insured population data (from /data/extras/Handbuch/Tabellen_Statistisches_Handbuch_2024/Kapitel 2_24.xlsx)
# Historical data 2019-2023 from Tabelle 2.02
# Future values calculated with lambda functions
INSURED_POPULATION = {
    "2020": {
        "Wien": 174141,
        "NÖ": 295949,
        "Bgld": 49829,
        "OÖ": 88499,
        "Stmk": 198221,
        "Ktn": 89240,
        "Sbg": 87638,
        "Tirol": 126532,
        "Vbg": 54439,
        "Gesamt": 1171842,
    },
    "2021": {
        "Wien": 174141,
        "NÖ": 295949,
        "Bgld": 49829,
        "OÖ": 88499,
        "Stmk": 198221,
        "Ktn": 89240,
        "Sbg": 87638,
        "Tirol": 126532,
        "Vbg": 54439,
        "Gesamt": 1171842,
    },
    "2022": {
        "Wien": 174141,
        "NÖ": 295949,
        "Bgld": 49829,
        "OÖ": 88499,
        "Stmk": 198221,
        "Ktn": 89240,
        "Sbg": 87638,
        "Tirol": 126532,
        "Vbg": 54439,
        "Gesamt": 1171842,
    },
    "2023": {
        "Wien": 174141,
        "NÖ": 295949,
        "Bgld": 49829,
        "OÖ": 88499,
        "Stmk": 198221,
        "Ktn": 89240,
        "Sbg": 87638,
        "Tirol": 126532,
        "Vbg": 54439,
        "Gesamt": 1171842,
    },
    "2024": {
        "Wien": 174141,
        "NÖ": 295949,
        "Bgld": 49829,
        "OÖ": 88499,
        "Stmk": 198221,
        "Ktn": 89240,
        "Sbg": 87638,
        "Tirol": 126532,
        "Vbg": 54439,
        "Gesamt": 1171842,
    },
    "2024Q1-Q3": lambda: {k: int(v) for k, v in INSURED_POPULATION["2024"].items()},
    "2025": lambda: {
        k: int(v * 1.008) for k, v in INSURED_POPULATION["2024"]().items()
    },
}

def get_population_for_year(year):
    """Get the population data for a specific year"""
    year_str = str(year)
    data = INSURED_POPULATION[year_str]
    return data() if callable(data) else data

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
    df["Weight"] = df.apply(lambda row: get_population_for_year(row["Year"])[row["Bundesland"]] / get_population_for_year(row["Year"])["Gesamt"], axis=1)
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
    fig, ax = plt.subplots(figsize=(12, 8))

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
    # Get all unique states and ensure "Gesamt" is first
    states = sorted(df["Bundesland"].unique())
    if "Gesamt" in states:
        states.remove("Gesamt")
        states.insert(0, "Gesamt")

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
        state_data = df[df["Bundesland"] == state]
        for j, year in enumerate(years):
            year_data = state_data[state_data["Year"] == year]
            if year == "2024Q1-Q3":
                # Adjust the 2024 Q1-Q3 data by multiplying by 4/3 to estimate full year
                year_data = year_data.copy()
                year_data["Rechnungsbeträge_weighted"] = year_data["Rechnungsbeträge_weighted"] * (4/3)
                year_data["Refundierungen_weighted"] = year_data["Refundierungen_weighted"] * (4/3)
                if "Personal_loss" in year_data.columns:
                    year_data["Personal_loss"] = year_data["Personal_loss"] * (4/3)
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
                            label=f"Rechnungsbeträge {year if year != '2024Q1-Q3' else '2024Q1-Q3 × 4/3'}" if i == 0 else "",
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
                            label=f"Refundierungen {year if year != '2024Q1-Q3' else '2024Q1-Q3 × 4/3'}" if i == 0 else "",
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
                                label=f"{year if year != '2024Q1-Q3' else '2024Q1-Q3 × 4/3'}" if i == 0 else "",
                            )
                        )

    # Customize the plot
    text_color = "white" if dark_mode else "black"

    # Set title and labels based on plot type
    if plot_type == "betraege":
        title_prefix = (
            "BVAEB - Inflationsbereinigte Wahlarzt Honorarnoten und Refundierungen pro Versicherter"
        )
        ylabel = "Beträge pro Versicherter (in 2024 Euro)"
    else:
        title_prefix = (
            "BVAEB - Inflationsbereinigte, durchschnittliche, nicht erstattete Wahlarzt-Kosten pro Versicherter"
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
        year = df["Year"].iloc[0]
        value = int(x / get_population_for_year(year)["Gesamt"])
        return f"{value:,} €"

    ax.yaxis.set_major_formatter(plt.FuncFormatter(format_yticks))

    # Set y-axis ticks in 10€ steps
    ymin, ymax = ax.get_ylim()
    year = df["Year"].iloc[0]
    gesamt = get_population_for_year(year)["Gesamt"]
    
    if plot_type == "personal_loss":
        # For personal loss, we need to handle negative values
        # Round to nearest 10 for cleaner tick marks
        ymin_rounded = np.floor(ymin / (10 * gesamt)) * (10 * gesamt)
        ymax_rounded = np.ceil(ymax / (10 * gesamt)) * (10 * gesamt)
        yticks = np.arange(ymin_rounded, ymax_rounded + (10 * gesamt), 10 * gesamt)
    else:
        # For regular betraege plot, only positive values
        ymax_rounded = np.ceil(ymax / (10 * gesamt)) * (10 * gesamt)
        yticks = np.arange(0, ymax_rounded + (10 * gesamt), 10 * gesamt)
    ax.set_yticks(yticks)

    # Add grid with appropriate opacity for each mode
    ax.grid(True, axis="y", linestyle="--", alpha=grid_alpha, color=text_color, zorder=1)

    # Add legend
    handles, labels = ax.get_legend_handles_labels()
    # Remove duplicate labels and sort lexicographically
    by_label = dict(sorted(zip(labels, handles)))
    ax.legend(by_label.values(), by_label.keys(), loc="upper left")

    # Set the axis limits
    ax.set_xlim(-0.6, len(states) - 0.1)
    # Let matplotlib automatically determine the y-axis limit based on the data

    # Adjust layout to prevent label cutoff
    plt.tight_layout()

    # Set output filename based on mode and data source
    if plot_type == "betraege":
        filename = os.path.join(
            OUTPUT_DIR,
            f"bvaeb_betraege_weighted_{'updated' if is_updated else 'original'}_{'dark' if dark_mode else 'light'}.png",
        )
    else:
        filename = os.path.join(
            OUTPUT_DIR,
            f"bvaeb_personal_loss_{'updated' if is_updated else 'original'}_{'dark' if dark_mode else 'light'}.png",
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
        "../data/csv/manually_extracted/BVAEB_Betraege_updated.csv",
        dark_mode=True,
        is_updated=False,
        plot_type="betraege",
    )
    create_plot(
        "../data/csv/manually_extracted/BVAEB_Betraege_updated.csv",
        dark_mode=False,
        is_updated=False,
        plot_type="betraege",
    )

    # Personal loss plots
    create_plot(
        "../data/csv/manually_extracted/BVAEB_Betraege_updated.csv",
        dark_mode=True,
        is_updated=False,
        plot_type="personal_loss",
    )
    create_plot(
        "../data/csv/manually_extracted/BVAEB_Betraege_updated.csv",
        dark_mode=False,
        is_updated=False,
        plot_type="personal_loss",
    )

if __name__ == "__main__":
    main() 
