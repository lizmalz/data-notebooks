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

# Remove rows with missing coordinates
df = df.dropna(subset=["latitude", "longitude"])

# Normalize state names for folder grouping
df["state_norm"] = df["address"].str.extract(r",\s*([^,]+)\s+State", expand=False)
df["state_norm"] = df["state_norm"].fillna("Unknown").str.title()

# ---------------------------------------------------------
# ICON + COLOR MAPPING
# ---------------------------------------------------------
STYLE_MAP = {
    "opencage":  {"color": "ff00ff00", "icon": "http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png"},
    "lga_fallback": {"color": "ff00a5ff", "icon": "http://maps.google.com/mapfiles/kml/shapes/placemark_square.png"},
    "state_fallback": {"color": "ff0000ff", "icon": "http://maps.google.com/mapfiles/kml/shapes/triangle.png"},
    "failed": {"color": "ff000000", "icon": "http://maps.google.com/mapfiles/kml/shapes/cross-hairs.png"},
}

# ---------------------------------------------------------
# CREATE KML / KMZ
# ---------------------------------------------------------
kml = simplekml.Kml()
root_folder = kml.newfolder(name="Schools")

# Create folders for each state
state_folders = {}
for state in sorted(df["state_norm"].unique()):
    state_folders[state] = root_folder.newfolder(name=state)

# ---------------------------------------------------------
# ADD POINTS
# ---------------------------------------------------------
for _, row in df.iterrows():
    lat = row["latitude"]
    lon = row["longitude"]
    address = row["address"]
    source = row["geocode_source"]

    # Choose style
    style = STYLE_MAP.get(source, STYLE_MAP["failed"])

    # Add to correct state folder
    folder = state_folders[row["state_norm"]]

    pnt = folder.newpoint(
        name=address,
        coords=[(lon, lat)]
    )

    # Apply color + icon
    pnt.style.iconstyle.color = style["color"]
    pnt.style.iconstyle.scale = 1.1
    pnt.style.iconstyle.icon.href = style["icon"]

# ---------------------------------------------------------
# SAVE KMZ
# ---------------------------------------------------------
kml.savekmz(OUTPUT_KMZ)

print(f"KMZ file created: {OUTPUT_KMZ}")
print(f"Total points exported: {len(df)}")