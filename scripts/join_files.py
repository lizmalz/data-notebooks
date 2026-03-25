import pandas as pd

# Load your Excel files
df1 = pd.read_excel("file1.xlsx")
df2 = pd.read_excel("file2.xlsx")

# Perform the join (VLOOKUP equivalent)
merged = df1.merge(df2, on="wrd_uniq_id", how="left")

# Save the output
merged.to_excel("output.xlsx", index=False)