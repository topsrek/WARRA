import subprocess
import sys
import os
import importlib.util

def check_and_install_package(package_name):
    """Check if a package is installed, and install it if not."""
    spec = importlib.util.find_spec(package_name)
    if spec is None:
        print(f"{package_name} is not installed. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"{package_name} has been installed.")
    else:
        print(f"{package_name} is already installed.")

def main():
    # List of packages to check and install
    packages = ["matplotlib", "seaborn", "plotly", "altair", "ipython"]
    
    # Check and install packages
    print("Checking and installing required packages...")
    for package in packages:
        check_and_install_package(package)
    
    # Now import the required packages
    import pandas as pd
    import numpy as np
    import matplotlib
    import matplotlib.pyplot as plt
    import seaborn as sns
    import plotly
    import plotly.express as px
    import altair as alt
    from IPython.display import display, HTML
    
    # Print environment information
    print("\nEnvironment Information:")
    print(f"Python version: {sys.version}")
    print(f"Platform: {os.name}")
    print(f"Pandas version: {pd.__version__}")
    print(f"NumPy version: {np.__version__}")
    print(f"Matplotlib version: {matplotlib.__version__}")
    print(f"Seaborn version: {sns.__version__}")
    print(f"Plotly version: {plotly.__version__}")
    print(f"Altair version: {alt.__version__}")
    
    # Load the data
    try:
        Beilage1_filename = "../raw_data/extracted_data/csv_files/Beilage_1_combined_tables.csv"
        df = pd.read_csv(Beilage1_filename)
        print(f"\nData loaded successfully from {Beilage1_filename}")
        print(f"Dataset Shape: {df.shape}")
    except Exception as e:
        print(f"Error loading data: {e}")
        # Create sample data for demonstration
        print("Creating sample data for demonstration...")
        df = pd.DataFrame({
            'Year': ['2023']*5 + ['2022']*5,
            'LST': ['ÖGK-W', 'ÖGK-N', 'ÖGK-B', 'ÖGK-O', 'ÖGK-ST'] * 2,
            'Refundierungen': [44992965.36, 31938943.74, 4715404.08, 29930360.88, 25873975.82,
                              42000000.00, 30000000.00, 4500000.00, 28000000.00, 24000000.00],
            'Rechnungsbeträge': [134065655.76, 89851098.22, 14315993.59, 77534663.23, 70452229.91,
                                125000000.00, 85000000.00, 13000000.00, 75000000.00, 68000000.00]
        })
    
    # Function to convert to Euro format
    def convert_to_euro(column):
        return pd.to_numeric(column).map("€{:,.2f}".format)
    
    # Make sure we have numeric data
    df['Refundierungen'] = pd.to_numeric(df['Refundierungen'], errors='coerce')
    df['Rechnungsbeträge'] = pd.to_numeric(df['Rechnungsbeträge'], errors='coerce')
    
    # Calculate the ratio
    df['Refund_Ratio'] = df['Refundierungen'] / df['Rechnungsbeträge']
    
    # Create a melted dataframe for easier visualization
    id_vars = ['Year', 'LST'] if 'Year' in df.columns and 'LST' in df.columns else df.index.names
    melted_df = pd.melt(df, 
                       id_vars=id_vars,
                       value_vars=['Refundierungen', 'Rechnungsbeträge'],
                       var_name='Type', value_name='Amount')
    
    # Create output directory if it doesn't exist
    output_dir = "visualizations"
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Matplotlib visualization
    print("\nCreating Matplotlib visualization...")
    plt.figure(figsize=(12, 6))
    x = np.arange(len(df))
    width = 0.35
    
    plt.bar(x - width/2, df['Refundierungen'], width, label='Refundierungen')
    plt.bar(x + width/2, df['Rechnungsbeträge'], width, label='Rechnungsbeträge')
    
    plt.xlabel('LST')
    plt.ylabel('Amount (€)')
    plt.title('Comparison of Refundierungen and Rechnungsbeträge by LST (Matplotlib)')
    
    # Handle different index types
    if 'LST' in df.columns:
        plt.xticks(x, df['LST'])
    else:
        plt.xticks(x, range(len(df)))
        
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'matplotlib_visualization.png'))
    plt.close()
    
    # 2. Seaborn visualization
    print("Creating Seaborn visualization...")
    plt.figure(figsize=(12, 6))
    
    # Determine the x-axis column
    x_col = 'LST' if 'LST' in melted_df.columns else 'index'
    
    sns.barplot(x=x_col, y='Amount', hue='Type', data=melted_df)
    plt.title('Comparison of Refundierungen and Rechnungsbeträge by LST (Seaborn)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'seaborn_visualization.png'))
    plt.close()
    
    # 3. Plotly visualization
    print("Creating Plotly visualization...")
    
    # Determine the x-axis column
    x_col = 'LST' if 'LST' in melted_df.columns else 'index'
    
    fig = px.bar(melted_df, x=x_col, y='Amount', color='Type', barmode='group',
                title='Comparison of Refundierungen and Rechnungsbeträge by LST (Plotly)',
                labels={'Amount': 'Amount (€)', 'LST': 'LST', 'Type': 'Type'})
    fig.write_html(os.path.join(output_dir, 'plotly_visualization.html'))
    
    # 4. Altair visualization
    print("Creating Altair visualization...")
    
    # Determine the x-axis column
    x_col = 'LST' if 'LST' in melted_df.columns else 'index'
    
    chart = alt.Chart(melted_df).mark_bar().encode(
        x=alt.X(f'{x_col}:N', title='LST'),
        y=alt.Y('Amount:Q', title='Amount (€)'),
        color=alt.Color('Type:N', title='Type'),
        column=alt.Column('Year:N', title='Year') if 'Year' in melted_df.columns else None
    ).properties(
        title='Comparison of Refundierungen and Rechnungsbeträge by LST (Altair)'
    )
    chart.save(os.path.join(output_dir, 'altair_visualization.html'))
    
    # 5. Bonus: Refund Ratio visualization with Plotly
    print("Creating Refund Ratio visualization...")
    
    # Determine the x-axis column
    x_col = 'LST' if 'LST' in df.columns else 'index'
    
    fig_ratio = px.bar(df, x=x_col, y='Refund_Ratio', 
                      title='Refund Ratio by LST (Refundierungen / Rechnungsbeträge)',
                      labels={'Refund_Ratio': 'Ratio', 'LST': 'LST'})
    fig_ratio.update_traces(marker_color='green')
    fig_ratio.write_html(os.path.join(output_dir, 'refund_ratio_visualization.html'))
    
    print("\nVisualizations generated successfully!")
    print(f"Files created in {os.path.abspath(output_dir)}:")
    print("- matplotlib_visualization.png")
    print("- seaborn_visualization.png")
    print("- plotly_visualization.html")
    print("- altair_visualization.html")
    print("- refund_ratio_visualization.html")

if __name__ == "__main__":
    main() 