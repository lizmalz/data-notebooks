import pandas as pd
import json

# === CONFIGURATION ===
input_file = "state_lga_wards_polling_units.json"   # Replace with your JSON filename
csv_output = "polling_units.csv"
excel_output = "election_summary.xlsx"

# === LOAD JSON ===
with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# === FLATTEN STRUCTURE WITH ERROR HANDLING ===
rows = []
for state_entry in data:
    try:
        state = state_entry.get("state", "UNKNOWN_STATE")
        for lga_entry in state_entry.get("lgas", []):
            try:
                lga = lga_entry.get("lga", "UNKNOWN_LGA")
                for ward_entry in lga_entry.get("wards", []):
                    try:
                        ward = ward_entry.get("ward", "UNKNOWN_WARD")
                        for pu in ward_entry.get("polling_units", []):
                            # Ensure polling unit is a string
                            if isinstance(pu, str):
                                rows.append({
                                    "state": state,
                                    "lga": lga,
                                    "ward": ward,
                                    "polling_unit": pu
                                })
                            else:
                                print(f"⚠️ Skipped non-string polling unit in {state}/{lga}/{ward}: {pu}")
                    except Exception as e:
                        print(f"⚠️ Error processing ward in {state}/{lga}: {e}")
            except Exception as e:
                print(f"⚠️ Error processing LGA in {state}: {e}")
    except Exception as e:
        print(f"⚠️ Error processing state entry: {e}")

df = pd.DataFrame(rows)

# === SUMMARY TABLES ===
summary_lga = df.groupby(['state','lga']).size().reset_index(name='polling_unit_count')
summary_state = df.groupby('state').size().reset_index(name='polling_unit_count')

# === EXPORT ===
df.to_csv(csv_output, index=False, encoding="utf-8")

with pd.ExcelWriter(excel_output, engine="openpyxl") as writer:
    df.to_excel(writer, sheet_name="Polling Units", index=False)
    summary_lga.to_excel(writer, sheet_name="Summary by LGA", index=False)
    summary_state.to_excel(writer, sheet_name="Summary by State", index=False)

print(f"✅ Export complete: {csv_output} and {excel_output}")