# Metadata Format

## English

Metadata files contain information about the dataset structure, columns, and data types.

### Loading in Python

```python
import json
with open('filename_metadata.json', 'r', encoding='utf-8') as f:
    metadata = json.load(f)
```

### Loading in R

```r
library(jsonlite)
metadata <- fromJSON('filename_metadata.json')
```

### Required Libraries

Python: json (built-in)

R: jsonlite

## Deutsch

Metadatendateien enthalten Informationen über die Datensatzstruktur, Spalten und Datentypen.

### Laden in Python

```python
import json
with open('filename_metadata.json', 'r', encoding='utf-8') as f:
    metadata = json.load(f)
```

### Laden in R

```r
library(jsonlite)
metadata <- fromJSON('filename_metadata.json')
```

### Erforderliche Bibliotheken

Python: json (built-in)

R: jsonlite

