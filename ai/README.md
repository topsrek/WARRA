# PDF Data Analysis and Visualization

This project provides tools for analyzing and visualizing data from PDF requests and responses. It focuses on temporal analysis, INR number patterns, and response time distributions.

## Project Structure

```
ai/
├── src/
│   ├── data_processor.py   # Data processing and preparation
│   ├── data_setup.py      # Data setup and copying
│   ├── timeline_plots.py   # Time-based visualizations
│   ├── inr_analysis.py     # INR number analysis
│   ├── utils.py           # Helper functions
│   ├── config.py          # Configuration settings
│   └── main.py           # Main analysis pipeline
├── data/
│   ├── raw/              # Raw copied data
│   │   ├── anfragen/     # Request PDFs
│   │   └── beantwortungen/ # Response PDFs
│   └── processed/        # Processed data files
├── output/
│   ├── plots/            # Generated static plots
│   └── dashboards/       # Interactive dashboards
├── logs/                 # Log files
├── run_analysis.py       # Analysis runner script
├── requirements.txt      # Python dependencies
└── README.md            # Project documentation
```

## Features

1. **Data Processing**
   - Extract information from PDF directory names
   - Create structured DataFrame for analysis
   - Calculate response times and other metrics

2. **Timeline Analysis**
   - Request-Response timeline visualization
   - Request volume over time
   - Response time distribution

3. **INR Analysis**
   - INR number patterns over time
   - Distribution analysis
   - Gap analysis between consecutive INR numbers
   - Cluster analysis of INR patterns

4. **Visualization Options**
   - Static plots using matplotlib/seaborn
   - Interactive plots using plotly
   - Option to save plots as PNG or HTML

## Setup

1. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Quick start - run complete analysis:
   ```bash
   python run_analysis.py
   ```

2. Command line options:
   ```bash
   # Skip data setup (use existing data)
   python run_analysis.py --skip-setup

   # Generate only interactive plots
   python run_analysis.py --interactive-only

   # Generate only static plots
   python run_analysis.py --static-only
   ```

3. Python API usage:
   ```python
   from src.main import AnalysisPipeline

   # Create and run pipeline
   pipeline = AnalysisPipeline()
   pipeline.run_pipeline(interactive=True)  # or False for static plots
   ```

## Output

The analysis generates several types of output:

1. **Processed Data**
   - CSV files in `data/processed/` containing structured data

2. **Static Plots** (in `output/plots/`)
   - Request-Response timeline
   - Request volume over time
   - Response time distribution
   - INR number patterns
   - INR distribution
   - Gap analysis
   - Cluster analysis

3. **Interactive Plots** (in `output/plots/`)
   - HTML files with interactive versions of all plots
   - Can be opened in any web browser

4. **Logs**
   - Detailed logs in `logs/app.log`
   - Console output for quick status

## Configuration

The `config.py` file contains various settings that can be adjusted:
- Plot styles and colors
- Output directories
- Date formats
- Dashboard settings
- Logging configuration

## Dependencies

Major dependencies include:
- pandas
- matplotlib
- seaborn
- plotly
- scikit-learn
- dash (for interactive dashboards)

See `requirements.txt` for complete list and version information.

## Development

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

### Adding New Features

To add new visualizations or analyses:

1. Create a new module in `src/`
2. Update `main.py` to include the new functionality
3. Add configuration in `config.py` if needed
4. Update documentation

## Troubleshooting

Common issues and solutions:

1. **Data not found**
   - Ensure you've run without `--skip-setup` first
   - Check paths in `config.py`

2. **Plot generation fails**
   - Check available memory
   - Verify data processing completed successfully
   - Check logs for detailed error messages

## License

This project is licensed under the MIT License - see the LICENSE file for details. 