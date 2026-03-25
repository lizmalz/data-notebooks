import pandas as pd

# Load your csv files
df1 = pd.read_csv("file1.csv")
df2 = pd.read_csv("file2.csv")

# Perform the join (VLOOKUP equivalent)
merged = df1.merge(df2, on="wardcode", how="left")

# Save the output
merged.to_csv("output.csv", index=False)