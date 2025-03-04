import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import altair as alt
from IPython.display import display, HTML

# Load the data
Beilage1_filename = "../raw_data/extracted_data/csv_files/Beilage_1_combined_tables.csv"
df = pd.read_csv(Beilage1_filename)

# Function to convert to Euro format
def convert_to_euro(column):
    return pd.to_numeric(column).map("€{:,.2f}".format)

# Group by Year and LST
if 'Year' in df.columns and 'LST' in df.columns:
    grouped_df = df.groupby(['Year', 'LST']).agg({
        'Refundierungen': 'sum',
        'Rechnungsbeträge': 'sum'
    }).reset_index()
else:
    # If the data is already in the grouped format, we'll use it as is
    grouped_df = df.copy()
    # Make sure we have the right columns
    if 'Refundierungen' not in grouped_df.columns or 'Rechnungsbeträge' not in grouped_df.columns:
        print("Warning: Expected columns not found in the dataset")

# Create a function to generate all visualizations
def generate_visualizations(df):
    """Generate visualizations using different libraries"""
    
    # Make sure we have numeric data
    df['Refundierungen'] = pd.to_numeric(df['Refundierungen'], errors='coerce')
    df['Rechnungsbeträge'] = pd.to_numeric(df['Rechnungsbeträge'], errors='coerce')
    
    # Calculate the ratio
    df['Refund_Ratio'] = df['Refundierungen'] / df['Rechnungsbeträge']
    
    # 1. Matplotlib visualization
    plt.figure(figsize=(12, 6))
    x = np.arange(len(df))
    width = 0.35
    
    plt.bar(x - width/2, df['Refundierungen'], width, label='Refundierungen')
    plt.bar(x + width/2, df['Rechnungsbeträge'], width, label='Rechnungsbeträge')
    
    plt.xlabel('LST')
    plt.ylabel('Amount (€)')
    plt.title('Comparison of Refundierungen and Rechnungsbeträge by LST (Matplotlib)')
    plt.xticks(x, df['LST'] if 'LST' in df.columns else [f"Item {i+1}" for i in range(len(df))])
    plt.legend()
    plt.tight_layout()
    plt.savefig('matplotlib_visualization.png')
    plt.close()
    
    # 2. Seaborn visualization
    plt.figure(figsize=(12, 6))
    melted_df = pd.melt(df, 
                        id_vars=['Year', 'LST'] if 'Year' in df.columns and 'LST' in df.columns else ['LST'],
                        value_vars=['Refundierungen', 'Rechnungsbeträge'],
                        var_name='Type', value_name='Amount')
    
    sns.barplot(x='LST', y='Amount', hue='Type', data=melted_df)
    plt.title('Comparison of Refundierungen and Rechnungsbeträge by LST (Seaborn)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('seaborn_visualization.png')
    plt.close()
    
    # 3. Plotly visualization
    fig = px.bar(melted_df, x='LST', y='Amount', color='Type', barmode='group',
                title='Comparison of Refundierungen and Rechnungsbeträge by LST (Plotly)',
                labels={'Amount': 'Amount (€)', 'LST': 'LST', 'Type': 'Type'})
    fig.write_html('plotly_visualization.html')
    
    # 4. Altair visualization
    chart = alt.Chart(melted_df).mark_bar().encode(
        x=alt.X('LST:N', title='LST'),
        y=alt.Y('Amount:Q', title='Amount (€)'),
        color=alt.Color('Type:N', title='Type'),
        column=alt.Column('Year:N', title='Year') if 'Year' in melted_df.columns else None
    ).properties(
        title='Comparison of Refundierungen and Rechnungsbeträge by LST (Altair)'
    )
    chart.save('altair_visualization.html')
    
    # 5. Bonus: Refund Ratio visualization with Plotly
    fig_ratio = px.bar(df, x='LST', y='Refund_Ratio', 
                      title='Refund Ratio by LST (Refundierungen / Rechnungsbeträge)',
                      labels={'Refund_Ratio': 'Ratio', 'LST': 'LST'})
    fig_ratio.update_traces(marker_color='green')
    fig_ratio.write_html('refund_ratio_visualization.html')
    
    print("Visualizations generated successfully!")
    print("Files created:")
    print("- matplotlib_visualization.png")
    print("- seaborn_visualization.png")
    print("- plotly_visualization.html")
    print("- altair_visualization.html")
    print("- refund_ratio_visualization.html")

# Run the visualization function
generate_visualizations(grouped_df)

# Display information about the environment
import sys
import platform

print("\nEnvironment Information:")
print(f"Python version: {sys.version}")
print(f"Platform: {platform.platform()}")
print(f"Pandas version: {pd.__version__}")
print(f"NumPy version: {np.__version__}")
print(f"Matplotlib version: {plt.__version__}")
print(f"Seaborn version: {sns.__version__}")
print(f"Plotly version: {px.__version__}")
print(f"Altair version: {alt.__version__}") 