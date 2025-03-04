"""
Utility functions for exporting data in various formats.
Designed for thesis data that will be shared as open source.
"""

import os
import pandas as pd
import json
import shutil

def ensure_directory(directory):
    """Create directory if it doesn't exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")

def export_to_csv(df, filename, export_dir="data/csv", index=True):
    """
    Export DataFrame to CSV format.
    
    Args:
        df: pandas DataFrame to export
        filename: name of the file (without extension)
        export_dir: directory to save the file
        index: whether to include index in the export
    
    Returns:
        Path to the exported file
    """
    ensure_directory(export_dir)
    filepath = os.path.join(export_dir, f"{filename}.csv")
    df.to_csv(filepath, index=index)
    print(f"Data exported to CSV: {filepath}")
    return filepath

def export_to_excel(df, filename, export_dir="data/excel", index=True):
    """
    Export DataFrame to Excel format for non-technical users.
    
    Args:
        df: pandas DataFrame to export
        filename: name of the file (without extension)
        export_dir: directory to save the file
        index: whether to include index in the export
    
    Returns:
        Path to the exported file
    """
    try:
        import openpyxl
    except ImportError:
        print("Warning: openpyxl not installed. Installing required packages for Excel export...")
        import subprocess
        subprocess.check_call(["pip", "install", "openpyxl"])
    
    ensure_directory(export_dir)
    filepath = os.path.join(export_dir, f"{filename}.xlsx")
    df.to_excel(filepath, index=index)
    print(f"Data exported to Excel: {filepath}")
    return filepath

def export_to_parquet(df, filename, export_dir="data/parquet", compression="snappy"):
    """
    Export DataFrame to Parquet format - excellent for large datasets.
    
    Args:
        df: pandas DataFrame to export
        filename: name of the file (without extension)
        export_dir: directory to save the file
        compression: compression algorithm ('snappy', 'gzip', 'brotli', None)
    
    Returns:
        Path to the exported file
    """
    try:
        import pyarrow
    except ImportError:
        print("Warning: pyarrow not installed. Installing required packages for Parquet...")
        import subprocess
        subprocess.check_call(["pip", "install", "pyarrow"])
    
    ensure_directory(export_dir)
    filepath = os.path.join(export_dir, f"{filename}.parquet")
    df.to_parquet(filepath, compression=compression)
    print(f"Data exported to Parquet: {filepath}")
    return filepath

def export_to_hdf5(df, filename, export_dir="data/hdf5", key="data"):
    """
    Export DataFrame to HDF5 format - good for very large datasets.
    
    Args:
        df: pandas DataFrame to export
        filename: name of the file (without extension)
        export_dir: directory to save the file
        key: identifier for the dataset within the HDF5 file
    
    Returns:
        Path to the exported file
    """
    try:
        import tables
    except ImportError:
        print("Warning: tables (PyTables) not installed. Installing required packages for HDF5...")
        import subprocess
        subprocess.check_call(["pip", "install", "tables"])
    
    ensure_directory(export_dir)
    filepath = os.path.join(export_dir, f"{filename}.h5")
    df.to_hdf(filepath, key=key, mode='w')
    print(f"Data exported to HDF5: {filepath}")
    return filepath

def export_to_feather(df, filename, export_dir="data/feather"):
    """
    Export DataFrame to Feather format - fast read/write, preserves pandas datatypes.
    Good for sharing between Python and R.
    
    Args:
        df: pandas DataFrame to export
        filename: name of the file (without extension)
        export_dir: directory to save the file
    
    Returns:
        Path to the exported file
    """
    try:
        import pyarrow
    except ImportError:
        print("Warning: pyarrow not installed. Installing required packages for Feather...")
        import subprocess
        subprocess.check_call(["pip", "install", "pyarrow"])
    
    ensure_directory(export_dir)
    filepath = os.path.join(export_dir, f"{filename}.feather")
    df.to_feather(filepath)
    print(f"Data exported to Feather: {filepath}")
    return filepath

def export_to_rds(df, filename, export_dir="data/rds"):
    """
    Export DataFrame to RDS format - native R format.
    Requires the pyreadr package.
    
    Args:
        df: pandas DataFrame to export
        filename: name of the file (without extension)
        export_dir: directory to save the file
    
    Returns:
        Path to the exported file
    """
    try:
        import pyreadr
    except ImportError:
        print("Warning: pyreadr not installed. Installing required packages for RDS export...")
        import subprocess
        subprocess.check_call(["pip", "install", "pyreadr"])
    
    import pyreadr
    
    ensure_directory(export_dir)
    filepath = os.path.join(export_dir, f"{filename}.rds")
    pyreadr.write_rds(filepath, df)
    print(f"Data exported to RDS: {filepath}")
    return filepath

def export_metadata(df, filename, export_dir="data/metadata", lang="en"):
    """
    Export metadata about the DataFrame to help with documentation.
    
    Args:
        df: pandas DataFrame to document
        filename: name of the file (without extension)
        export_dir: directory to save the file
        lang: language for metadata descriptions ('en' or 'de')
    
    Returns:
        Path to the exported file
    """
    ensure_directory(export_dir)
    filepath = os.path.join(export_dir, f"{filename}_metadata.json")
    
    # Create metadata
    metadata = {
        "columns": list(df.columns),
        "shape": df.shape,
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "index_names": df.index.names if hasattr(df.index, 'names') else None,
        "has_null_values": df.isnull().any().any(),
        "column_descriptions": {col: "" for col in df.columns}  # To be filled manually
    }
    
    # Add language-specific metadata
    if lang == "de":
        metadata["language"] = "Deutsch"
        metadata["description"] = "Metadaten für den Datensatz"
    else:
        metadata["language"] = "English"
        metadata["description"] = "Metadata for the dataset"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"Metadata exported to: {filepath}")
    return filepath

def export_thesis_format(df, filename, export_dir="data/thesis"):
    """
    Export DataFrame in the recommended format for thesis use.
    This uses Parquet format which offers the best balance of performance and features.
    
    Args:
        df: pandas DataFrame to export
        filename: name of the file (without extension)
        export_dir: directory to save the file
    
    Returns:
        Path to the exported file
    """
    ensure_directory(export_dir)
    
    # For thesis, we use parquet with brotli compression for maximum compression
    filepath = os.path.join(export_dir, f"{filename}.parquet")
    
    try:
        import pyarrow
    except ImportError:
        print("Warning: pyarrow not installed. Installing required packages...")
        import subprocess
        subprocess.check_call(["pip", "install", "pyarrow"])
    
    df.to_parquet(filepath, compression="brotli", index=True)
    
    # Also create a metadata file specifically for the thesis data
    metadata_path = os.path.join(export_dir, f"{filename}_metadata.json")
    
    metadata = {
        "columns": list(df.columns),
        "shape": df.shape,
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "index_names": df.index.names if hasattr(df.index, 'names') else None,
        "has_null_values": df.isnull().any().any(),
        "column_descriptions": {col: "" for col in df.columns},
        "thesis_specific_notes": "This dataset is formatted specifically for thesis analysis."
    }
    
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"Data exported in thesis format: {filepath}")
    print(f"Thesis metadata exported to: {metadata_path}")
    
    return filepath

def export_all_formats(df, filename_base):
    """
    Export DataFrame to all supported formats in their respective directories.
    
    Args:
        df: pandas DataFrame to export
        filename_base: base name for the files (without extension)
    
    Returns:
        Dictionary with paths to all exported files
    """
    paths = {}
    paths['csv'] = export_to_csv(df, filename_base)
    paths['excel'] = export_to_excel(df, filename_base)
    paths['parquet'] = export_to_parquet(df, filename_base)
    paths['hdf5'] = export_to_hdf5(df, filename_base)
    paths['feather'] = export_to_feather(df, filename_base)
    paths['rds'] = export_to_rds(df, filename_base)
    paths['metadata_en'] = export_metadata(df, filename_base, lang="en")
    paths['metadata_de'] = export_metadata(df, f"{filename_base}_de", lang="de")
    paths['thesis'] = export_thesis_format(df, filename_base)
    
    return paths

def create_format_readme(format_dir, format_name, description_en, description_de, 
                         load_python, load_r=None, required_libs=None):
    """
    Create a README file for each format directory.
    
    Args:
        format_dir: Directory to create the README in
        format_name: Name of the format
        description_en: English description
        description_de: German description
        load_python: How to load in Python
        load_r: How to load in R (if applicable)
        required_libs: Required libraries (if any)
    """
    ensure_directory(format_dir)
    
    with open(os.path.join(format_dir, "README.md"), "w", encoding="utf-8") as f:
        f.write(f"# {format_name} Format\n\n")
        
        f.write("## English\n\n")
        f.write(f"{description_en}\n\n")
        f.write("### Loading in Python\n\n")
        f.write(f"```python\n{load_python}\n```\n\n")
        
        if load_r:
            f.write("### Loading in R\n\n")
            f.write(f"```r\n{load_r}\n```\n\n")
        
        if required_libs:
            f.write("### Required Libraries\n\n")
            f.write(f"Python: {required_libs['python']}\n\n")
            if 'r' in required_libs:
                f.write(f"R: {required_libs['r']}\n\n")
        
        f.write("## Deutsch\n\n")
        f.write(f"{description_de}\n\n")
        f.write("### Laden in Python\n\n")
        f.write(f"```python\n{load_python}\n```\n\n")
        
        if load_r:
            f.write("### Laden in R\n\n")
            f.write(f"```r\n{load_r}\n```\n\n")
        
        if required_libs:
            f.write("### Erforderliche Bibliotheken\n\n")
            f.write(f"Python: {required_libs['python']}\n\n")
            if 'r' in required_libs:
                f.write(f"R: {required_libs['r']}\n\n")

def create_format_directories():
    """
    Create all format directories with README files.
    """
    # CSV
    create_format_readme(
        "data/csv",
        "CSV",
        "CSV (Comma-Separated Values) is a universal format that can be opened with Excel, text editors, or any data analysis tool.",
        "CSV (Komma-getrennte Werte) ist ein universelles Format, das mit Excel, Texteditoren oder jedem Datenanalysetool geöffnet werden kann.",
        "import pandas as pd\ndf = pd.read_csv('filename.csv')",
        "df <- read.csv('filename.csv')",
        {"python": "pandas", "r": "base R"}
    )
    
    # Excel
    create_format_readme(
        "data/excel",
        "Excel",
        "Excel (.xlsx) files can be directly opened in Microsoft Excel or other spreadsheet applications.",
        "Excel (.xlsx) Dateien können direkt in Microsoft Excel oder anderen Tabellenkalkulationsanwendungen geöffnet werden.",
        "import pandas as pd\ndf = pd.read_excel('filename.xlsx')",
        "library(readxl)\ndf <- read_excel('filename.xlsx')",
        {"python": "pandas, openpyxl", "r": "readxl"}
    )
    
    # Parquet
    create_format_readme(
        "data/parquet",
        "Parquet",
        "Parquet is a columnar storage format that offers excellent compression and performance for large datasets.",
        "Parquet ist ein spaltenorientiertes Speicherformat, das hervorragende Komprimierung und Leistung für große Datensätze bietet.",
        "import pandas as pd\ndf = pd.read_parquet('filename.parquet')",
        "library(arrow)\ndf <- read_parquet('filename.parquet')",
        {"python": "pandas, pyarrow", "r": "arrow"}
    )
    
    # HDF5
    create_format_readme(
        "data/hdf5",
        "HDF5",
        "HDF5 is a hierarchical data format suitable for complex, large datasets.",
        "HDF5 ist ein hierarchisches Datenformat, das für komplexe, große Datensätze geeignet ist.",
        "import pandas as pd\ndf = pd.read_hdf('filename.h5', key='data')",
        "library(rhdf5)\ndf <- h5read('filename.h5', 'data')",
        {"python": "pandas, tables", "r": "rhdf5"}
    )
    
    # Feather
    create_format_readme(
        "data/feather",
        "Feather",
        "Feather is designed for fast read/write operations and works well for sharing data between Python and R.",
        "Feather ist für schnelle Lese-/Schreibvorgänge konzipiert und eignet sich gut für den Datenaustausch zwischen Python und R.",
        "import pandas as pd\ndf = pd.read_feather('filename.feather')",
        "library(arrow)\ndf <- read_feather('filename.feather')",
        {"python": "pandas, pyarrow", "r": "arrow"}
    )
    
    # RDS
    create_format_readme(
        "data/rds",
        "RDS",
        "RDS is a native R format for storing R objects. This is the most convenient format for R users.",
        "RDS ist ein natives R-Format zum Speichern von R-Objekten. Dies ist das bequemste Format für R-Benutzer.",
        "import pyreadr\nresult = pyreadr.read_r('filename.rds')\ndf = result[None]  # RDS files contain only one object",
        "df <- readRDS('filename.rds')",
        {"python": "pyreadr", "r": "base R"}
    )
    
    # Thesis
    create_format_readme(
        "data/thesis",
        "Thesis Format",
        "This format is specifically optimized for use in the thesis, using Parquet with brotli compression for maximum efficiency.",
        "Dieses Format ist speziell für die Verwendung in der Abschlussarbeit optimiert und verwendet Parquet mit Brotli-Komprimierung für maximale Effizienz.",
        "import pandas as pd\ndf = pd.read_parquet('filename.parquet')",
        "library(arrow)\ndf <- read_parquet('filename.parquet')",
        {"python": "pandas, pyarrow", "r": "arrow"}
    )
    
    # Metadata
    create_format_readme(
        "data/metadata",
        "Metadata",
        "Metadata files contain information about the dataset structure, columns, and data types.",
        "Metadatendateien enthalten Informationen über die Datensatzstruktur, Spalten und Datentypen.",
        "import json\nwith open('filename_metadata.json', 'r', encoding='utf-8') as f:\n    metadata = json.load(f)",
        "library(jsonlite)\nmetadata <- fromJSON('filename_metadata.json')",
        {"python": "json (built-in)", "r": "jsonlite"}
    ) 