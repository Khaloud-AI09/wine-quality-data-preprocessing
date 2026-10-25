# Preprocessing Methodology

## 1. Data collection
The pipeline downloads the official red and white CSV files from the UCI Machine Learning Repository. It records the original file names and combines them into one table. A `wine_type` label is added based on the file each row came from.

## 2. Data inspection
The script records the original row and column counts, data types, missing values, and duplicate rows before cleaning.

## 3. Column names and data types
Column names are stripped of surrounding whitespace and converted to lowercase snake_case. Expected measurement and quality columns are converted to numeric values using safe coercion. The script reports any values that could not be converted.

## 4. Missing values
Missing values are counted. If any are present in numeric columns, they are replaced with that column's median. This is robust to skewed distributions. The actual counts and imputation actions are written to the JSON report. The UCI page indicates that the original feature columns have no missing values, so imputation may not be needed for this dataset.

## 5. Duplicate rows
Exact duplicate rows are counted and removed. A duplicate is defined as a row whose values match another row across all columns, including `wine_type`.

## 6. Outlier review
The pipeline uses the interquartile range (IQR) rule for numeric columns:
- IQR = Q3 - Q1
- Lower review threshold = Q1 - 1.5 × IQR
- Upper review threshold = Q3 + 1.5 × IQR

Outliers are reported per column but are not automatically deleted. In a scientific dataset, extreme measurements can be legitimate and should not be removed without domain justification. The report documents the decision.

## 7. Feature engineering
- `total_acidity`: sum of fixed acidity, volatile acidity, and citric acid.
- `sulfur_dioxide_ratio`: free sulfur dioxide / total sulfur dioxide. When total sulfur dioxide is zero, the ratio is set to 0 to avoid division by zero.

These are simple derived measurements for exploratory analysis. They do not guarantee better predictive performance.

## 8. Validation and outputs
The script checks for remaining missing values and duplicate rows, writes the processed CSV, and generates:
- `reports/preprocessing_report.json` — machine-readable detailed report.
- `reports/run_summary.txt` — readable summary for submission.

## Reproducibility
Run `python src/preprocess.py`. The script is designed to be rerun; downloaded raw files are reused if already present.
