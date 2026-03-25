import csv
import simplekml

def csv_to_kmz(csv_file, kmz_file):
    kml = simplekml.Kml()

    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            name = row.get("name", "NoName")
            lat = float(row["latitude"])
            lon = float(row["longitude"])

            kml.newpoint(name=name, coords=[(lon, lat)])

    kml.savekmz(kmz_file)
    print(f"KMZ file created: {kmz_file}")

# Usage
csv_to_kmz("data.csv", "output.kmz")