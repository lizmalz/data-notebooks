import pandas as pd
import simplekml

# ---------------------------------------------------------
# INPUT / OUTPUT
# ---------------------------------------------------------
INPUT_CSV = "schools_all_coords.csv"
OUTPUT_KMZ = "schools_all_coords.kmz"

# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------
df = pd.read_csv(INPUT_CSV)

# Filter out rows with missing coordinates
df = df.dropna(subset=["latitude", "longitude"])

# ---------------------------------------------------------
# CREATE KML / KMZ
# ---------------------------------------------------------
kml = simplekml.Kml()

for _, row in df.iterrows():
    lat = row["latitude"]
    lon = row["longitude"]

    # Choose the label shown in Google Earth
    label = row.get("address", "Unknown Location")

    pnt = kml.newpoint(
        name=label,
        coords=[(lon, lat)]
    )

# Save as KMZ
kml.savekmz(OUTPUT_KMZ)

print(f"KMZ file created: {OUTPUT_KMZ}")
print(f"Total points exported: {len(df)}")