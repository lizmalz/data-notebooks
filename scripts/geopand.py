import geopandas as gpd
import pandas as pd

# ---------------------------------------------------------
# INPUT FILES
# ---------------------------------------------------------
GPKG_FILE = "NGA_LGA_Boundaries.gpkg"
ATTRIBUTE_CSV = "NGA_LGA_Boundaries_2_.csv"
OUTPUT_CSV = "nigeria_lga_centroids.csv"

# ---------------------------------------------------------
# LOAD GEOMETRY FROM GPKG
# ---------------------------------------------------------
gdf = gpd.read_file(GPKG_FILE)

# Ensure geometry is in WGS84 (EPSG:4326)
if gdf.crs is None or gdf.crs.to_epsg() != 4326:
    gdf = gdf.to_crs(4326)

# ---------------------------------------------------------
# LOAD ATTRIBUTE TABLE
# ---------------------------------------------------------
attr = pd.read_csv(ATTRIBUTE_CSV)

# ---------------------------------------------------------
# NORMALIZE JOIN KEYS
# ---------------------------------------------------------
def norm(x):
    return str(x).strip().lower()

# Normalize GPKG fields
gdf["state_join"] = gdf["statename"].apply(norm)
gdf["lga_join"] = gdf["lganame"].apply(norm)

# Normalize CSV fields
attr["state_join"] = attr["statename"].apply(norm)
attr["lga_join"] = attr["lganame"].apply(norm)

# ---------------------------------------------------------
# MERGE GEOMETRY + ATTRIBUTES
# ---------------------------------------------------------
merged = gdf.merge(
    attr[["state_join", "lga_join", "statename", "lganame"]],
    on=["state_join", "lga_join"],
    how="inner"
)

print("Merged rows:", len(merged))
print("Merged columns:", merged.columns)

# ---------------------------------------------------------
# PROJECT TO METRIC CRS FOR ACCURATE CENTROIDS
# ---------------------------------------------------------
projected = merged.to_crs(26391)  # Minna / Nigeria West Belt

# Compute centroid in projected CRS
projected["centroid"] = projected.geometry.centroid

# Extract centroid coordinates BEFORE converting back
projected["centroid_lat"] = projected["centroid"].y
projected["centroid_lon"] = projected["centroid"].x

# Convert back to WGS84
centroids_wgs = projected.to_crs(4326)

# ---------------------------------------------------------
# FINAL OUTPUT TABLE
# ---------------------------------------------------------
final = pd.DataFrame({
    "state": merged["statename_y"],   # CSV version
    "lga": merged["lganame_y"],       # CSV version
    "lat": projected["centroid_lat"],
    "lon": projected["centroid_lon"]
})

# Sort by state → LGA
final = final.sort_values(["state", "lga"])

# Save
final.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")

print("Centroid file created:", OUTPUT_CSV)
print("Total LGAs:", len(final))