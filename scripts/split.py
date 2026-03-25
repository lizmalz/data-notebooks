import pandas as pd
import math

def split_csv_by_100(input_csv, output_prefix):
    df = pd.read_csv(input_csv)
    total_rows = len(df)

    rows_per_file = 100
    num_files = math.ceil(total_rows / rows_per_file)

    print(f"Total rows: {total_rows}")
    print(f"Creating {num_files} files of ~{rows_per_file} rows each...")

    for i in range(num_files):
        start = i * rows_per_file
        end = start + rows_per_file
        chunk = df.iloc[start:end]

        if chunk.empty:
            break

        output_file = f"{output_prefix}_{i+1}.csv"
        chunk.to_csv(output_file, index=False)

        print(f"Saved {output_file} ({len(chunk)} rows)")

    print("Done.")


# -----------------------------
# CALL THE FUNCTION HERE
# -----------------------------
split_csv_by_100("schools.csv", "schools_part")