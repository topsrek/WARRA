# RDS Format

## English

RDS is a native R format for storing R objects. This is the most convenient format for R users.

### Loading in Python

```python
import pyreadr
result = pyreadr.read_r('filename.rds')
df = result[None]  # RDS files contain only one object
```

### Loading in R

```r
df <- readRDS('filename.rds')
```

### Required Libraries

Python: pyreadr

R: base R

## Deutsch

RDS ist ein natives R-Format zum Speichern von R-Objekten. Dies ist das bequemste Format für R-Benutzer.

### Laden in Python

```python
import pyreadr
result = pyreadr.read_r('filename.rds')
df = result[None]  # RDS files contain only one object
```

### Laden in R

```r
df <- readRDS('filename.rds')
```

### Erforderliche Bibliotheken

Python: pyreadr

R: base R

