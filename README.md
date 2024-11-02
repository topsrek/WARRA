# WARRA
**W**ahl **A**erzte **R**echnungs **R**efundierungs **A**nalyse Österreich
Late 2024

## Parlamentarische Anfragen
https://www.parlament.gv.at/gegenstand/XXVII/AB/18726



## Data
### Download
packages needed: requests

`python -m pipenv install requests` or
`pip install requests`
if pipenv: `python -m pipenv shell`

`cd raw_data`

`python download_parliament_files.py`

### Converting
packages needed: PyPDF2 pdfplumber tabula-py pandas

`python -m pipenv install PyPDF2 pdfplumber tabula-py pandas` or
`pip install PyPDF2 pdfplumber tabula-py pandas`
if pipenv: `python -m pipenv shell`

`cd raw_data`

`python extract_data_from_pdfs.py`

### Postprocessing


## Development
Use(d) the Cursor IDE with Composer to generate the download script and main structure of extraction and postprocessing.

Use pipenv to install new packages, like:
python -m pipenv install [PACKAGENAME]
python -m pipenv shell
