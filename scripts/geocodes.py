import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import glob
import os

# ---------------------------------------------------------
# Shared cache across ALL files (prevents duplicate lookups)
# ---------------------------------------------------------
cache = {}

# ---------------------------------------------------------
# Geocoding function for a single CSV file
# ---------------------------------------------------------
def get_school_coordinates(input_csv, output_csv):
    global cache

    # Initialize geocoder
    geolocator = Nominatim(user_agent="nigeria_school_locator")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1, max_retries=3)

    # Load data (handle Windows CSV encodings)
    df = pd.read_csv(input_csv, encoding="latin1")
    print(f"Processing {len(df)} schools in {input_csv}...")

    # Nigeria bounding box for validation
    def is_in_nigeria(lat, lon):
        return (-5 <= lat <= 14) and (2 <= lon <= 15)

    # Safe geocode wrapper with caching
    def safe_geocode(query):
        if query in cache:
            return cache[query]

        try:
            loc = geocode(query)
            if loc and is_in_nigeria(loc.latitude, loc.longitude):
                cache[query] = loc
                return loc
            else:
                cache[query] = None
                return None
        except Exception:
            cache[query] = None
            return None

    # Geocode each school name
    df['location'] = df['school_name'].apply(safe_geocode)

    # Extract coordinates
    df['latitude'] = df['location'].apply(lambda loc: loc.latitude if loc else None)
    df['longitude'] = df['location'].apply(lambda loc: loc.longitude if loc else None)

    # Save output
    df.drop(columns=['location'], inplace=True)
    df.to_csv(output_csv, index=False, encoding="utf-8")

    print(f"Done → {output_csv}")


# ---------------------------------------------------------
# Batch runner: process ALL split files in this folder
# ---------------------------------------------------------
input_files = sorted(glob.glob("schools_part_*.csv"))

print(f"Found {len(input_files)} split files to process.")

for file in input_files:
    base = os.path.splitext(file)[0]          # e.g., schools_part_1
    output_file = base + "_coords.csv"        # e.g., schools_part_1_coords.csv

    print(f"\n=== Processing {file} ===")
    get_school_coordinates(file, output_file)

print("\nAll files processed successfully.")