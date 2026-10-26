
from pathlib import Path
import pandas as pd

# Locate the project's data folder
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "sheets"

print("Checking Olist dataset files...\n")

# Find all CSV files
csv_files = list(DATA_DIR.glob("*.csv"))

if not csv_files:
    print("No CSV files found!")
    print("Please check that the Olist CSV files are inside the data folder.")
else:
    print(f"Found {len(csv_files)} CSV files:\n")

    for file in sorted(csv_files):
        print(f"File: {file.name}")

        try:
            df = pd.read_csv(file)

            print(f"Rows: {df.shape[0]:,}")
            print(f"Columns: {df.shape[1]}")
            print(f"Column names: {list(df.columns)}")
            print("-" * 70)

        except Exception as error:
            print(f"Could not read this file: {error}")
            print("-" * 70)
