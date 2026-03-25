import pandas as pd
import os

def split_excel_by_column(input_file, column_name, output_folder):
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Load the Excel file
    df = pd.read_excel(input_file)

    # Group by the chosen column
    for value, group in df.groupby(column_name):
        # Clean the value for safe filenames
        safe_value = str(value).replace("/", "_").replace("\\", "_")

        output_path = os.path.join(output_folder, f"{safe_value}.xlsx")
        group.to_excel(output_path, index=False)

    print("Done splitting files.")


# Run it for your file
split_excel_by_column(
    input_file="health.xlsx",
    column_name="facility_level",
    output_folder="health_files"
)