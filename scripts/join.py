import pandas as pd
import glob
import os

# === CONFIGURATION ===
# Folder containing your monthly Excel exports
folder_path = r"D:\Downloads\FireFox\py_scripts\fibre cut- - Copy"
# Output file
output_file = os.path.join(folder_path, "merged_events.xlsx")

# === STEP 1: Find all Excel files ===
files = glob.glob(os.path.join(folder_path, "*.xlsx"))

if not files:
    raise FileNotFoundError("No Excel files found in the folder. Check path or extension.")

print(f"Found {len(files)} files.")

# === STEP 2: Load all files into DataFrames ===
dfs = []
all_cols = set()

for f in files:
    try:
        df = pd.read_excel(f)
        # Normalize column names (strip spaces, lowercase)
        df.columns = df.columns.str.strip().str.lower()
        dfs.append(df)
        all_cols.update(df.columns)
        print(f"Loaded {f} with {len(df)} rows and {len(df.columns)} columns.")
    except Exception as e:
        print(f"Error reading {f}: {e}")

if not dfs:
    raise ValueError("No valid dataframes loaded. Check file formats.")

# === STEP 3: Build master schema ===
all_cols = list(all_cols)
print(f"Master schema has {len(all_cols)} columns.")

# === STEP 4: Reindex each DataFrame to master schema ===
normalized_dfs = []
for df in dfs:
    normalized = df.reindex(columns=all_cols, fill_value=0)
    normalized_dfs.append(normalized)

# === STEP 5: Concatenate all normalized DataFrames ===
merged = pd.concat(normalized_dfs, ignore_index=True)

print(f"Merged dataset has {len(merged)} rows and {len(merged.columns)} columns.")

# === STEP 6: Save output ===
merged.to_excel(output_file, index=False)
print(f"Saved merged file to: {output_file}")