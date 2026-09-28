"""
generate_test_data.py — Drishti Test Dataset Generator

Generates a small (< 200 records), deterministic CSV with embedded
test scenarios for manual and automated testing of the analytics engine.

Usage:
    python generate_test_data.py

Output:
    test_crime_data.csv (in the same src/ directory)

Test scenarios embedded:
    Area-03  → consistent high-volume hotspot (18 incidents/month, all 6 months)
    Area-07  → rising trend  (2/month for months 1-4, then 20/month for months 5-6)
    Area-05  → festival effect (incidents logged with nearby_event=Festival)
    Area-01, Area-02  → quiet low-baseline zones (2/month each)
    Area-09  → mixed events (Market Day, Cricket Match, None)
    Area-04  → zero incidents (edge case: graceful empty-zone handling)
"""

import pandas as pd
import random

random.seed(99)

crime_types = ["Theft", "Burglary", "Robbery", "Assault", "Vandalism", "Chain Snatching"]
day_map = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday",
           4: "Friday", 5: "Saturday", 6: "Sunday"}


def make_record(month, area, hour, event="No Event", crime_weight=None):
    day = random.randint(1, 28)
    dt = pd.Timestamp(f"2026-{month:02d}-{day:02d}")
    if crime_weight is None:
        crime_weight = [0.30, 0.20, 0.15, 0.15, 0.12, 0.08]
    return {
        "date": dt.strftime("%Y-%m-%d"),
        "time": f"{hour:02d}:{random.choice([0, 15, 30, 45]):02d}",
        "day_of_week": day_map[dt.dayofweek],
        "area": area,
        "crime_type": random.choices(crime_types, weights=crime_weight, k=1)[0],
        "nearby_event": event,
    }


records = []

# ─── SCENARIO A: Area-03 — steady high-volume hotspot ─────────────────────────
# Expected: highest total_incidents, top risk score, trend = Stable
for month in range(1, 7):
    for _ in range(18):
        records.append(make_record(month, "Area-03", random.randint(19, 23),
                                   crime_weight=[0.40, 0.20, 0.15, 0.10, 0.10, 0.05]))

# ─── SCENARIO B: Area-07 — rising trend ───────────────────────────────────────
# Low months 1-4 (2/month), then heavy concentration in June only (last ~28 days)
# so recent_30d >> prev_30d → trend_direction = "Rising"
for month in range(1, 5):
    for _ in range(2):
        records.append(make_record(month, "Area-07", random.randint(10, 18)))
# Month 5: a few (falls in prev_30d window)
for _ in range(4):
    records.append({
        "date": "2026-05-10",
        "time": "21:00",
        "day_of_week": "Sunday",
        "area": "Area-07",
        "crime_type": "Theft",
        "nearby_event": "No Event",
    })
# Month 6 (June = last 30 days from max date 2026-06-28): heavy spike
for day in [2, 4, 5, 7, 8, 10, 11, 12, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28]:
    dt = pd.Timestamp(f"2026-06-{day:02d}")
    records.append({
        "date": dt.strftime("%Y-%m-%d"),
        "time": f"{random.choice([19,20,21,22,23]):02d}:00",
        "day_of_week": {0:"Monday",1:"Tuesday",2:"Wednesday",3:"Thursday",
                        4:"Friday",5:"Saturday",6:"Sunday"}[dt.dayofweek],
        "area": "Area-07",
        "crime_type": random.choices(crime_types, weights=[0.25,0.25,0.20,0.15,0.10,0.05], k=1)[0],
        "nearby_event": "No Event",
    })

# ─── SCENARIO C: Area-05 — festival event effect ──────────────────────────────
# To get a meaningful event multiplier, we need:
#   - Some records WITHOUT a festival (no-event baseline)
#   - Some records WITH a festival (clustered on fewer dates = higher per-day rate)
# Add 20 no-event background records spread across the 6 months
for month in range(1, 7):
    for _ in range(3):
        records.append(make_record(month, "Area-05", random.randint(10, 17),
                                   event="No Event",
                                   crime_weight=[0.35, 0.20, 0.15, 0.15, 0.10, 0.05]))
# Add 18 festival records but on only 3 unique festival dates (6 incidents/date → high rate)
for festival_date in ["2026-02-15", "2026-04-14", "2026-06-10"]:
    dt = pd.Timestamp(festival_date)
    dow = {0:"Monday",1:"Tuesday",2:"Wednesday",3:"Thursday",
           4:"Friday",5:"Saturday",6:"Sunday"}[dt.dayofweek]
    for _ in range(6):
        records.append({
            "date": festival_date,
            "time": f"{random.choice([18,19,20,21,22]):02d}:{random.choice([0,15,30,45]):02d}",
            "day_of_week": dow,
            "area": "Area-05",
            "crime_type": random.choices(crime_types, weights=[0.35,0.20,0.15,0.15,0.10,0.05], k=1)[0],
            "nearby_event": "Festival",
        })

# ─── SCENARIO D: Area-01, Area-02 — quiet / low-baseline zones ────────────────
# Expected: low risk scores, trend = Stable or Declining
for area in ["Area-01", "Area-02"]:
    for month in range(1, 7):
        for _ in range(2):
            records.append(make_record(month, area, random.randint(9, 17),
                                       crime_weight=[0.50, 0.15, 0.10, 0.10, 0.10, 0.05]))

# ─── SCENARIO E: Area-09 — mixed events (Market Day + Cricket Match) ──────────
# To get multiplier > 1: cluster multiple incidents per Market Day / Cricket Match date
for month in range(1, 7):
    # 4 no-event records per month (1 incident/day spread)
    for _ in range(4):
        records.append(make_record(month, "Area-09",
                                   random.choice([10, 11, 12, 13]),
                                   event="No Event",
                                   crime_weight=[0.30, 0.20, 0.20, 0.15, 0.10, 0.05]))
# 2 Market Day dates with 4 incidents each
for md_date in ["2026-03-08", "2026-05-17"]:
    dt = pd.Timestamp(md_date)
    dow = {0:"Monday",1:"Tuesday",2:"Wednesday",3:"Thursday",
           4:"Friday",5:"Saturday",6:"Sunday"}[dt.dayofweek]
    for _ in range(4):
        records.append({
            "date": md_date,
            "time": f"{random.choice([11,12,13,20,21]):02d}:00",
            "day_of_week": dow,
            "area": "Area-09",
            "crime_type": random.choices(crime_types, weights=[0.30,0.20,0.20,0.15,0.10,0.05], k=1)[0],
            "nearby_event": "Market Day",
        })
# 2 Cricket Match dates with 4 incidents each
for cm_date in ["2026-04-06", "2026-06-22"]:
    dt = pd.Timestamp(cm_date)
    dow = {0:"Monday",1:"Tuesday",2:"Wednesday",3:"Thursday",
           4:"Friday",5:"Saturday",6:"Sunday"}[dt.dayofweek]
    for _ in range(4):
        records.append({
            "date": cm_date,
            "time": f"{random.choice([20,21,22]):02d}:00",
            "day_of_week": dow,
            "area": "Area-09",
            "crime_type": random.choices(crime_types, weights=[0.30,0.20,0.20,0.15,0.10,0.05], k=1)[0],
            "nearby_event": "Cricket Match",
        })

# ─── SCENARIO F: Area-04 — zero incidents (edge case) ─────────────────────────
# No records added. Tests that explain_zone() and suggest_patrol() handle
# an area with zero incidents without crashing.

# ─── Build & export ────────────────────────────────────────────────────────────
df = pd.DataFrame(records)
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date").reset_index(drop=True)
df["date"] = df["date"].dt.strftime("%Y-%m-%d")
df.to_csv("test_crime_data.csv", index=False)

print(f"Generated {len(df)} records")
print(f"Date range: {df['date'].min()} to {df['date'].max()}")
print(f"Areas: {sorted(df['area'].unique())}")
print()
print("Incident count per area:")
print(df["area"].value_counts().sort_index())
print()
print("Crime type distribution:")
print(df["crime_type"].value_counts())
print()
print("Event distribution:")
print(df["nearby_event"].value_counts())
