import pandas as pd
import googlemaps
import simplekml
import logging
import re

# =========================================================
# CONFIGURATION
# =========================================================
INPUT_CSV = "schools.csv"                 # Your master input file
OUTPUT_CSV = "schools_all_coords.csv"     # Final geocoded output
SUMMARY_CSV = "geocode_summary.csv"       # QA summary
FAILED_CSV = "geocode_failed.csv"         # Failed rows
FALLBACK_CSV = "geocode_fallbacks.csv"    # Fallback rows
OUTPUT_KMZ = "schools_all_coords.kmz"     # KMZ output

GOOGLE_API_KEY = "YOUR_NEW_GOOGLE_API_KEY_HERE"

# =========================================================
# LOGGING
# =========================================================
logging.basicConfig(
    filename="geocode_debug.log",
    filemode="a",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# =========================================================
# LOAD LGA CENTROIDS
# =========================================================
def load_lga_centroids(csv_path="nigeria_lga_centroids.csv"):
    df = pd.read_csv(csv_path)
    centroids = {}
    for _, row in df.iterrows():
        key = (row["state"].strip().lower(), row["lga"].strip().lower())
        centroids[key] = (row["lat"], row["lon"])
    return centroids

LGA_CENTROIDS = load_lga_centroids()

# =========================================================
# STATE CENTROIDS
# =========================================================
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

# =========================================================
# GOOGLE GEOCODER
# =========================================================
gmaps = googlemaps.Client(key=GOOGLE_API_KEY)
cache = {}

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

# =========================================================
# STATE + LGA EXTRACTION
# =========================================================
def extract_state_and_lga(address):
    addr = address.lower()
    for (state, lga) in LGA_CENTROIDS.keys():
        if state in addr and lga in addr:
            return state, lga
    for state in STATE_CENTROIDS.keys():
        if state in addr:
            return state, None
    return None, None

# =========================================================
# MAIN GEOCODING PIPELINE
# =========================================================
def run_geocoding():
    df = pd.read_csv(INPUT_CSV, encoding="latin1")
    print(f"Loaded {len(df)} schools.")

    for address in df["address"]:
        if address in cache:
            continue

        # 1. Google
        lat, lon, src, conf = geocode_google(address)
        if lat is not None:
            cache[address] = (lat, lon, src, conf)
            continue

        # 2. LGA fallback
        state, lga = extract_state_and_lga(address)
        if state and lga:
            lat, lon = LGA_CENTROIDS[(state, lga)]
            cache[address] = (lat, lon, "lga_fallback", 0.7)
            continue

        # 3. State fallback
        if state:
            lat, lon = STATE_CENTROIDS[state]
            cache[address] = (lat, lon, "state_fallback", 0.4)
            continue

        # 4. Failed
        cache[address] = (None, None, "failed", 0.0)

    df["latitude"] = [cache[a][0] for a in df["address"]]
    df["longitude"] = [cache[a][1] for a in df["address"]]
    df["geocode_source"] = [cache[a][2] for a in df["address"]]
    df["confidence"] = [cache[a][3] for a in df["address"]]

    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    print(f"Saved geocoded file → {OUTPUT_CSV}")

# =========================================================
# QA SUMMARY
# =========================================================
def run_qa_summary():
    df = pd.read_csv(OUTPUT_CSV)

    total = len(df)
    source_counts = df["geocode_source"].value_counts()
    source_percent = (source_counts / total * 100).round(2)

    summary = pd.DataFrame({
        "count": source_counts,
        "percent": source_percent
    })

    summary.to_csv(SUMMARY_CSV)
    df[df["geocode_source"] == "failed"].to_csv(FAILED_CSV, index=False)
    df[df["geocode_source"].isin(["lga_fallback", "state_fallback"])].to_csv(FALLBACK_CSV, index=False)

    print("\n=== QA SUMMARY ===")
    print(summary)

# =========================================================
# KMZ GENERATION
# =========================================================
def run_kmz_export():
    df = pd.read_csv(OUTPUT_CSV)
    df = df.dropna(subset=["latitude", "longitude"])

    df["state_norm"] = df["address"].str.extract(r",\s*([^,]+)\s+State", expand=False)
    df["state_norm"] = df["state_norm"].fillna("Unknown").str.title()

    STYLE_MAP = {
        "google": {"color": "ff00ff00", "icon": "http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png"},
        "lga_fallback": {"color": "ff00a5ff", "icon": "http://maps.google.com/mapfiles/kml/shapes/placemark_square.png"},
        "state_fallback": {"color": "ff0000ff", "icon": "http://maps.google.com/mapfiles/kml/shapes/triangle.png"},
        "failed": {"color": "ff000000", "icon": "http://maps.google.com/mapfiles/kml/shapes/cross-hairs.png"},
    }

    kml = simplekml.Kml()
    root = kml.newfolder(name="Schools")

    state_folders = {state: root.newfolder(name=state) for state in sorted(df["state_norm"].unique())}

    for _, row in df.iterrows():
        lat, lon = row["latitude"], row["longitude"]
        address = row["address"]
        src = row["geocode_source"]

        style = STYLE_MAP.get(src, STYLE_MAP["failed"])
        folder = state_folders[row["state_norm"]]

        pnt = folder.newpoint(name=address, coords=[(lon, lat)])
        pnt.style.iconstyle.color = style["color"]
        pnt.style.iconstyle.scale = 1.1
        pnt.style.iconstyle.icon.href = style["icon"]

    kml.savekmz(OUTPUT_KMZ)
    print(f"KMZ exported → {OUTPUT_KMZ}")

# =========================================================
# RUN EVERYTHING
# =========================================================
run_geocoding()
run_qa_summary()
run_kmz_export()

print("\nPipeline complete.")