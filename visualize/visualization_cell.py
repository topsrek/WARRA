# Import visualization libraries
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import altair as alt
from IPython.display import display, HTML

# Make sure we have numeric data
df_1['Refundierungen'] = pd.to_numeric(df_1['Refundierungen'], errors='coerce')
df_1['Rechnungsbeträge'] = pd.to_numeric(df_1['Rechnungsbeträge'], errors='coerce')

# Calculate the ratio
df_1['Refund_Ratio'] = df_1['Refundierungen'] / df_1['Rechnungsbeträge']

# Create a melted dataframe for easier visualization
melted_df = pd.melt(df_1, 
                   id_vars=['Year', 'LST'] if 'Year' in df_1.columns and 'LST' in df_1.columns else df_1.index.names,
                   value_vars=['Refundierungen', 'Rechnungsbeträge'],
                   var_name='Type', value_name='Amount')

# Print environment information
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

# 1. Matplotlib visualization
plt.figure(figsize=(12, 6))
x = np.arange(len(df_1))
width = 0.35

plt.bar(x - width/2, df_1['Refundierungen'], width, label='Refundierungen')
plt.bar(x + width/2, df_1['Rechnungsbeträge'], width, label='Rechnungsbeträge')

plt.xlabel('LST')
plt.ylabel('Amount (€)')
plt.title('Comparison of Refundierungen and Rechnungsbeträge by LST (Matplotlib)')
plt.xticks(x, df_1.index.get_level_values('LST') if isinstance(df_1.index, pd.MultiIndex) else range(len(df_1)))
plt.legend()
plt.tight_layout()
plt.show()

# 2. Seaborn visualization
plt.figure(figsize=(12, 6))
sns.barplot(x='LST', y='Amount', hue='Type', data=melted_df.reset_index())
plt.title('Comparison of Refundierungen and Rechnungsbeträge by LST (Seaborn)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# 3. Plotly visualization
fig = px.bar(melted_df.reset_index(), x='LST', y='Amount', color='Type', barmode='group',
            title='Comparison of Refundierungen and Rechnungsbeträge by LST (Plotly)',
            labels={'Amount': 'Amount (€)', 'LST': 'LST', 'Type': 'Type'})
fig.show()

# 4. Altair visualization
chart = alt.Chart(melted_df.reset_index()).mark_bar().encode(
    x=alt.X('LST:N', title='LST'),
    y=alt.Y('Amount:Q', title='Amount (€)'),
    color=alt.Color('Type:N', title='Type'),
    column=alt.Column('Year:N', title='Year') if 'Year' in melted_df.columns else None
).properties(
    title='Comparison of Refundierungen and Rechnungsbeträge by LST (Altair)'
)
display(chart)

# 5. Bonus: Refund Ratio visualization with Plotly
fig_ratio = px.bar(df_1.reset_index(), x='LST', y='Refund_Ratio', 
                  title='Refund Ratio by LST (Refundierungen / Rechnungsbeträge)',
                  labels={'Refund_Ratio': 'Ratio', 'LST': 'LST'})
fig_ratio.update_traces(marker_color='green')
fig_ratio.show() 