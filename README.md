# WARRA
**W**ahl **A**erzte **R**echnungs **R**efundierungs **A**nalyse Österreich
Late 2024

## Parlamentarische Anfragen
https://www.parlament.gv.at/gegenstand/XXVII/AB/18726



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
