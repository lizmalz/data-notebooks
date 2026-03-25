import numpy as np
import matplotlib.pyplot as plt

# Constants
annual_rate = 0.012
weekly_n = 52
monthly_n = 12

# Function to compute compound interest
def compound_interest(P, r, n, t):
    return P * (1 + r / n) ** (n * t)

# Time range to evaluate (in years)
time_years = np.linspace(0, 10, 1000)

# Calculate the amounts for weekly and monthly compounding
A_weekly = compound_interest(1, annual_rate, weekly_n, time_years)
A_monthly = compound_interest(1, annual_rate, monthly_n, time_years)

# Calculate the difference and percentage difference
diff = np.abs(A_weekly - A_monthly)
percentage_diff = diff / A_monthly

# Find when the difference reaches 10%
threshold = 0.1
time_to_10_percent = time_years[np.where(percentage_diff >= threshold)[0][0]]

# Plotting the results
plt.figure(figsize=(10, 6))
plt.plot(time_years, A_weekly, label="Weekly Compounding", color='blue')
plt.plot(time_years, A_monthly, label="Monthly Compounding", color='green')
plt.axvline(time_to_10_percent, color='red', linestyle='--', label=f'10% Difference at t = {time_to_10_percent:.2f} years')
plt.xlabel("Time (years)")
plt.ylabel("Amount ($)")
plt.title("Comparison of Weekly and Monthly Compounding")
plt.legend()
plt.grid(True)
plt.show()

# Output the time when the difference reaches 10%
print(f"The difference reaches 10% at approximately {time_to_10_percent:.2f} years.")
