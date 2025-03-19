import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import colorsys
import glob

# Global settings
OUTPUT_DIR = "../figures/BVAEB/Betraege"  # Output directory for the plot
SV_DATA_DIR = "../data/extras/SV_Jahresberichte"  # Directory containing SV Excel files

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

def read_insured_population_from_excel():
    """
    Read insured population data from Excel files in SV_Veroeffentlichungen directory.
    Returns a dictionary with years as keys and population data as values.
    """
    population_data = {}
    
    # Get all Excel files
    excel_files = glob.glob(os.path.join(SV_DATA_DIR, "Jahresergebnisse_*.xlsx"))
    # Filter out files from years 2018 and 2019
    excel_files = [file for file in excel_files 
                  if not os.path.basename(file).endswith(('_18.xlsx', '_19.xlsx'))]
    
    for file_path in excel_files:
        try:
            # Extract year from filename
            year = f"20{file_path.split('_')[-1].split('.')[0]}"
            
            # Read the Excel file
            df = pd.read_excel(file_path, sheet_name="Tab4", header=None)
            
            # Determine which row to use based on filename
            row_index = 24 if os.path.basename(file_path) == "Jahresergebnisse_20.xlsx" else 11
            
            # Get the row with insured population (B12 to K12 or B25 to K25)
            row_data = df.iloc[row_index, 1:11].values

            #print(year, row_data)
            
            # Create dictionary for this year
            year_data = {
                "Gesamt": int(row_data[0]),
                "Wien": int(row_data[1]),
                "NÖ": int(row_data[2]),
                "Bgld": int(row_data[3]),
                "OÖ": int(row_data[4]),
                "Stmk": int(row_data[5]),
                "Ktn": int(row_data[6]),
                "Sbg": int(row_data[7]),
                "Tirol": int(row_data[8]),
                "Vbg": int(row_data[9])
            }
            
            population_data[year] = year_data
            
        except Exception as e:
            print(f"Error reading {file_path}: {str(e)}")
            continue
    
    return population_data

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

# Read insured population data from Excel files
INSURED_POPULATION = read_insured_population_from_excel()

# Add 2024Q1-Q3 data as a lambda function
INSURED_POPULATION["2024Q1-Q3"] = lambda: {k: int(v) for k, v in INSURED_POPULATION["2024"].items()}

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
    bar_width = 1 / len(years)  # Adjust bar width based on number of years
    group_spacing = 0.2  # Add spacing between groups of bars

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
                            i + (j - 1) * bar_width + i * group_spacing,
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
                            i + (j - 1) * bar_width + i * group_spacing,
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
                                i + (j - 1) * bar_width + i * group_spacing,
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

    # Set x-axis labels with special formatting for Gesamt
    xticks = x + (len(years) - 3) * bar_width / 2 + x * group_spacing
    xlabels = []
    for state in states:
        if state == "Gesamt":
            xlabels.append(r"$\mathbf{Gesamt}$")  # Bold Gesamt using LaTeX
        else:
            xlabels.append(prettify_LST.get(state, state))
    
    plt.xticks(xticks, xlabels, rotation=0, ha="center", color=text_color)
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
    ax.legend(by_label.values(), by_label.keys(), loc="center", bbox_to_anchor=(0.5, -0.19), ncol=2)

    # Add note about 2020 data
    note_text = "Für das Jahr 2020 wurden ausschließlich Daten aus dem Rechenkreis \"Öffentlich Bedienstete\" verwendet"
    plt.figtext(0.53, -0.0, note_text, ha='center', color=text_color, fontsize=10)

    # Set the axis limits
    ax.set_xlim(-0.5, len(states) - 0.2 + (len(states) - 1) * group_spacing)
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
