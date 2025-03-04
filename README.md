# WARRA
**W**ahl **A**erzte **R**echnungs **R**efundierungs **A**nalyse Österreich
Late 2024

## Sources
### Parlamentarische Anfragen
https://www.parlament.gv.at/gegenstand/XXVII/AB/18726

### Price Adjustment
https://www.statistik.at/statistiken/volkswirtschaft-und-oeffentliche-finanzen/preise-und-preisindizes/verbraucherpreisindex-vpi/hvpi#:~:text=Verbraucherpreisindizes%20%2D%20%C3%9Cbersichtstabelle

## Data Export Information / Datenexport-Informationen

### English

This project includes a comprehensive data export system that saves datasets in multiple formats for different use cases. All exported data is organized in format-specific subdirectories within the `data` directory:

- **CSV** (`data/csv/`): Universal format readable by any tool
- **Excel** (`data/excel/`): For German-speaking non-technical users
- **Parquet** (`data/parquet/`): Efficient columnar format for large datasets
- **Feather** (`data/feather/`): Fast format for sharing between Python and R
- **RDS** (`data/rds/`): Native R format for R users
- **Metadata** (`data/metadata/`): Documentation about the datasets

For thesis work, we recommend using the Parquet format in the `data/thesis` directory, which offers the best balance of performance and features.

To export your data to all formats, use the `export_all_formats()` function from the `data/export_utils.py` module:

```python
from data.export_utils import export_all_formats
export_all_formats(your_dataframe, "dataset_name")
```

See `data/export_example.ipynb` for a complete demonstration of the export functionality.

### Deutsch

Dieses Projekt enthält ein umfassendes Datenexportsystem, das Datensätze in mehreren Formaten für verschiedene Anwendungsfälle speichert. Alle exportierten Daten sind in formatspezifischen Unterverzeichnissen innerhalb des `data`-Verzeichnisses organisiert:

- **CSV** (`data/csv/`): Universelles Format, das von jedem Tool gelesen werden kann
- **Excel** (`data/excel/`): Für deutschsprachige nicht-technische Benutzer
- **Parquet** (`data/parquet/`): Effizientes spaltenorientiertes Format für große Datensätze
- **Feather** (`data/feather/`): Schnelles Format für den Austausch zwischen Python und R
- **RDS** (`data/rds/`): Natives R-Format für R-Benutzer
- **HDF5** (`data/hdf5/`): Für komplexe hierarchische Daten
- **Thesis** (`data/thesis/`): Optimiertes Format speziell für die Analyse in der Abschlussarbeit
- **Metadata** (`data/metadata/`): Dokumentation über die Datensätze

Für die Arbeit an der Abschlussarbeit empfehlen wir die Verwendung des Parquet-Formats im Verzeichnis `data/thesis`, das die beste Balance zwischen Leistung und Funktionen bietet.

Um Ihre Daten in alle Formate zu exportieren, verwenden Sie die Funktion `export_all_formats()` aus dem Modul `data/export_utils.py`:

```python
from data.export_utils import export_all_formats
export_all_formats(your_dataframe, "dataset_name")
```

Siehe `data/export_example.ipynb` für eine vollständige Demonstration der Exportfunktionalität.

## Data
### Download
packages needed: requests

`pip install requests`
or use pipenv: `python -m pipenv install requests` and `python -m pipenv shell`

`cd raw_data`

`python download_parliament_files.py`

### Extracting/Converting
packages needed: PyPDF2 pdfplumber tabula-py pandas

`pip install PyPDF2 pdfplumber tabula-py pandas`
or use pipenv:  `python -m pipenv install PyPDF2 pdfplumber tabula-py pandas` and `python -m pipenv shell`

`cd raw_data`

`python extract_data_from_pdfs.py`
`python extract_text_from_pdfs.py` (generate searchable text files)

Note: Beilage 13-16 were extracted manually (Copy/Paste, Excel, and OCR)

### Postprocessing


## Development
Use(d) the Cursor IDE with Composer to generate the download script and main structure of extraction and postprocessing.

Use pipenv to install new packages, like:
python -m pipenv install [PACKAGENAME]
python -m pipenv shell
