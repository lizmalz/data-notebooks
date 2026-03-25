import pandas as pd
import simplekml

# Load Excel file
df = pd.read_excel("locations.xlsx")

# Create KML object
kml = simplekml.Kml()

# Optional: define a custom icon style
style = simplekml.Style()
style.iconstyle.color = simplekml.Color.blue
style.iconstyle.scale = 1.1
style.iconstyle.icon.href = "http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png"

# Loop through rows and add placemarks
for _, row in df.iterrows():
    name = row.get("Name", "Unnamed")
    lat = row["Latitude"]
    lon = row["Longitude"]
    desc = row.get("Description", "")
    
    pnt = kml.newpoint(name=name, coords=[(lon, lat)])
    pnt.description = desc
    pnt.style = style

# Save KML and KMZ
kml.save("output.kml")
kml.savekmz("output.kmz")