import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# -----------------------------
# 1. Load CSV
# -----------------------------
df = pd.read_csv("zdata.csv")

# Ensure distance column is numeric
df["distance_km"] = pd.to_numeric(df["distance_km"], errors="coerce")

# -----------------------------
# 2. Create Distance Bands (Updated)
# -----------------------------
bins = [0, 2, 5, 10, 15, 20, np.inf]
labels = [
    "0–2 km",
    "2–5 km",
    "5–10 km",
    "10–15 km",
    "15–20 km",
    "20+ km"
]

df["distance_band"] = pd.cut(df["distance_km"], bins=bins, labels=labels, right=True)

# -----------------------------
# 3. Summary Table
# -----------------------------
summary = (
    df["distance_band"]
    .value_counts()
    .sort_index()
    .rename_axis("Distance Band")
    .reset_index(name="Number of Settlements")
)

summary["Percent of Total"] = (summary["Number of Settlements"] / len(df) * 100).round(2)

# NEW: cumulative percentage column
summary["Cumulative Percent"] = summary["Percent of Total"].cumsum().round(2)

print("\n=== Coverage Distribution Summary ===")
print(summary)

# Save summary to CSV
summary.to_csv("coverage_distribution_summary.csv", index=False)

# -----------------------------
# 4. Histogram of Distances
# -----------------------------
plt.figure(figsize=(10, 6))
plt.hist(df["distance_km"], bins=40, color="steelblue", edgecolor="black")
plt.title("Histogram of Settlement Distances to Nearest Service Point / Site")
plt.xlabel("Distance (km)")
plt.ylabel("Number of Settlements")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("distance_histogram.png", dpi=300)
plt.close()

# -----------------------------
# 5. CDF Plot
# -----------------------------
sorted_distances = np.sort(df["distance_km"])
cdf = np.arange(1, len(sorted_distances) + 1) / len(sorted_distances)

plt.figure(figsize=(10, 6))
plt.plot(sorted_distances, cdf, color="darkred", linewidth=2)
plt.title("Cumulative Distribution of Distances to Nearest Service Point / Site")
plt.xlabel("Distance (km)")
plt.ylabel("Cumulative Percentage")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("distance_cdf.png", dpi=300)
plt.close()

print("\nGenerated files:")
print("- coverage_distribution_summary.csv")
print("- distance_histogram.png")
print("- distance_cdf.png")

# -----------------------------
# 6. Probability Distribution (PDF) Plot
# -----------------------------


plt.figure(figsize=(10, 6))
sns.kdeplot(df["distance_km"], fill=True, color="purple", linewidth=2)

plt.title("Probability Distribution of Settlement Distances to Nearest Service Point / Site")
plt.xlabel("Distance (km)")
plt.ylabel("Probability Density")
plt.grid(alpha=0.3)
plt.tight_layout()

# Save PNG
plt.savefig("distance_pdf.png", dpi=300)

# Save PDF
plt.savefig("distance_pdf.pdf")

plt.close()