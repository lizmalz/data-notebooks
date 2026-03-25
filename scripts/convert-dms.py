import pandas as pd
import re

# --- Function to convert DMS string to Decimal Degrees ---
def dms_to_dd(dms_str):
    # Pattern handles degrees, minutes, decimal seconds, and direction
    pattern = r'(\d+)[°\s]+(\d+)[\'\s]+([\d\.]+)[\"\s]*([NSEW])'
    match = re.search(pattern, dms_str.strip().upper())

    if not match:
        return None

    deg, minutes, seconds, direction = match.groups()
    deg = float(deg)
    minutes = float(minutes)
    seconds = float(seconds)

    dd = deg + minutes/60 + seconds/3600

    if direction in ['S', 'W']:
        dd = -dd

    return dd

# --- Load Excel file ---
df = pd.read_excel("file3.xlsx")

# --- Apply conversion ---
df["Longitude_DD"] = df["Longitude"].apply(dms_to_dd)
df["Latitude_DD"] = df["Lattitude"].apply(dms_to_dd)

# --- Save output ---
df.to_excel("file3_converted.xlsx", index=False)

print("Done. Saved as file3_converted.xlsx")