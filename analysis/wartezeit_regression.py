import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error
import statsmodels.api as sm
import os

def prepare_bearbeitungszeit_data():
    """Prepare and merge the processing time data using the successful approach from the plotting script."""
    # Read the CSV files
    df_2023 = pd.read_csv(
        "D:/DEV/WU/WARRA/data/csv/07_OEGK_Durchschnittliche_Bearbeitungszeit_pro_Monat_2023_postal_online_online_pro_Bundesland.csv"
    )
    df_historical = pd.read_csv(
        "D:/DEV/WU/WARRA/data/csv/07a_OEGK_Durchschnittliche_Bearbeitungszeit_pro_Monat_2021_bis_Mai_2023_postal_online_online_pro_Bundesland.csv"
    )
    
    # Convert dates to datetime
    df_2023["Date"] = pd.to_datetime(df_2023["Date"])
    df_historical["Date"] = pd.to_datetime(df_historical["Date"])
    
    # Combine the data
    overlap_start = df_2023["Date"].min()
    df_combined = pd.concat([
        df_historical[df_historical["Date"] < overlap_start],
        df_2023
    ]).sort_values(["Date", "Bundesland_pretty"])
    
    return df_combined

def prepare_antraege_data():
    """Prepare the application volume data."""
    # Read the CSV file
    df_antraege = pd.read_csv(
        "D:/DEV/WU/WARRA/data/csv/04_OEGK_Antraege_pro_Monat_2023_pro_Fachrichtung_online_postal_pro_Bundesland.csv"
    )
    
    # Convert date to datetime
    df_antraege["Date"] = pd.to_datetime(df_antraege["Date"])
    
    # Group by Date and Bundesland to get total applications
    df_grouped = df_antraege.groupby(["Date", "Bundesland_pretty"]).agg({
        "postal": "sum",
        "online": "sum",
        "Gesamt": "sum"
    }).reset_index()
    
    # Rename columns to avoid confusion
    df_grouped = df_grouped.rename(columns={
        "postal": "postal_vol",
        "online": "online_vol",
        "Gesamt": "total_vol"
    })
    
    return df_grouped

def run_regression_analysis():
    """Run regression analysis to analyze the impact of application volume on processing time."""
    # Prepare data
    df_bearbeitungszeit = prepare_bearbeitungszeit_data()
    df_antraege = prepare_antraege_data()
    
    # Print column names for debugging
    print("Bearbeitungszeit columns:", df_bearbeitungszeit.columns.tolist())
    print("Antraege columns:", df_antraege.columns.tolist())
    
    # Merge the datasets
    df_merged = pd.merge(
        df_bearbeitungszeit,
        df_antraege,
        on=["Date", "Bundesland_pretty"],
        how='inner'  # Only keep matching rows
    )
    
    print("\nMerged columns:", df_merged.columns.tolist())
    print("\nSample of merged data:")
    print(df_merged[["Date", "Bundesland_pretty", "Postal", "OnlineMeine", "postal_vol", "online_vol"]].head())
    
    # Prepare variables for regression
    X = df_merged[["postal_vol", "online_vol"]]  # Independent variables: application volumes
    y_postal = df_merged["Postal"]  # Dependent variable: postal processing time
    y_online = df_merged["OnlineMeine"]  # Dependent variable: online processing time
    
    # Add constant for statsmodels
    X_sm = sm.add_constant(X)
    
    # Run regression for postal processing time
    model_postal = sm.OLS(y_postal, X_sm)
    results_postal = model_postal.fit()
    
    # Run regression for online processing time
    model_online = sm.OLS(y_online, X_sm)
    results_online = model_online.fit()
    
    # Print results
    print("\nRegression Results for Postal Processing Time:")
    print("=============================================")
    print(results_postal.summary().tables[1])
    print("\nR-squared:", results_postal.rsquared)
    print("Adjusted R-squared:", results_postal.rsquared_adj)
    
    print("\nRegression Results for Online Processing Time:")
    print("=============================================")
    print(results_online.summary().tables[1])
    print("\nR-squared:", results_online.rsquared)
    print("Adjusted R-squared:", results_online.rsquared_adj)
    
    # Additional analysis by Bundesland
    print("\nAnalysis by Bundesland:")
    print("=====================")
    for bundesland in df_merged["Bundesland_pretty"].unique():
        df_bl = df_merged[df_merged["Bundesland_pretty"] == bundesland]
        
        X_bl = df_bl[["postal_vol", "online_vol"]]
        y_postal_bl = df_bl["Postal"]
        y_online_bl = df_bl["OnlineMeine"]
        
        X_bl_sm = sm.add_constant(X_bl)
        
        # Postal regression
        model_postal_bl = sm.OLS(y_postal_bl, X_bl_sm)
        results_postal_bl = model_postal_bl.fit()
        
        # Online regression
        model_online_bl = sm.OLS(y_online_bl, X_bl_sm)
        results_online_bl = model_online_bl.fit()
        
        print(f"\n{bundesland}:")
        print(f"Postal R-squared: {results_postal_bl.rsquared:.3f}")
        print(f"Online R-squared: {results_online_bl.rsquared:.3f}")

if __name__ == "__main__":
    run_regression_analysis()
