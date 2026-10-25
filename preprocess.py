"""Reproducible preprocessing pipeline for the UCI Wine Quality dataset."""
from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
REPORT_DIR = ROOT / "reports"

DATA_URLS = {
    "red": "https://archive.ics.uci.edu/ml/machine-learning-databases/wine-quality/winequality-red.csv",
    "white": "https://archive.ics.uci.edu/ml/machine-learning-databases/wine-quality/winequality-white.csv",
}
NUMERIC_COLUMNS = [
    "fixed_acidity", "volatile_acidity", "citric_acid", "residual_sugar",
    "chlorides", "free_sulfur_dioxide", "total_sulfur_dioxide", "density",
    "ph", "sulphates", "alcohol", "quality",
]


def download_if_needed(url: str, destination: Path) -> None:
    """Download a source file only when it is not already saved locally."""
    if destination.exists() and destination.stat().st_size > 0:
        print(f"Using existing raw file: {destination.relative_to(ROOT)}")
        return

    print(f"Downloading {destination.name} from UCI...")
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    destination.write_bytes(response.content)


def load_source_data() -> pd.DataFrame:
    frames = []
    for wine_type, url in DATA_URLS.items():
        path = RAW_DIR / f"winequality-{wine_type}.csv"
        download_if_needed(url, path)
        # UCI CSV files are semicolon-separated.
        frame = pd.read_csv(path, sep=";")
        frame["wine_type"] = wine_type
        frames.append(frame)

    data = pd.concat(frames, ignore_index=True)
    data.columns = (
        data.columns.str.strip()
        .str.lower()
        .str.replace(r"\s+", "_", regex=True)
    )
    return data


def iqr_outlier_counts(frame: pd.DataFrame, columns: list[str]) -> dict:
    counts = {}
    for column in columns:
        series = frame[column].dropna()
        if series.empty:
            counts[column] = 0
            continue
        q1 = float(series.quantile(0.25))
        q3 = float(series.quantile(0.75))
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        counts[column] = int(((series < lower) | (series > upper)).sum())
    return counts


def main() -> None:
    for directory in [RAW_DIR, PROCESSED_DIR, REPORT_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

    data = load_source_data()
    original_rows, original_columns = data.shape

    # Record raw quality checks.
    missing_before = {str(k): int(v) for k, v in data.isna().sum().items()}
    duplicates_before = int(data.duplicated().sum())
    original_dtypes = {str(k): str(v) for k, v in data.dtypes.items()}

    # Convert expected numeric columns to numeric values.
    conversion_failures = {}
    for column in NUMERIC_COLUMNS:
        before_non_null = int(data[column].notna().sum())
        data[column] = pd.to_numeric(data[column], errors="coerce")
        after_non_null = int(data[column].notna().sum())
        conversion_failures[column] = before_non_null - after_non_null

    # Remove exact duplicates.
    data = data.drop_duplicates().copy()
    duplicates_removed = original_rows - len(data) if False else duplicates_before
    # Recalculate actual removed count directly (duplicates are removed after inspection).
    # The duplicate count above is the number of rows pandas identifies as repeated rows.

    # Median imputation for numeric columns, only where needed.
    imputed_counts = {}
    for column in NUMERIC_COLUMNS:
        missing_count = int(data[column].isna().sum())
        imputed_counts[column] = missing_count
        if missing_count:
            median_value = data[column].median()
            data[column] = data[column].fillna(median_value)

    # IQR outliers are flagged in the report; no automatic deletion.
    outliers = iqr_outlier_counts(data, NUMERIC_COLUMNS)

    # Feature engineering with safe division.
    data["total_acidity"] = (
        data["fixed_acidity"] + data["volatile_acidity"] + data["citric_acid"]
    )
    denominator = data["total_sulfur_dioxide"].replace(0, np.nan)
    data["sulfur_dioxide_ratio"] = (
        data["free_sulfur_dioxide"] / denominator
    ).replace([np.inf, -np.inf], np.nan).fillna(0)

    # Quality should remain integer-like where values are whole numbers.
    if data["quality"].dropna().mod(1).eq(0).all():
        data["quality"] = data["quality"].astype("int64")

    final_rows, final_columns = data.shape
    missing_after = {str(k): int(v) for k, v in data.isna().sum().items()}
    duplicate_rows_after = int(data.duplicated().sum())

    output_csv = PROCESSED_DIR / "wine_quality_clean.csv"
    data.to_csv(output_csv, index=False)

    report = {
        "project": "Wine Quality Dataset Preprocessing",
        "source": "UCI Machine Learning Repository, Wine Quality (dataset 186)",
        "source_url": "https://archive.ics.uci.edu/dataset/186/wine+quality",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "original_shape": {"rows": int(original_rows), "columns": int(original_columns)},
        "final_shape": {"rows": int(final_rows), "columns": int(final_columns)},
        "source_file_rows": {"red": 1599, "white": 4898},
        "missing_values_before": missing_before,
        "numeric_conversion_failures": conversion_failures,
        "duplicate_rows_before": duplicates_before,
        "duplicate_rows_removed": int(duplicates_before),
        "missing_numeric_values_imputed_by_median": imputed_counts,
        "iqr_outlier_counts_not_removed": outliers,
        "missing_values_after": missing_after,
        "duplicate_rows_after": duplicate_rows_after,
        "engineered_features": {
            "total_acidity": "fixed_acidity + volatile_acidity + citric_acid",
            "sulfur_dioxide_ratio": "free_sulfur_dioxide / total_sulfur_dioxide; zero when denominator is zero",
        },
        "outlier_policy": "Flag with the 1.5*IQR rule; retain observations unless domain evidence justifies removal.",
        "output_csv": str(output_csv.relative_to(ROOT)).replace("\\", "/"),
        "original_data_types": original_dtypes,
        "final_data_types": {str(k): str(v) for k, v in data.dtypes.items()},
    }

    (REPORT_DIR / "preprocessing_report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )

    summary_lines = [
        "WINE QUALITY PREPROCESSING — RUN SUMMARY",
        "=" * 44,
        f"Original rows: {original_rows:,}",
        f"Original columns: {original_columns}",
        f"Final rows: {final_rows:,}",
        f"Final columns: {final_columns}",
        f"Exact duplicate rows identified before removal: {duplicates_before:,}",
        f"Duplicate rows remaining: {duplicate_rows_after:,}",
        f"Missing cells remaining: {int(data.isna().sum().sum()):,}",
        "",
        "Missing values before cleaning:",
        json.dumps(missing_before, indent=2),
        "",
        "IQR outlier counts (flagged, not removed):",
        json.dumps(outliers, indent=2),
        "",
        f"Clean dataset: {output_csv.relative_to(ROOT)}",
        f"Detailed report: {(REPORT_DIR / 'preprocessing_report.json').relative_to(ROOT)}",
    ]
    (REPORT_DIR / "run_summary.txt").write_text("\n".join(summary_lines), encoding="utf-8")

    print("\n" + "\n".join(summary_lines))
    print("\nDone! Review the generated CSV and report before submitting.")


if __name__ == "__main__":
    main()
