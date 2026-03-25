import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

def get_school_coordinates(input_csv, output_csv):
    # Initialize geocoder
    geolocator = Nominatim(user_agent="nigeria_school_locator")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1, max_retries=3)

    # Load data
    df = pd.read_csv(input_csv)
    print(f"Processing {len(df)} schools...")

    # Cache to avoid repeated lookups
    cache = {}

    # Nigeria bounding box for validation
    def is_in_nigeria(lat, lon):
        return (-5 <= lat <= 14) and (2 <= lon <= 15)

    def safe_geocode(query):
        # Use cache if available
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

    # Geocode each row using the full school_name string
    df['location'] = df['school_name'].apply(safe_geocode)

    # Extract coordinates
    df['latitude'] = df['location'].apply(lambda loc: loc.latitude if loc else None)
    df['longitude'] = df['location'].apply(lambda loc: loc.longitude if loc else None)

    # Clean up
    df.drop(columns=['location'], inplace=True)
    df.to_csv(output_csv, index=False)

    print(f"Done. Coordinates saved to {output_csv}.")