import pandas as pd
import glob

def merge_geocoded_files(output_csv="schools_all_coords.csv"):
    # Find all geocoded split files
    files = sorted(glob.glob("schools_part_*_coords.csv"))

    print(f"Found {len(files)} geocoded files to merge.")

    # Load and combine
    dfs = []
    for f in files:
        print(f"Loading {f}...")
        df = pd.read_csv(f, encoding="utf-8")
        dfs.append(df)

    # Concatenate all into one DataFrame
    merged = pd.concat(dfs, ignore_index=True)

    # Save final merged file
    merged.to_csv(output_csv, index=False, encoding="utf-8")
    print(f"\nMerged file saved as {output_csv}")
    print(f"Total rows: {len(merged)}")


# Run the merge
merge_geocoded_files()