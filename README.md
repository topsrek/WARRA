# WARRA
**W**ahl **A**erzte **R**echnungs **R**efundierungs **A**nalyse Österreich
Late 2024

## Parlamentarische Anfragen
https://www.parlament.gv.at/gegenstand/XXVII/AB/18726



## Data
### Download
    pip install requests
    python download_parliament_files.py
### Converting
    pip install PyPDF2 tabula-py pandas
    python extract_data_from_pdfs.py

## Development
Use(d) the Cursor IDE with Composer to generate most scripts
Use pipenv to install new packages, like:
python -m pipenv install [PACKAGENAME]
python -m pipenv shell
