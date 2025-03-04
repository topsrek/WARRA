import logging
from pathlib import Path
import pandas as pd
from datetime import datetime

from data_processor import DataProcessor
from timeline_plots import TimelinePlotter
from inr_analysis import INRAnalyzer
from config import (
    ANFRAGEN_DIR, 
    BEANTWORTUNGEN_DIR, 
    PROCESSED_DATA_DIR,
    LOGGING
)

# Setup logging
logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)

class AnalysisPipeline:
    def __init__(self):
        """Initialize the analysis pipeline."""
        self.processor = None
        self.plotter = None
        self.analyzer = None
        self.data = None
        
    def setup(self):
        """Set up the data processor and load data."""
        logger.info("Setting up analysis pipeline")
        self.processor = DataProcessor(
            anfragen_dir=ANFRAGEN_DIR,
            beantwortungen_dir=BEANTWORTUNGEN_DIR
        )
        
    def process_data(self):
        """Process the raw data and create master DataFrame."""
        logger.info("Processing data")
        self.data = self.processor.create_master_dataframe()
        
        # Save processed data
        output_file = PROCESSED_DATA_DIR / f"processed_data_{datetime.now().strftime('%Y%m%d')}.csv"
        self.data.to_csv(output_file, index=False)
        logger.info(f"Saved processed data to {output_file}")
        
    def generate_timeline_plots(self, interactive: bool = False):
        """Generate timeline-based visualizations."""
        logger.info("Generating timeline plots")
        self.plotter = TimelinePlotter(self.data)
        
        # Generate plots
        self.plotter.plot_request_response_timeline(interactive=interactive)
        self.plotter.plot_request_volume(interactive=interactive)
        self.plotter.plot_response_time_distribution(interactive=interactive)
        
    def analyze_inr_patterns(self, interactive: bool = False):
        """Analyze INR number patterns."""
        logger.info("Analyzing INR patterns")
        self.analyzer = INRAnalyzer(self.data)
        
        # Generate analysis plots
        self.analyzer.plot_inr_timeline(interactive=interactive)
        self.analyzer.plot_inr_distribution(interactive=interactive)
        self.analyzer.analyze_inr_gaps(interactive=interactive)
        self.analyzer.analyze_inr_clusters(interactive=interactive)
        
    def run_pipeline(self, interactive: bool = False):
        """Run the complete analysis pipeline."""
        try:
            logger.info("Starting analysis pipeline")
            
            # Setup and process data
            self.setup()
            self.process_data()
            
            # Generate visualizations
            self.generate_timeline_plots(interactive)
            self.analyze_inr_patterns(interactive)
            
            logger.info("Analysis pipeline completed successfully")
            
        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}")
            raise

def main():
    """Main function to run the analysis."""
    pipeline = AnalysisPipeline()
    
    # Run pipeline with both static and interactive plots
    logger.info("Running pipeline with static plots")
    pipeline.run_pipeline(interactive=False)
    
    logger.info("Running pipeline with interactive plots")
    pipeline.run_pipeline(interactive=True)

if __name__ == "__main__":
    main() 