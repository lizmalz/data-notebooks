import pandas as pd
import googlemaps
from tqdm import tqdm
import glob
import os
import logging

# ---------------------------------------------------------
# Logging setup
# ---------------------------------------------------------
logging.basicConfig(
    filename="geocode_debug.log",
    filemode="a",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ---------------------------------------------------------
# Load LGA centroid table
# ---------------------------------------------------------
def load_lga_centroids(csv_path="nigeria_lga_centroids.csv"):
    df = pd.read_csv(csv_path)
    centroids = {}
    for _, row in df.iterrows():
        key = (row["state"].strip().lower(), row["lga"].strip().lower())
        centroids[key] = (row["lat"], row["lon"])
    return centroids

LGA_CENTROIDS = load_lga_centroids()

# ---------------------------------------------------------
# State centroid fallback
# ---------------------------------------------------------
STATE_CENTROIDS = {
    "abia": (5.4527, 7.5248), "adamawa": (9.3265, 12.3984),
    "akwa ibom": (4.9057, 7.8537), "anambra": (6.2100, 7.0700),
    "bauchi": (10.3158, 9.8442), "bayelsa": (4.7719, 6.0699),
    "benue": (7.1907, 8.1291), "borno": (11.8846, 13.1510),
    "cross river": (5.8702, 8.5988), "delta": (5.5320, 5.8987),
    "ebonyi": (6.2649, 8.0137), "edo": (6.5438, 5.8987),
    "ekiti": (7.7180, 5.3103), "enugu": (6.4402, 7.4940),
    "gombe": (10.2897, 11.1673), "imo": (5.5720, 7.0588),
    "jigawa": (12.2280, 9.5616), "kaduna": (10.3764, 7.7090),
    "kano": (12.0022, 8.5919), "katsina": (12.9843, 7.6170),
    "kebbi": (11.6781, 4.0695), "kogi": (7.7337, 6.6906),
    "kwara": (8.9669, 4.3874), "lagos": (6.5244, 3.3792),
    "nasarawa": (8.5475, 7.7118), "niger": (9.0810, 6.0170),
    "ogun": (6.9970, 3.4737), "ondo": (7.2500, 5.2000),
    "osun": (7.5629, 4.5194), "oyo": (7.8400, 3.9500),
    "plateau": (9.2182, 9.5170), "rivers": (4.8436, 6.9112),
    "sokoto": (13.0667, 5.2333), "taraba": (7.9990, 10.9650),
    "yobe": (12.2939, 11.4390), "zamfara": (12.1704, 6.6640),
    "fct": (9.0765, 7.3986)
}

# ---------------------------------------------------------
# Shared cache
# ---------------------------------------------------------
cache = {}

# ---------------------------------------------------------
# Extract state + LGA from address
# ---------------------------------------------------------
def extract_state_and_lga(address):
    addr = address.lower()
    for (state, lga) in LGA_CENTROIDS.keys():
        if state in addr and lga in addr:
            return state, lga
    for state in STATE_CENTROIDS.keys():
        if state in addr:
            return state, None
    return None, None

# ---------------------------------------------------------
# Google geocoding function
# ---------------------------------------------------------
gmaps = googlemaps.Client(key="AIzaSyBdfPEFQ9u7cMeH7rd1FtwxD7nDBZDNqK0")

def geocode_google(address):
    try:
        result = gmaps.geocode(address, region="ng")
        if result:
            lat = result[0]["geometry"]["location"]["lat"]
            lon = result[0]["geometry"]["location"]["lng"]
            return lat, lon, "google", 1.0
    except Exception as e:
        logging.error(f"GOOGLE ERROR: {address} → {e}")
    return None, None, None, 0.0

# ---------------------------------------------------------
# Main geocoding function
# ---------------------------------------------------------
def get_school_coordinates(input_csv, output_csv):
    global cache

    df = pd.read_csv(input_csv, encoding="latin1")
    print(f"Processing {len(df)} schools in {input_csv}...")

    for address in tqdm(df["address"], desc=f"Geocoding {input_csv}"):

        if address in cache:
            continue

        # 1. Google primary geocoding
        lat, lon, src, conf = geocode_google(address)
        if lat is not None:
            cache[address] = (lat, lon, src, conf)
            continue

        # 2. LGA fallback
        state, lga = extract_state_and_lga(address)
        if state and lga:
            lat, lon = LGA_CENTROIDS[(state, lga)]
            cache[address] = (lat, lon, "lga_fallback", 0.7)
            logging.warning(f"LGA FALLBACK: {address} → {state}/{lga}")
            continue

        # 3. State fallback
        if state:
            lat, lon = STATE_CENTROIDS[state]
            cache[address] = (lat, lon, "state_fallback", 0.4)
            logging.warning(f"STATE FALLBACK: {address} → {state}")
            continue

        # 4. Final failure
        cache[address] = (None, None, "failed", 0.0)
        logging.error(f"FAILED: {address}")

    # Write results
    df["latitude"] = [cache[a][0] for a in df["address"]]
    df["longitude"] = [cache[a][1] for a in df["address"]]
    df["geocode_source"] = [cache[a][2] for a in df["address"]]
    df["confidence"] = [cache[a][3] for a in df["address"]]

    df.to_csv(output_csv, index=False, encoding="utf-8")
    print(f"Done → {output_csv}")

# ---------------------------------------------------------
# Batch runner
# ---------------------------------------------------------
input_files = sorted(glob.glob("schools_part_*.csv"))
print(f"Found {len(input_files)} split files to process.")

for file in input_files:
    base = os.path.splitext(file)[0]
    output_file = base + "_coords.csv"
    print(f"\n=== Processing {file} ===")
    get_school_coordinates(file, output_file)

# ---------------------------------------------------------
# Final merge
# ---------------------------------------------------------
def merge_geocoded_files(output_csv="schools_all_coords.csv"):
    files = sorted(glob.glob("schools_part_*_coords.csv"))
    dfs = [pd.read_csv(f, encoding="utf-8") for f in files]
    merged = pd.concat(dfs, ignore_index=True)
    merged.to_csv(output_csv, index=False, encoding="utf-8")
    print(f"\nFinal merged file saved as {output_csv}")

merge_geocoded_files()
print("\nAll tasks completed.")