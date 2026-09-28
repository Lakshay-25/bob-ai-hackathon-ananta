import pandas as pd
import numpy as np
import random

random.seed(42)
np.random.seed(42)

areas = [f"Area-{i:02d}" for i in range(1, 31)]
hotspot_areas = ["Area-03", "Area-07", "Area-12", "Area-18", "Area-22", "Area-27"]
crime_types = ["Theft", "Burglary", "Robbery", "Assault", "Vandalism", "Chain Snatching"]
events = ["None", "None", "None", "None", "None", "Market Day", "Festival", "Political Rally", "Cricket Match"]

records = []
start_date = pd.Timestamp("2026-01-01")
end_date = pd.Timestamp("2026-06-30")
dates = pd.date_range(start_date, end_date)

for _ in range(1000):
    date = random.choice(dates)
    day_name = date.day_name()
    month = date.month

    # Hotspot areas get picked more often
    if random.random() < 0.55:
        area = random.choice(hotspot_areas)
    else:
        area = random.choice(areas)

    # Evening/night bias (70% of crimes between 7PM-midnight)
    if random.random() < 0.7:
        hour = random.randint(19, 23)
    else:
        hour = random.randint(6, 18)
    minute = random.choice([0, 15, 30, 45])
    time_str = f"{hour:02d}:{minute:02d}"

    # Crime type — Theft is most common
    weights = [0.30, 0.20, 0.15, 0.15, 0.12, 0.08]
    crime_type = random.choices(crime_types, weights=weights, k=1)[0]

    # Weekend event boost
    if day_name in ["Friday", "Saturday", "Sunday"] and random.random() < 0.3:
        event = random.choice(["Market Day", "Festival", "Cricket Match", "Political Rally"])
    else:
        event = random.choice(events)

    records.append({
        "date": date.strftime("%Y-%m-%d"),
        "time": time_str,
        "day_of_week": day_name,
        "area": area,
        "crime_type": crime_type,
        "nearby_event": event
    })

# Add extra incidents in hotspot areas for months 5-6 (escalating trend)
for _ in range(150):
    date = random.choice(pd.date_range("2026-05-01", "2026-06-30"))
    day_name = date.day_name()
    area = random.choice(hotspot_areas)
    hour = random.randint(19, 23)
    minute = random.choice([0, 15, 30, 45])
    time_str = f"{hour:02d}:{minute:02d}"
    crime_type = random.choices(crime_types, weights=weights, k=1)[0]
    event = random.choice(events)
    records.append({
        "date": date.strftime("%Y-%m-%d"),
        "time": time_str,
        "day_of_week": day_name,
        "area": area,
        "crime_type": crime_type,
        "nearby_event": event
    })

df = pd.DataFrame(records)
df = df.sort_values("date").reset_index(drop=True)
df.to_csv("crime_data.csv", index=False)
print(f"Generated {len(df)} records across {df['area'].nunique()} areas")
print(f"Date range: {df['date'].min()} to {df['date'].max()}")
print(f"\nTop 10 areas by incident count:")
print(df['area'].value_counts().head(10))
print(f"\nCrime type distribution:")
print(df['crime_type'].value_counts())
print(f"\nEvent distribution:")
print(df['nearby_event'].value_counts())
