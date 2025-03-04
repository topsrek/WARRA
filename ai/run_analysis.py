#!/usr/bin/env python3
import argparse
import logging
from pathlib import Path

from src.data_setup import main as setup_data
from src.main import main as run_analysis

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Run PDF data analysis pipeline')
    parser.add_argument('--skip-setup', action='store_true',
                       help='Skip data setup step (use existing data)')
    parser.add_argument('--interactive-only', action='store_true',
                       help='Generate only interactive plots')
    parser.add_argument('--static-only', action='store_true',
                       help='Generate only static plots')
    return parser.parse_args()

def main():
    """Main function to run setup and analysis."""
    # Parse arguments
    args = parse_args()
    
    try:
        # Run data setup if not skipped
        if not args.skip_setup:
            print("Setting up data directories and copying data...")
            setup_data()
        
        # Run analysis
        print("Running analysis pipeline...")
        if args.interactive_only:
            print("Generating interactive plots only...")
            # Import and run only interactive analysis
            from src.main import AnalysisPipeline
            pipeline = AnalysisPipeline()
            pipeline.run_pipeline(interactive=True)
        elif args.static_only:
            print("Generating static plots only...")
            # Import and run only static analysis
            from src.main import AnalysisPipeline
            pipeline = AnalysisPipeline()
            pipeline.run_pipeline(interactive=False)
        else:
            print("Generating both static and interactive plots...")
            run_analysis()
            
        print("Analysis completed successfully!")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        raise

if __name__ == "__main__":
    main() 