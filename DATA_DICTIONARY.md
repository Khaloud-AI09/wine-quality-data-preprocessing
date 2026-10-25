# Data Dictionary

The source data describes red and white Vinho Verde wine samples from northern Portugal. Measurements are physicochemical tests; `quality` is a sensory score. The source does not provide wine brand, price, or grape variety.

| Column | Meaning | Type | Role |
|---|---|---|---|
| `fixed_acidity` | Fixed acids in the wine | Numeric | Source feature |
| `volatile_acidity` | Volatile acidity measurement | Numeric | Source feature |
| `citric_acid` | Citric acid measurement | Numeric | Source feature |
| `residual_sugar` | Residual sugar measurement | Numeric | Source feature |
| `chlorides` | Chloride measurement | Numeric | Source feature |
| `free_sulfur_dioxide` | Free sulfur dioxide measurement | Numeric | Source feature |
| `total_sulfur_dioxide` | Total sulfur dioxide measurement | Numeric | Source feature |
| `density` | Wine density | Numeric | Source feature |
| `pH` | pH measurement | Numeric | Source feature |
| `sulphates` | Sulphates measurement | Numeric | Source feature |
| `alcohol` | Alcohol measurement | Numeric | Source feature |
| `quality` | Sensory quality score (typically 0–10 scale) | Integer-like numeric | Target/outcome |
| `wine_type` | Whether the row came from the red or white source file | Categorical | Added from source-file identity |
| `total_acidity` | Sum of fixed, volatile, and citric acid measurements | Numeric | Engineered feature |
| `sulfur_dioxide_ratio` | Free sulfur dioxide divided by total sulfur dioxide; set to 0 if denominator is 0 | Numeric | Engineered feature |

The original files have 11 numeric columns. `wine_type` is added during combination. Engineered fields are extra features and are not part of the original UCI columns.
