# Step 1: Environment & Dataset Loading

## Goal

Set up the Python environment and load the **Zomato dataset** from Kaggle as a pandas DataFrame. Verify columns and map them to our four preferences: **Location**, **Cuisine**, **Price**, **Ratings**.

## Prerequisites

1. **Python 3.9+** installed.
2. **Kaggle API credentials** (for local runs):
   - Go to [Kaggle Account](https://www.kaggle.com/settings) → Create New Token to download `kaggle.json`.
   - Place it in `%USERPROFILE%\.kaggle\kaggle.json` (Windows) or `~/.kaggle/kaggle.json` (Mac/Linux).
   - Or set env vars: `KAGGLE_USERNAME` and `KAGGLE_KEY`.

## Setup and Run

From the **project root** (`c-Users-Vishakha-Prasad-cursor`):

```powershell
# Install dependencies
pip install -r requirements.txt

# Or explicitly:
pip install "kagglehub[pandas-datasets]" pandas

# Run the data loader
python scripts/load_zomato_data.py
```

## Expected Output

- **First 5 records** of the DataFrame.
- **Columns** list.
- **Shape** (rows, columns).
- **Preference column mapping**: suggested dataset columns for Location, Cuisine, Price, Ratings.

## Configuring the CSV path

If the loader fails with "file not found", the dataset may use a different CSV filename. In `scripts/load_zomato_data.py` set:

- `FILE_PATH = "zomato.csv"`  
  or  
- `FILE_PATH = "Zomato data.csv"`  
  or  
- `FILE_PATH = ""`  

With `FILE_PATH = ""`, the script uses a fallback that downloads the dataset and loads the first CSV found.

## Deliverable (Step 1 complete)

- [x] `requirements.txt` with `kagglehub[pandas-datasets]` and `pandas`.
- [x] `scripts/load_zomato_data.py` loads `rajeshrampure/zomato-dataset` and prints head, columns, shape, and preference mapping.
- You have run the script once and confirmed the DataFrame loads and mapping looks correct for Step 2 (cleaning).
