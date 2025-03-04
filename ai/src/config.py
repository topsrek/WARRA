from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
LOGS_DIR = BASE_DIR / "logs"

# Data paths
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
ANFRAGEN_DIR = RAW_DATA_DIR / "anfragen"
BEANTWORTUNGEN_DIR = RAW_DATA_DIR / "beantwortungen"

# Output paths
PLOTS_DIR = OUTPUT_DIR / "plots"
DASHBOARDS_DIR = OUTPUT_DIR / "dashboards"

# Ensure directories exist
for directory in [DATA_DIR, OUTPUT_DIR, LOGS_DIR, RAW_DATA_DIR, 
                 PROCESSED_DATA_DIR, PLOTS_DIR, DASHBOARDS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Plot settings
PLOT_SETTINGS = {
    'style': 'seaborn',
    'figsize': (12, 8),
    'dpi': 300,
    'date_format': '%Y-%m-%d',
}

# Color schemes
COLORS = {
    'primary': '#2C3E50',
    'secondary': '#E74C3C',
    'accent': '#3498DB',
    'background': '#ECF0F1',
    'text': '#2C3E50',
}

# Date ranges
DATE_RANGES = {
    'all': None,
    'last_year': 365,
    'last_month': 30,
    'last_week': 7,
}

# File patterns
FILE_PATTERNS = {
    'request': r'\d{4}-\d{2}-\d{2}_INR_\d+_beantwortet_mit_\d+',
    'response': r'\d{4}-\d{2}-\d{2}_INR_\d+_beantwortet_\d+J',
}

# Dashboard settings
DASHBOARD_SETTINGS = {
    'port': 8050,
    'debug': True,
    'host': 'localhost',
}

# Export settings
EXPORT_SETTINGS = {
    'csv': {
        'encoding': 'utf-8',
        'index': False,
    },
    'excel': {
        'engine': 'openpyxl',
        'index': False,
    },
    'plot': {
        'format': 'png',
        'bbox_inches': 'tight',
    }
}

# Logging settings
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.FileHandler',
            'filename': LOGS_DIR / 'app.log',
            'mode': 'a',
        },
        'console': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True
        }
    }
} 