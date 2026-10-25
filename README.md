# Wine Quality Dataset: Data Cleaning & Preprocessing

**Internship Task 2 — Real-world dataset preprocessing**

This project downloads the red and white Wine Quality datasets from the UCI Machine Learning Repository, combines them, checks data quality, cleans the data, engineers additional features, and creates documentation and outputs.

## Dataset source
- Official UCI page: https://archive.ics.uci.edu/dataset/186/wine+quality
- Dataset DOI: https://doi.org/10.24432/C56S3T
- Original researchers: P. Cortez, A. Cerdeira, F. Almeida, T. Matos, and J. Reis (2009).
- License: CC BY 4.0 (credit the source when reusing the data).

The two source files contain 1,599 red-wine rows and 4,898 white-wine rows (6,497 rows total before cleaning). The script downloads the files directly from UCI. The source files use semicolons as separators.

## Project structure

```text
wine-quality-preprocessing-project/
├── data/
│   ├── raw/                 # downloaded original CSV files
│   └── processed/           # generated cleaned CSV
├── reports/
│   ├── preprocessing_report.json
│   └── run_summary.txt
├── screenshots/             # add screenshots of your own run here
├── src/
│   └── preprocess.py        # complete reproducible pipeline
├── DATA_DICTIONARY.md
├── METHODOLOGY.md
├── requirements.txt
└── README.md
```

## Run it (Windows / VS Code)

1. Install Python 3.10+ and open this folder in VS Code.
2. Open **Terminal → New Terminal**.
3. Run these commands:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python src/preprocess.py
```

If PowerShell blocks activation, you can skip activation and run:
```powershell
python -m pip install -r requirements.txt
python src/preprocess.py
```

Internet access is needed for the first run to download the original UCI CSV files. The script saves them to `data/raw/` so later runs can use the local copies.

## What the pipeline does

1. Downloads and combines the red and white wine data, adding a `wine_type` column.
2. Standardizes column names and checks dimensions and data types.
3. Converts numeric columns to numeric types and reports conversion problems.
4. Counts missing values and handles any missing numeric values with the column median.
5. Removes exact duplicate rows and reports how many were removed.
6. Checks numeric values for IQR-based outliers. **Outliers are flagged for review, not automatically deleted or capped**, because extreme chemistry measurements can be genuine observations.
7. Engineers `total_acidity` (fixed acidity + volatile acidity + citric acid) and `sulfur_dioxide_ratio` (free sulfur dioxide / total sulfur dioxide, with safe handling when the denominator is zero).
8. Validates the cleaned dataset and writes a CSV, JSON report, and text summary.

## Deliverables

- **GitHub repository:** create a public repository and upload the project folder.
- **Clean dataset:** `data/processed/wine_quality_clean.csv` (created after running the script).
- **Python preprocessing script:** `src/preprocess.py`.
- **Data documentation:** `DATA_DICTIONARY.md` and `METHODOLOGY.md`.
- **Screenshots/output:** capture the terminal summary and a preview of the generated clean CSV, then save screenshots in `screenshots/`.

## Important honesty note

Do not claim that missing values or duplicates were found if the generated report says zero. The UCI source describes the original features as having no missing values. This pipeline still checks for missing values and handles them if present. The exact duplicate count, outlier counts, and final row count are generated from the actual files when you run it.

## Suggested screenshots

1. `01_terminal_run.png` — terminal showing successful execution and final row/column counts.
2. `02_clean_dataset_preview.png` — open `data/processed/wine_quality_clean.csv` in VS Code or a spreadsheet.
3. `03_report.png` — open `reports/preprocessing_report.json` and show its summary.
4. Optional: GitHub repository page showing the uploaded files.

## Attribution

Cortez, P., Cerdeira, A., Almeida, F., Matos, T., & Reis, J. (2009). *Wine Quality*. UCI Machine Learning Repository. https://doi.org/10.24432/C56S3T
