import pandas as pd
import numpy as np
from sklearn.neighbors import BallTree

# Load files
file1 = pd.read_excel("file_1.xlsx")   # 300k rows
file2 = pd.read_excel("file_2.xlsx")   # 42k rows

# Convert degrees → radians
file1_rad = np.radians(file1[["latitude", "longitude"]])
file2_rad = np.radians(file2[["latitude", "longitude"]])

# Build BallTree using Haversine metric
tree = BallTree(file2_rad, metric="haversine")

# Query nearest neighbour for all points in file_1
distances, indices = tree.query(file1_rad, k=1)

# Convert radians → km
distances_km = distances[:, 0] * 6371

# Build output
output = pd.DataFrame({
    "file1_CODE": file1["CODE"],
    "nearest_file2_CODE": file2.loc[indices[:, 0], "CODE"].values,
    "distance_km": distances_km
})

output.to_csv("nearest_sites.csv", index=False)
print("Done.")