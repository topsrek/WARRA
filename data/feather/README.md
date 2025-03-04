# Feather Format

## English

Feather is designed for fast read/write operations and works well for sharing data between Python and R.

### Loading in Python

```python
import pandas as pd
df = pd.read_feather('filename.feather')
```

### Loading in R

```r
library(arrow)
df <- read_feather('filename.feather')
```

### Required Libraries

Python: pandas, pyarrow

R: arrow

## Deutsch

Feather ist für schnelle Lese-/Schreibvorgänge konzipiert und eignet sich gut für den Datenaustausch zwischen Python und R.

### Laden in Python

```python
import pandas as pd
df = pd.read_feather('filename.feather')
```

### Laden in R

```r
library(arrow)
df <- read_feather('filename.feather')
```

### Erforderliche Bibliotheken

Python: pandas, pyarrow

R: arrow

