import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import colorsys
import glob

# Global settings
OUTPUT_DIR = "../figures/Insurance_Comparison"  # Output directory for the plot
SV_DATA_DIR = "../data/extras/SV_Jahresberichte"  # Directory containing SV Excel files

# Dictionary to prettify insurance provider names
prettify_insurance = {
    "BVAEB": "BVAEB-Bundesweit",
    "ÖGK": "ÖGK-Bundesweit",
    "SVS": "SVS-Bundesweit",
}

def read_insured_population_from_excel():
    """
    Read insured population data from Excel files in SV_Veroeffentlichungen directory.
    Returns a dictionary with insurance providers as keys, containing years and population data.
    """
    population_data = {
        "BVAEB": {},
        "ÖGK": {},
        "SVS": {}
    }
    
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
            
            # Get the row with insured population (B11 for ÖGK, B12 for BVAEB, B13 for SVS)
            oegk_data = int(df.iloc[10, 1])  # B11
            bvaeb_data = int(df.iloc[11, 1])  # B12
            svs_data = int(df.iloc[12, 1])  # B13
            
            # Store data for each insurance provider
            population_data["ÖGK"][year] = {"Gesamt": oegk_data}
            population_data["BVAEB"][year] = {"Gesamt": bvaeb_data}
            population_data["SVS"][year] = {"Gesamt": svs_data}
            
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
}

# Read insured population data from Excel files
INSURED_POPULATION = read_insured_population_from_excel()

# Add 2024Q1-Q3 data using 2024 data directly
for insurance in ["BVAEB", "ÖGK", "SVS"]:
    INSURED_POPULATION[insurance]["2024Q1-Q3"] = INSURED_POPULATION[insurance]["2024"]

def get_population_for_year(year, insurance):
    """Get the population data for a specific year and insurance provider"""
    year_str = str(year)
    data = INSURED_POPULATION[insurance][year_str]
    return data() if callable(data) else data

def adjust_for_inflation(value, year, base_year=2024):
    """Adjust value for inflation using VPI data"""
    return value * (VPI_DATA[str(base_year)] / VPI_DATA[str(year)])

def create_plot(bvaeb_file, oegk_file, svs_file, dark_mode=True, is_updated=False, plot_type="betraege"):
    """
    Create a plot showing either billing amounts or personal loss.

    Args:
        bvaeb_file: Path to BVAEB CSV data file
        oegk_file: Path to ÖGK CSV data file
        svs_file: Path to SVS CSV data file
        dark_mode: Whether to use dark mode styling
        is_updated: Whether this is using updated 2025 data
        plot_type: Either "betraege" or "personal_loss" to determine plot type
    """
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Load data from each insurance provider
    # BVAEB data
    bvaeb_df = pd.read_csv(bvaeb_file)
    bvaeb_df = bvaeb_df[bvaeb_df["Bundesland"] == "Gesamt"].copy()
    bvaeb_df["Insurance"] = "BVAEB"
    bvaeb_df["Year"] = bvaeb_df["Year"].astype(str)

    # ÖGK data
    oegk_df = pd.read_csv(oegk_file)
    oegk_df = oegk_df[oegk_df["LST"] == "Gesamt"].copy()
    oegk_df["Insurance"] = "ÖGK"
    oegk_df["Year"] = oegk_df["Year"].astype(str)

    # SVS data
    svs_df = pd.read_csv(svs_file)
    svs_df = svs_df[svs_df["Bundesland"] == "Gesamt"].copy()
    svs_df["Insurance"] = "SVS"
    svs_df["Year"] = svs_df["Year"].astype(str)

    # Combine all data
    combined_df = pd.concat([bvaeb_df, oegk_df, svs_df], ignore_index=True)

    # Adjust values for inflation
    combined_df["Rechnungsbeträge_adj"] = combined_df.apply(
        lambda row: adjust_for_inflation(row["Rechnungsbeträge"], row["Year"]), axis=1
    )
    combined_df["Refundierungen_adj"] = combined_df.apply(
        lambda row: adjust_for_inflation(row["Refundierungen"], row["Year"]), axis=1
    )

    # Weight by insured population
    combined_df["Weight"] = combined_df.apply(
        lambda row: get_population_for_year(row["Year"], row["Insurance"])["Gesamt"], 
        axis=1
    )
    combined_df["Rechnungsbeträge_weighted"] = combined_df["Rechnungsbeträge_adj"] / combined_df["Weight"]
    combined_df["Refundierungen_weighted"] = combined_df["Refundierungen_adj"] / combined_df["Weight"]

    # Calculate personal loss if needed
    if plot_type == "personal_loss":
        combined_df["Personal_loss"] = np.where(
            combined_df["Refundierungen"].notna(),
            -(combined_df["Rechnungsbeträge_weighted"] - combined_df["Refundierungen_weighted"]),
            np.nan
        )

    # Create figure with smaller size
    fig, ax = plt.subplots(figsize=(11, 11))

    # Set dark mode if enabled
    if dark_mode:
        plt.style.use("dark_background")
        fig.patch.set_facecolor("#1a1a1a")
        ax.set_facecolor("#1a1a1a")
    else:
        plt.style.use("default")
        fig.patch.set_facecolor("white")
        ax.set_facecolor("white")

    # Get unique years and insurances
    years = sorted(combined_df["Year"].unique())
    insurances = ["ÖGK", "BVAEB", "SVS"]  # Fixed order

    # Create x-axis positions
    x = np.arange(len(insurances))
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
    for i, insurance in enumerate(insurances):
        insurance_data = combined_df[combined_df["Insurance"] == insurance]
        for j, year in enumerate(years):
            year_data = insurance_data[insurance_data["Year"] == year]
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
            "Inflationsbereinigte Wahlarzthonorarnoten und Refundierungen pro Versichertem im Vergleich"
        )
        ylabel = "Beträge pro Versichertem (in 2024 Euro)"
    else:
        title_prefix = (
            "Inflationsbereinigte, durchschnittliche, nicht erstattete Wahlarzt-Kosten pro Versichertem im Vergleich"
        )
        ylabel = "nicht erstattete Kosten pro Versichertem (in 2024 Euro)"

    plt.title(
        title_prefix,
        fontsize=16,
        pad=20,
        color=text_color,
    )
    plt.xlabel("Versicherung", fontsize=12, color=text_color)
    plt.ylabel(ylabel, fontsize=12, labelpad=10, color=text_color)

    xticks = x + (len(years) - 3) * bar_width / 2
    plt.xticks(
        xticks, map(prettify_insurance.get, insurances), rotation=0, ha="center", color=text_color
    )
    plt.yticks(color=text_color)

    # Format y-axis with thousands separator, € symbol, and 10€ steps
    def format_yticks(x, p):
        value = int(x)
        return f"{value:,} €"

    ax.yaxis.set_major_formatter(plt.FuncFormatter(format_yticks))

    # Set y-axis ticks in 10€ steps
    if plot_type == "personal_loss":
        # For personal loss, we need to handle negative values
        ax.yaxis.set_major_locator(plt.AutoLocator())
    else:
        # For regular betraege plot, only positive values
         ax.yaxis.set_major_locator(plt.MaxNLocator(steps=[1, 2, 5, 10], integer=True))

    # Add grid with appropriate opacity for each mode
    ax.grid(True, axis="y", linestyle="--", alpha=grid_alpha, color=text_color, zorder=1)

    # Add watermark
    print_watermark = False
    if print_watermark:
        watermark_text = "NOCH FALSCHE DATEN"
        watermark_color = "red" if dark_mode else "darkred"
        watermark_alpha = 0.3
        ax.text(0.5, 0.5, watermark_text, 
                transform=ax.transAxes,
                fontsize=72,
                color=watermark_color,
                alpha=watermark_alpha,
                ha='center',
                va='center',
                rotation=45,
                fontweight='bold',
                zorder=2)

    # Add legend
    handles, labels = ax.get_legend_handles_labels()
    # Remove duplicate labels and sort lexicographically
    by_label = dict(sorted(zip(labels, handles)))
    ax.legend(by_label.values(), by_label.keys(), loc="upper left")

    # Set the axis limits
    ax.set_xlim(-0.6, len(insurances) - 0.1)
    # Let matplotlib automatically determine the y-axis limit based on the data

    # Adjust layout to prevent label cutoff
    plt.tight_layout()

    # Set output filename based on mode and data source
    if plot_type == "betraege":
        filename = os.path.join(
            OUTPUT_DIR,
            f"insurance_comparison_betraege_weighted_{'updated' if is_updated else 'original'}_{'dark' if dark_mode else 'light'}.png",
        )
    else:
        filename = os.path.join(
            OUTPUT_DIR,
            f"insurance_comparison_personal_loss_{'updated' if is_updated else 'original'}_{'dark' if dark_mode else 'light'}.png",
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
        "../data/csv/manually_extracted/OEGK_Betraege_updated2025.csv",
        "../data/csv/manually_extracted/SVS_Betraege_updated.csv",
        dark_mode=True,
        is_updated=False,
        plot_type="betraege",
    )
    create_plot(
        "../data/csv/manually_extracted/BVAEB_Betraege_updated.csv",
        "../data/csv/manually_extracted/OEGK_Betraege_updated2025.csv",
        "../data/csv/manually_extracted/SVS_Betraege_updated.csv",
        dark_mode=False,
        is_updated=False,
        plot_type="betraege",
    )

    # Personal loss plots
    create_plot(
        "../data/csv/manually_extracted/BVAEB_Betraege_updated.csv",
        "../data/csv/manually_extracted/OEGK_Betraege_updated2025.csv",
        "../data/csv/manually_extracted/SVS_Betraege_updated.csv",
        dark_mode=True,
        is_updated=False,
        plot_type="personal_loss",
    )
    create_plot(
        "../data/csv/manually_extracted/BVAEB_Betraege_updated.csv",
        "../data/csv/manually_extracted/OEGK_Betraege_updated2025.csv",
        "../data/csv/manually_extracted/SVS_Betraege_updated.csv",
        dark_mode=False,
        is_updated=False,
        plot_type="personal_loss",
    )

if __name__ == "__main__":
    main() 
