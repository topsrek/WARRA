import locale
import pandas as pd
import os
import numpy as np


EXPORT_DIR = "../../data/csv"

DATA_DIR = "../../raw_data/2023_Anfrage/extracted_data/csv_files/"
DATA_DIR_BEILAGE_13_14_15_16 = "../../raw_data/2023_Anfrage/extracted_data/Beilage_13_14_15_16/exports/"

LST_TO_BUNDESLAND = {
    "W": "Wien",
    "N": "Niederösterreich",
    "O": "Oberösterreich",
    "B": "Burgenland",
    "S": "Salzburg",
    "ST": "Steiermark",
    "K": "Kärnten",
    "T": "Tirol",
    "V": "Vorarlberg",
}


# Assert that all sums are correct
# Are deciEuros better than Euros? -> no rounding errors
# FG Code to int
# make counts (Anzahl) also to true ints
# Bundesländer Namen explizit

# Delete all Gesamt rows?!

# make educated guesses on worng data (see obsiain for details)


def convert_to_euro(column):
    locale.setlocale(locale.LC_ALL, "de_DE.UTF-8")
    return pd.to_numeric(column).map(
        lambda x: locale.currency(x, symbol="€", grouping=True)
    )


def convert_month_year_to_date(df):
    """Convert month.year column to proper datetime Period"""
    df["Date"] = pd.to_datetime(
        df["Monat.Jahr"]
        .str.replace("Jän", "01")
        .str.replace("Feb", "02")
        .str.replace("Mär", "03")
        .str.replace("Apr", "04")
        .str.replace("Mai", "05")
        .str.replace("Jun", "06")
        .str.replace("Jul", "07")
        .str.replace("Aug", "08")
        .str.replace("Sep", "09")
        .str.replace("Okt", "10")
        .str.replace("Nov", "11")
        .str.replace("Dez", "12")
        .str.replace(".", "/"),
        format="%m/%y",
    ).dt.to_period("M")
    return df


def export_to_csv(df, filename, export_dir=EXPORT_DIR):
    ensure_directory(export_dir)
    filepath = os.path.join(export_dir, f"{filename}")
    df.to_csv(filepath)


def ensure_directory(directory):
    """Create directory if it doesn't exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")


def process_1():
    new_filename = "01_OEGK_Betraege_pro_Landesstelle_2023.csv"
    Beilage1_filename = (
        DATA_DIR + "Beilage_1_combined_tables.csv"
    )
    df_1 = pd.read_csv(Beilage1_filename)
    df_1["Bundesland_pretty"] = (
        df_1["LST"].str.split("-", expand=True)[1].str.strip().map(LST_TO_BUNDESLAND)
    )
    # df_1.loc[df_1["LST"] == "Gesamt", "Bundesland_pretty"] = "Alle"
    df_1["Year"] = pd.Period("2023")
    df_1 = df_1.set_index(["Year", "LST"])

    df_1["FG-Code"] = "ALL"

    df_1["Refundierungen_pretty"] = convert_to_euro(df_1["Refundierungen"])
    df_1["Rechnungsbeträge_pretty"] = convert_to_euro(df_1["Rechnungsbeträge"])

    export_to_csv(df_1, new_filename)


def process_2():
    new_filename = "02_OEGK_Betraege_pro_Fachrichtung_2023.csv"
    Beilage2_filename = (
        DATA_DIR + "Beilage_2_combined_tables.csv"
    )
    df_2 = pd.read_csv(Beilage2_filename)

    df_2["Year"] = pd.Period("2023")
    # df_2.loc[df_2["FG-Code"] == "", "FG-Code"] = "Alle"
    df_2 = df_2.set_index(["Year", "FG-Code"])

    df_2["LST"] = "ALL"
    df_2["Bundesland_pretty"] = "Alle"

    export_to_csv(df_2, new_filename)


def process_3():
    new_filename = (
        "03_OEGK_Antraege_pro_Monat_2023_pro_Fachrichtung_online_postal_Bundesweit.csv"
    )
    Beilage3_filename = (
        DATA_DIR + "Beilage_3_combined_tables.csv"
    )
    df_3 = pd.read_csv(Beilage3_filename)

    df_3 = convert_month_year_to_date(df_3)

    df_3["Year"] = pd.Period("2023")
    df_3 = df_3.set_index(["Date", "FG-Code"])

    df_3["LST"] = "ALL"
    df_3["Bundesland_pretty"] = "Alle"

    export_to_csv(df_3, new_filename)


def process_4():
    new_filename = "04_OEGK_Antraege_pro_Monat_2023_pro_Fachrichtung_online_postal_pro_Bundesland.csv"
    Beilage4_filename = (
        DATA_DIR + "Beilage_4_combined_tables.csv"
    )
    df_4 = pd.read_csv(Beilage4_filename)

    # Convert month.year to proper datetime
    df_4 = convert_month_year_to_date(df_4)

    df_4["Year"] = pd.Period("2023")
    df_4.rename(columns={"ÖGK-LS": "LST"}, inplace=True)
    df_4["Bundesland_pretty"] = (
        df_4["LST"].str.split("-", expand=True)[1].str.strip().map(LST_TO_BUNDESLAND)
    )
    # df_4.loc[df_4["LST"] == "Gesamt", "Bundesland_pretty"] = "Alle"

    # Recalculate totals to ensure consistency
    df_4["Gesamt"] = df_4["postal"].fillna(0) + df_4["online"].fillna(0)

    # Inconsistent rows:
    # ÖGK-LS	Monat.Jahr	FG-Code	Fachrichtung	postal	online	Gesamt	calculated_sum	sum_matches
    # 1526	ÖGK-S	Sep.23	20.0	FA für Psychiatrie -	6.0	8.0	68.0	14.0	False
    # 2612	ÖGK-W	Jän.23	29.0	FA für Immunologie -	1.0	4.0	14.0	5.0	False

    df_4 = df_4.set_index(["Date", "FG-Code", "LST"])

    export_to_csv(df_4, new_filename)


def process_5():
    new_filename = "05_OEGK_Abgearbeitete_Antraege_pro_Monat_2023_pro_Fachrichtung_postal_online_Bundesweit.csv"
    Beilage5_filename = (
        DATA_DIR + "Beilage_5_combined_tables.csv"
    )
    df_5 = pd.read_csv(Beilage5_filename)

    df_5 = convert_month_year_to_date(df_5)

    df_5["Year"] = pd.Period("2023")
    df_5 = df_5.set_index(["Date", "FG-Code"])

    df_5.rename(columns={"ÖGK-LS": "LST"}, inplace=True)
    df_5["LST"] = "ALL"
    df_5["Bundesland_pretty"] = "Alle"

    export_to_csv(df_5, new_filename)

def process_6():
    new_filename = "06_OEGK_Abgearbeitete_Antraege_pro_Monat_2023_pro_Fachrichtung_postal_online_pro_Bundesland.csv"
    Beilage6_filename = (
        DATA_DIR + "Beilage_6_combined_tables.csv"
    )
    df_6 = pd.read_csv(Beilage6_filename)

    df_6 = convert_month_year_to_date(df_6)

    df_6["Year"] = pd.Period("2023")
    df_6.rename(columns={"ÖGK-LS": "LST"}, inplace=True)


    df_6["Bundesland_pretty"] = (
        df_6["LST"].str.split("-", expand=True)[1].str.strip().map(LST_TO_BUNDESLAND)
    )
    # df_6.loc[df_6["LST"] == "Gesamt", "Bundesland_pretty"] = "Alle"

    df_6 = df_6.set_index(["Date", "FG-Code", "LST"])

    # Recalculate totals to ensure consistency
    df_6["Gesamt"] = df_6["postal"].fillna(0) + df_6["online"].fillna(0)

    # Inconsistent rows:
    # ÖGK-LS	Monat.Jahr	FG-Code	Fachrichtung	postal	online	Gesamt	calculated_sum	sum_matches
    # 2612	ÖGK-W	Jän.23	29.0	FA für Immunologie -	1.0	4.0	14.0	5.0	False

    export_to_csv(df_6, new_filename)

def process_5a():
    new_filename = "05a_OEGK_Abgearbeitete_Antraege_pro_Monat_2021_bis_Mai_2023_pro_Fachrichtung_postal_online_Bundesweit.csv"
    Beilage5a_filename = (
        DATA_DIR + "Beilage_5a_combined_tables.csv"
    )
    df_5a = pd.read_csv(Beilage5a_filename)

    df_5a = convert_month_year_to_date(df_5a)

    df_5a = df_5a.set_index(["Date", "FG-Code"])

    df_5a.rename(columns={"ÖGK-LS": "LST"}, inplace=True)
    df_5a["LST"] = "ALL"
    df_5a["Bundesland_pretty"] = "Alle"

    export_to_csv(df_5a, new_filename)

def process_6a():
    new_filename = "06a_OEGK_Abgearbeitete_Antraege_pro_Monat_2021_bis_Mai_2023_pro_Fachrichtung_postal_online_pro_Bundesland.csv"
    Beilage6a_filename = (
        DATA_DIR + "Beilage_6a_combined_tables.csv"
    )
    df_6a = pd.read_csv(Beilage6a_filename)

    df_6a = convert_month_year_to_date(df_6a)

    df_6a.rename(columns={"ÖGK-LS": "LST"}, inplace=True)

    df_6a["Bundesland_pretty"] = (
        df_6a["LST"].str.split("-", expand=True)[1].str.strip().map(LST_TO_BUNDESLAND)
    )
    # df_6a.loc[df_6a["LST"] == "Gesamt", "Bundesland_pretty"] = "Alle"
    df_6a = df_6a.set_index(["Date", "FG-Code", "LST"])

    export_to_csv(df_6a, new_filename)

def process_7():
    new_filename = "07_OEGK_Durchschnittliche_Bearbeitungszeit_pro_Monat_2023_postal_online_online_pro_Bundesland.csv"
    Beilage7_filename = (
        DATA_DIR + "Beilage_7_combined_tables.csv"
    )
    df_7 = pd.read_csv(Beilage7_filename)

    # Filter out rows with "Durchschnitt" in the Monat.Jahr column
    # We can calculate the average later on the fly
    df_7 = df_7[~df_7["Monat.Jahr"].str.contains("Durchschnitt", na=False)]

    df_7 = convert_month_year_to_date(df_7)

    df_7["Year"] = pd.Period("2023")

    df_7.rename(columns={"ÖGK-LS": "LST"}, inplace=True)
    df_7["Bundesland_pretty"] = (
        df_7["LST"].str.split("-", expand=True)[1].str.strip().map(LST_TO_BUNDESLAND)
    )
    # df_7.loc[df_7["LST"] == "Gesamt", "Bundesland_pretty"] = "Alle"

    df_7 = df_7.set_index(["Date", "LST"])

    export_to_csv(df_7, new_filename)

def process_7a():
    new_filename = "07a_OEGK_Durchschnittliche_Bearbeitungszeit_pro_Monat_2021_bis_Mai_2023_postal_online_online_pro_Bundesland.csv"
    Beilage7a_filename = (
        DATA_DIR + "Beilage_7a_combined_tables.csv"
    )
    df_7a = pd.read_csv(Beilage7a_filename)

    # Filter out rows with "Durchschnitt" in the Monat.Jahr column
    # We can calculate the average later on the fly
    df_7a = df_7a[~df_7a["Monat.Jahr"].str.contains("Durchschnitt", na=False)]
    df_7a = convert_month_year_to_date(df_7a)

    df_7a = df_7a.set_index(["Date"])

    df_7a.rename(columns={"ÖGK-LS": "LST"}, inplace=True)
    df_7a["Bundesland_pretty"] = (
        df_7a["LST"].str.split("-", expand=True)[1].str.strip().map(LST_TO_BUNDESLAND)
    )

    export_to_csv(df_7a, new_filename)

def process_8():
    new_filename = "08_OEGK_Betraege_MTD_Berufe_2021_2022_2023_Bundesweit.csv"
    Beilage8_filename = (
        DATA_DIR + "Beilage_8_combined_tables.csv"
    )
    df_8 = pd.read_csv(Beilage8_filename)

    df_8 = df_8[~df_8["Monat.Jahr"].str.contains("Durchschnitt", na=False)]

    df_8.rename(columns={"ÖGK-LS": "LST"}, inplace=True)
    df_8.rename(columns={"Monat.Jahr": "Year"}, inplace=True)

    df_8 = df_8.set_index(["Year", "FG-Code"])

    export_to_csv(df_8, new_filename)


def process_9():
    new_filename = "09_OEGK_Betraege_MTD_Berufe_2021_2022_2023_pro_Bundesland.csv"
    Beilage9_filename = (
        DATA_DIR + "Beilage_9_combined_tables.csv"
    )
    df_9 = pd.read_csv(Beilage9_filename)

    df_9 = df_9[~df_9["Monat.Jahr"].str.contains("Durchschnitt", na=False)]

    df_9.rename(columns={"ÖGK-LS": "LST"}, inplace=True)
    df_9.rename(columns={"Monat.Jahr": "Year"}, inplace=True)

    df_9["Bundesland_pretty"] = (
        df_9["LST"].str.split("-", expand=True)[1].str.strip().map(LST_TO_BUNDESLAND)
    )   

    df_9 = df_9.set_index(["Year", "FG-Code", "LST"])

    export_to_csv(df_9, new_filename)

def process_10():
    new_filename = "10_OEGK_Antraege_MTD_Berufe_pro_Monat_2021_2022_2023_postal_online_pro_Fachrichtung_Bundesweit_und_pro_Bundesland.csv"
    Beilage10_filename = (
        DATA_DIR + "Beilage_10_combined_tables.csv"
    )
    df_10 = pd.read_csv(Beilage10_filename) 

    df_10 = convert_month_year_to_date(df_10)

    df_10.rename(columns={"ÖGK-LS": "LST"}, inplace=True)

    df_10["Bundesland_pretty"] = df_10["LST"].apply(
        lambda x: (
            "Bundesweit"
            if x == "ÖGK"
            else LST_TO_BUNDESLAND.get(x.split("-")[1].strip(), x)
        )
    )

    # Fix the data for March 2022 where online data is incorrectly stored as Gesamt
    march_2022_mask = (df_10['Date'] == '2022-03') & (df_10['LST'] == 'ÖGK')
    if march_2022_mask.any():
        # Store the correct online values (currently in Gesamt column)
        online_values = df_10.loc[march_2022_mask, 'Gesamt'].copy()
        
        # Recalculate Gesamt as the sum of postal and online
        df_10.loc[march_2022_mask, 'online'] = online_values
        df_10.loc[march_2022_mask, 'Gesamt'] = df_10.loc[march_2022_mask, 'postal'] + df_10.loc[march_2022_mask, 'online']
        
        print("Fixed March 2022 data: moved online values from Gesamt column and recalculated totals")

    df_10 = df_10.set_index(["Date", "FG-Code", "LST"])

    export_to_csv(df_10, new_filename)

def process_11():
    new_filename = "11_OEGK_Bearbeitete_Antraege_MTD_Berufe_pro_Monat_2021_2022_2023_postal_online_pro_Fachrichtung_Bundesweit_und_pro_Bundesland.csv"
    Beilage11_filename = (
        DATA_DIR + "Beilage_11_combined_tables.csv"
    )
    df_11 = pd.read_csv(Beilage11_filename)

    df_11.rename(columns={"ÖGK-LS": "LST"}, inplace=True)

    df_11 = convert_month_year_to_date(df_11)

    df_11["Bundesland_pretty"] = (
        df_11["LST"].str.split("-", expand=True)[1].str.strip().map(LST_TO_BUNDESLAND)
    )
    # Calculate totals for each row group and compare with original
    df_calc = df_11.copy()
    df_calc['Calc_Total'] = df_calc['postal'] + df_calc['online']
    
    # Compare calculated vs original totals
    total_diff = df_calc['Calc_Total'] - df_calc['Gesamt']
    discrepancies = total_diff[total_diff != 0]
    
    if len(discrepancies) > 0:
        print("\nDiscrepancies found in Beilage 11 totals:")
        print(discrepancies)
        
        # Print detailed information about discrepancies
        for idx in discrepancies.index:
            row = df_calc.loc[idx]
            fg_code = row['FG-Code']
            date = row['Date']
            lst = row['LST']
            fachrichtung = row['Fachrichtung']
            postal = row['postal']
            online = row['online']
            gesamt = row['Gesamt']
            calc_total = row['Calc_Total']
            diff = calc_total - gesamt
            print(f"LST: {lst}, Date: {date}, FG-Code: {fg_code}, Fachrichtung: {fachrichtung}")
            print(f"postal: {postal}, online: {online}, Original Total: {gesamt}, Calculated Total: {calc_total}")
            print(f"Difference: {diff}")

            # Find rows with same FG-Code from month before and after
            all_months = df_calc['Date'].unique()
            current_idx = np.where(all_months == date)[0][0]
            
            # Get previous month if available
            prev_month = all_months[current_idx - 1] if current_idx > 0 else None
            # Get next month if available
            next_month = all_months[current_idx + 1] if current_idx < len(all_months) - 1 else None
            
            print(f"\nDiscrepancy details for {date}, FG-Code: {fg_code}")
            print(f"Current row: {row.to_dict()}")
            
            if prev_month:
                prev_rows = df_calc[(df_calc['Date'] == prev_month) & (df_calc['FG-Code'] == fg_code)]
                if not prev_rows.empty:
                    print(f"Previous month ({prev_month}): {prev_rows.iloc[0].to_dict()}")
            
            if next_month:
                next_rows = df_calc[(df_calc['Date'] == next_month) & (df_calc['FG-Code'] == fg_code)]
                if not next_rows.empty:
                    print(f"Next month ({next_month}): {next_rows.iloc[0].to_dict()}")
        
    # Keep calculated totals
    df_11['Gesamt'] = df_calc['Calc_Total']

    df_11 = df_11.set_index(["Date", "FG-Code", "LST"])
    
    export_to_csv(df_11, new_filename)

def process_12():
    new_filename = "12_OEGK_Durchschnittliche_Bearbeitungszeit_MTD_Berufe_pro_Monat_2023_postal_online_online_pro_Fachrichtung_Bundesweit_und_pro_Bundesland.csv"
    Beilage12_filename = (
        DATA_DIR + "Beilage_12_combined_tables.csv"
    )
    df_12 = pd.read_csv(Beilage12_filename)

    df_12.rename(columns={"ÖGK-LS": "LST"}, inplace=True)

    df_12 = df_12[~df_12["Monat.Jahr"].str.contains("Durchschnitt", na=False)]

    df_12 = convert_month_year_to_date(df_12)

    df_12["Bundesland_pretty"] = (
        df_12["LST"].str.split("-", expand=True)[1].str.strip().map(LST_TO_BUNDESLAND)
    )

    df_12 = df_12.set_index(["Date", "LST"])

    export_to_csv(df_12, new_filename)

def process_13():
    new_filename = (
        "13_OEGK_Refundierungen_Heilbehelfe_pro_Monat_2021_2022_2023_pro_Bundesland.csv"
    )
    Beilage13_filename = DATA_DIR_BEILAGE_13_14_15_16 + "Beilage_13.csv"

    # Read the CSV file
    df_13 = pd.read_csv(Beilage13_filename, low_memory=False)

    # Clean column names
    df_13.columns = [col.strip().lower() for col in df_13.columns]

    # Process monthly data for each year
    monthly_data = []

    # Process 2021 data (rows 14-23)
    data_2021 = df_13.iloc[14:23].copy()
    data_2021.columns = ['bundesland'] + list(range(1, 13))  # Rename columns to month numbers

    # Process 2022 data (rows 25-34)
    data_2022 = df_13.iloc[26:35].copy()
    data_2022.columns = ['bundesland'] + list(range(1, 13))

    # Process 2023 data (rows 36-45)
    data_2023 = df_13.iloc[38:47].copy()
    data_2023.columns = ['bundesland'] + list(range(1, 13))

    # Remove sum rows
    data_2021 = data_2021[data_2021['bundesland'] != 'Summe']
    data_2022 = data_2022[data_2022['bundesland'] != 'Summe']
    data_2023 = data_2023[data_2023['bundesland'] != 'Summe']

    # Create long format data
    for year, data in [('2021', data_2021), ('2022', data_2022), ('2023', data_2023)]:
        for month in range(1, 13):
            for _, row in data.iterrows():
                bundesland = row['bundesland']
                value = row[month]

                # Convert value from string with comma as decimal separator to float
                if isinstance(value, str):
                    try:
                        # Handle numeric values with German formatting (comma as decimal separator)
                        value = float(value.replace('.', '').replace(',', '.'))
                    except (ValueError, AttributeError):
                        # If conversion fails (e.g., for month names like 'Jänner'), set to NaN
                        value = float('nan')

                monthly_data.append({
                    'Date': pd.Period(f"{year}-{month:02d}", freq='M'),
                    'Bundesland': bundesland,
                    'Refundierung': value
                })

    # Create DataFrame from monthly data
    result_df = pd.DataFrame(monthly_data)

    # No need to convert Date as we're already using pandas Period
    # result_df['Date'] is already in datetime format from Period.start_time

    # Sort by Date and Bundesland
    result_df = result_df.sort_values(['Date', 'Bundesland'])

    # Set index for consistency with other processed files
    result_df = result_df.set_index(['Date', 'Bundesland'])

    export_to_csv(result_df, new_filename)

def process_14():
    new_filename = "14_OEGK_Antraege_Heilbehelfe_pro_Monat_2021_2022_2023_pro_Bundesland.csv"
    Beilage14_filename = (
        DATA_DIR_BEILAGE_13_14_15_16 + "Beilage_14.csv"
    )
    df_14 = pd.read_csv(Beilage14_filename)

    # Read the CSV file
    df_14 = pd.read_csv(Beilage14_filename, low_memory=False)

    # Clean column names
    df_14.columns = [col.strip().lower() for col in df_14.columns]

    # Process monthly data for each year
    monthly_data = []

    # Process 2021 data (rows 14-23)
    data_2021 = df_14.iloc[16:25].copy()
    data_2021.columns = ["bundesland"] + list(
        range(1, 13)
    )  # Rename columns to month numbers

    # Process 2022 data (rows 25-34)
    data_2022 = df_14.iloc[28:37].copy()
    data_2022.columns = ["bundesland"] + list(range(1, 13))

    # Process 2023 data (rows 36-45)
    data_2023 = df_14.iloc[40:49].copy()
    data_2023.columns = ["bundesland"] + list(range(1, 13))

    # Remove sum rows
    data_2021 = data_2021[data_2021["bundesland"] != "Summe"]
    data_2022 = data_2022[data_2022["bundesland"] != "Summe"]
    data_2023 = data_2023[data_2023["bundesland"] != "Summe"]

    # Create long format data
    for year, data in [("2021", data_2021), ("2022", data_2022), ("2023", data_2023)]:
        for month in range(1, 13):
            for _, row in data.iterrows():
                bundesland = row["bundesland"]
                value = row[month]

                # Convert value from string with comma as decimal separator to float
                if isinstance(value, str):
                    try:
                        # Handle numeric values with German formatting (comma as decimal separator)
                        value = float(value.replace(".", "").replace(",", "."))
                    except (ValueError, AttributeError):
                        # If conversion fails (e.g., for month names like 'Jänner'), set to NaN
                        value = float("nan")

                monthly_data.append(
                    {
                        "Date": pd.Period(f"{year}-{month:02d}", freq="M"),
                        "Bundesland": bundesland,
                        "Refundierung": value,
                    }
                )

    # Create DataFrame from monthly data
    result_df = pd.DataFrame(monthly_data)

    # No need to convert Date as we're already using pandas Period
    # result_df['Date'] is already in datetime format from Period.start_time

    # Sort by Date and Bundesland
    result_df = result_df.sort_values(["Date", "Bundesland"])

    # Set index for consistency with other processed files
    result_df = result_df.set_index(["Date", "Bundesland"])

    export_to_csv(result_df, new_filename)


def process_data():
    print("Processing data...")
    process_1()
    process_2()
    process_3()
    process_4()
    process_5()
    process_6()
    process_5a()
    process_6a()
    process_7()
    process_7a()
    process_8()
    process_9()
    process_10()
    process_11()
    process_12()
    process_13()
    process_14()
    print("Data processing complete.")
    print("Data saved to: " + EXPORT_DIR)


if __name__ == "__main__":
    process_data()
