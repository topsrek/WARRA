import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Union, Tuple, Optional
import plotly.express as px
import plotly.graph_objects as go
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from config import PLOT_SETTINGS, COLORS, PLOTS_DIR

class INRAnalyzer:
    def __init__(self, data_df: pd.DataFrame):
        """
        Initialize the INRAnalyzer with a DataFrame containing INR data.
        
        Args:
            data_df (pd.DataFrame): DataFrame with INR information
        """
        self.data = data_df
        self.setup_plot_style()
        
    def setup_plot_style(self):
        """Set up the plotting style using seaborn and matplotlib."""
        plt.style.use(PLOT_SETTINGS['style'])
        plt.rcParams['figure.figsize'] = PLOT_SETTINGS['figsize']
        plt.rcParams['figure.dpi'] = PLOT_SETTINGS['dpi']
        
    def plot_inr_timeline(self,
                         save: bool = True,
                         interactive: bool = False) -> Union[plt.Figure, go.Figure]:
        """
        Create a scatter plot showing INR numbers over time.
        
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
                y='request_inr',
                title='INR Numbers Over Time',
                labels={
                    'request_date': 'Date',
                    'request_inr': 'INR Number'
                }
            )
            
            if save:
                fig.write_html(PLOTS_DIR / 'inr_timeline.html')
                
            return fig
            
        else:
            fig, ax = plt.subplots()
            
            sns.scatterplot(
                data=self.data,
                x='request_date',
                y='request_inr',
                ax=ax,
                color=COLORS['primary']
            )
            
            ax.set_title('INR Numbers Over Time')
            ax.set_xlabel('Date')
            ax.set_ylabel('INR Number')
            
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            if save:
                plt.savefig(PLOTS_DIR / 'inr_timeline.png')
                
            return fig
            
    def plot_inr_distribution(self,
                            save: bool = True,
                            interactive: bool = False) -> Union[plt.Figure, go.Figure]:
        """
        Create a histogram of INR numbers.
        
        Args:
            save (bool): Whether to save the plot to file
            interactive (bool): Whether to create an interactive plotly plot
            
        Returns:
            Union[plt.Figure, go.Figure]: The created figure
        """
        if interactive:
            fig = px.histogram(
                self.data,
                x='request_inr',
                title='Distribution of INR Numbers',
                labels={'request_inr': 'INR Number'},
                nbins=30
            )
            
            if save:
                fig.write_html(PLOTS_DIR / 'inr_distribution.html')
                
            return fig
            
        else:
            fig, ax = plt.subplots()
            
            sns.histplot(
                data=self.data,
                x='request_inr',
                ax=ax,
                color=COLORS['primary'],
                bins=30
            )
            
            ax.set_title('Distribution of INR Numbers')
            ax.set_xlabel('INR Number')
            ax.set_ylabel('Count')
            
            plt.tight_layout()
            
            if save:
                plt.savefig(PLOTS_DIR / 'inr_distribution.png')
                
            return fig
            
    def analyze_inr_gaps(self,
                        save: bool = True,
                        interactive: bool = False) -> Union[plt.Figure, go.Figure]:
        """
        Analyze and plot gaps between consecutive INR numbers.
        
        Args:
            save (bool): Whether to save the plot to file
            interactive (bool): Whether to create an interactive plotly plot
            
        Returns:
            Union[plt.Figure, go.Figure]: The created figure
        """
        # Calculate gaps between consecutive INR numbers
        sorted_inrs = self.data.sort_values('request_inr')
        gaps = sorted_inrs['request_inr'].diff()
        
        if interactive:
            fig = px.histogram(
                x=gaps,
                title='Distribution of Gaps Between Consecutive INR Numbers',
                labels={'x': 'Gap Size'},
                nbins=30
            )
            
            if save:
                fig.write_html(PLOTS_DIR / 'inr_gaps.html')
                
            return fig
            
        else:
            fig, ax = plt.subplots()
            
            sns.histplot(
                x=gaps,
                ax=ax,
                color=COLORS['primary'],
                bins=30
            )
            
            ax.set_title('Distribution of Gaps Between Consecutive INR Numbers')
            ax.set_xlabel('Gap Size')
            ax.set_ylabel('Count')
            
            plt.tight_layout()
            
            if save:
                plt.savefig(PLOTS_DIR / 'inr_gaps.png')
                
            return fig
            
    def analyze_inr_clusters(self,
                           n_clusters: int = 5,
                           save: bool = True,
                           interactive: bool = False) -> Union[plt.Figure, go.Figure]:
        """
        Perform cluster analysis on INR numbers and their temporal distribution.
        
        Args:
            n_clusters (int): Number of clusters for K-means
            save (bool): Whether to save the plot to file
            interactive (bool): Whether to create an interactive plotly plot
            
        Returns:
            Union[plt.Figure, go.Figure]: The created figure
        """
        # Prepare data for clustering
        X = self.data[['request_inr']].copy()
        X['days_since_start'] = (self.data['request_date'] - self.data['request_date'].min()).dt.days
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Perform clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(X_scaled)
        
        if interactive:
            fig = px.scatter(
                x=self.data['request_date'],
                y=self.data['request_inr'],
                color=clusters,
                title='INR Clusters Over Time',
                labels={
                    'x': 'Date',
                    'y': 'INR Number',
                    'color': 'Cluster'
                }
            )
            
            if save:
                fig.write_html(PLOTS_DIR / 'inr_clusters.html')
                
            return fig
            
        else:
            fig, ax = plt.subplots()
            
            scatter = ax.scatter(
                self.data['request_date'],
                self.data['request_inr'],
                c=clusters,
                cmap='viridis'
            )
            
            ax.set_title('INR Clusters Over Time')
            ax.set_xlabel('Date')
            ax.set_ylabel('INR Number')
            
            plt.colorbar(scatter, label='Cluster')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            if save:
                plt.savefig(PLOTS_DIR / 'inr_clusters.png')
                
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
    
    # Create analyzer and generate plots
    analyzer = INRAnalyzer(df)
    analyzer.plot_inr_timeline()
    analyzer.plot_inr_distribution()
    analyzer.analyze_inr_gaps()
    analyzer.analyze_inr_clusters() 