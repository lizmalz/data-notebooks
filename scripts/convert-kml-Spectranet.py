import csv
import xml.etree.ElementTree as ET

def kml_to_csv(kml_file, csv_file):
    tree = ET.parse(kml_file)
    root = tree.getroot()

    ns = {'kml': 'http://www.opengis.net/kml/2.2'}

    rows = []

    for placemark in root.findall(".//kml:Placemark", ns):
        name = placemark.find("kml:name", ns)
        name = name.text if name is not None else ""

        coords = placemark.find(".//kml:Point/kml:coordinates", ns)
        if coords is not None:
            lon, lat, *_ = coords.text.strip().split(",")
            rows.append([name, lat, lon])

    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "latitude", "longitude"])
        writer.writerows(rows)

    print(f"CSV saved as: {csv_file}")


# Run it on your file
kml_to_csv("Spectranet.kml", "Spectranet.csv")