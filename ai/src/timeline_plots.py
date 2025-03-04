import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Optional, Tuple, Union
import plotly.express as px
import plotly.graph_objects as go

from config import PLOT_SETTINGS, COLORS, PLOTS_DIR

class TimelinePlotter:
    def __init__(self, data_df: pd.DataFrame):
        """
        Initialize the TimelinePlotter with a DataFrame containing request and response data.
        
        Args:
            data_df (pd.DataFrame): DataFrame with request and response information
        """
        self.data = data_df
        self.setup_plot_style()
        
    def setup_plot_style(self):
        """Set up the plotting style using seaborn and matplotlib."""
        plt.style.use(PLOT_SETTINGS['style'])
        plt.rcParams['figure.figsize'] = PLOT_SETTINGS['figsize']
        plt.rcParams['figure.dpi'] = PLOT_SETTINGS['dpi']
        
    def plot_request_response_timeline(self, 
                                    save: bool = True,
                                    interactive: bool = False) -> Union[plt.Figure, go.Figure]:
        """
        Create a scatter plot showing request dates vs response times.
        
        Args:
            save (bool): Whether to save the plot to file
            interactive (bool): Whether to create an interactive plotly plot
            
        Returns:
            Union[plt.Figure, go.Figure]: The created figure
        """
        if interactive:
            fig = px.scatter(
                self.data,
                x='request_date',
                y='response_time_days',
                title='Request-Response Timeline',
                labels={
                    'request_date': 'Request Date',
                    'response_time_days': 'Response Time (Days)'
                },
                color='response_time_days',
                color_continuous_scale='viridis'
            )
            
            if save:
                fig.write_html(PLOTS_DIR / 'request_response_timeline.html')
            
            return fig
        
        else:
            fig, ax = plt.subplots()
            
            sns.scatterplot(
                data=self.data,
                x='request_date',
                y='response_time_days',
                ax=ax,
                color=COLORS['primary']
            )
            
            ax.set_title('Request-Response Timeline')
            ax.set_xlabel('Request Date')
            ax.set_ylabel('Response Time (Days)')
            
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            if save:
                plt.savefig(PLOTS_DIR / 'request_response_timeline.png')
            
            return fig
            
    def plot_request_volume(self,
                          frequency: str = 'M',
                          save: bool = True,
                          interactive: bool = False) -> Union[plt.Figure, go.Figure]:
        """
        Create a line or bar plot showing request volume over time.
        
        Args:
            frequency (str): Frequency for grouping ('D', 'W', 'M', 'Y')
            save (bool): Whether to save the plot to file
            interactive (bool): Whether to create an interactive plotly plot
            
        Returns:
            Union[plt.Figure, go.Figure]: The created figure
        """
        # Group data by time frequency
        volume_data = self.data.set_index('request_date').resample(frequency).size()
        
        if interactive:
            fig = px.line(
                volume_data,
                title='Request Volume Over Time',
                labels={'value': 'Number of Requests', 'request_date': 'Date'}
            )
            
            if save:
                fig.write_html(PLOTS_DIR / 'request_volume.html')
                
            return fig
            
        else:
            fig, ax = plt.subplots()
            
            volume_data.plot(
                kind='line',
                ax=ax,
                color=COLORS['primary']
            )
            
            ax.set_title('Request Volume Over Time')
            ax.set_xlabel('Date')
            ax.set_ylabel('Number of Requests')
            
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            if save:
                plt.savefig(PLOTS_DIR / 'request_volume.png')
                
            return fig
            
    def plot_response_time_distribution(self,
                                      save: bool = True,
                                      interactive: bool = False) -> Union[plt.Figure, go.Figure]:
        """
        Create a histogram and box plot of response times.
        
        Args:
            save (bool): Whether to save the plot to file
            interactive (bool): Whether to create an interactive plotly plot
            
        Returns:
            Union[plt.Figure, go.Figure]: The created figure
        """
        if interactive:
            fig = go.Figure()
            
            # Add histogram
            fig.add_trace(go.Histogram(
                x=self.data['response_time_days'],
                name='Distribution',
                nbinsx=30
            ))
            
            # Add box plot
            fig.add_trace(go.Box(
                x=self.data['response_time_days'],
                name='Box Plot'
            ))
            
            fig.update_layout(
                title='Response Time Distribution',
                xaxis_title='Response Time (Days)',
                yaxis_title='Count'
            )
            
            if save:
                fig.write_html(PLOTS_DIR / 'response_time_distribution.html')
                
            return fig
            
        else:
            fig, (ax1, ax2) = plt.subplots(2, 1, height_ratios=[3, 1])
            
            # Histogram
            sns.histplot(
                data=self.data,
                x='response_time_days',
                ax=ax1,
                color=COLORS['primary']
            )
            ax1.set_title('Response Time Distribution')
            
            # Box plot
            sns.boxplot(
                data=self.data,
                x='response_time_days',
                ax=ax2,
                color=COLORS['primary']
            )
            
            plt.tight_layout()
            
            if save:
                plt.savefig(PLOTS_DIR / 'response_time_distribution.png')
                
            return fig

if __name__ == "__main__":
    # Example usage
    from data_processor import DataProcessor
    
    # Create sample data
    processor = DataProcessor(
        anfragen_dir="../raw_data/alle_Anfragen_Beantwortungen/Anfragen/pdfs",
        beantwortungen_dir="../raw_data/alle_Anfragen_Beantwortungen/Beantwortungen/pdfs"
    )
    df = processor.create_master_dataframe()
    
    # Create plotter and generate plots
    plotter = TimelinePlotter(df)
    plotter.plot_request_response_timeline()
    plotter.plot_request_volume()
    plotter.plot_response_time_distribution() 