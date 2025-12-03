import pandas as pd
from pathlib import Path

# Read the existing times.csv
BASE_DIR = Path(__file__).resolve().parent
times_path = BASE_DIR / "out" / "times.csv"
df = pd.read_csv(times_path)

# Map ranges to individual days
day_map = {
    "Mon - Fri": ["Mon", "Tue", "Wed", "Thu", "Fri"],
    "Monday - Friday": ["Mon", "Tue", "Wed", "Thu", "Fri"],
    "Sat": ["Sat"],
    "Saturday": ["Sat"],
    "Sun": ["Sun"],
    "Sunday": ["Sun"],
}

expanded_rows = []
for _, row in df.iterrows():
    days_field = str(row["days"]).strip()
    days_list = day_map.get(days_field, [d.strip() for d in days_field.split(",") if d.strip()])
    for day in days_list:
        expanded_rows.append(
            {
                "day": day,
                "start_time": row["start_time"],
                "duration_hours": row["duration_hours"],
            }
        )

expanded_df = pd.DataFrame(expanded_rows)

# Overwrite the original or write a new file
expanded_path = BASE_DIR / "out" / "times_expanded.csv"
expanded_df.to_csv(expanded_path, index=False)
print(f"Wrote expanded times to {expanded_path}")
