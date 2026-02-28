import os
import time
import requests
import pandas as pd
from tqdm import tqdm


# ==========================================================
# 1️⃣ State Coordinate Lookup (Centroids)
# ==========================================================

STATE_COORDS = {
    "andhra pradesh": (15.9129, 79.7400),
    "assam": (26.2006, 92.9376),
    "bihar": (25.0961, 85.3131),
    "chhattisgarh": (21.2787, 81.8661),
    "gujarat": (22.2587, 71.1924),
    "haryana": (29.0588, 76.0856),
    "himachal pradesh": (31.1048, 77.1734),
    "jharkhand": (23.6102, 85.2799),
    "karnataka": (15.3173, 75.7139),
    "kerala": (10.8505, 76.2711),
    "madhya pradesh": (22.9734, 78.6569),
    "maharashtra": (19.7515, 75.7139),
    "odisha": (20.9517, 85.0985),
    "punjab": (31.1471, 75.3412),
    "tamil nadu": (11.1271, 78.6569),
    "telangana": (18.1124, 79.0193),
    "uttar pradesh": (26.8467, 80.9462),
    "uttarakhand": (30.0668, 79.0193),
    "west bengal": (22.9868, 87.8550),
}


# ==========================================================
# 2️⃣ NASA POWER API CALL (Monthly)
# ==========================================================

def fetch_climate_for_state(state, lat, lon, year_start, year_end):

    url = (
        "https://power.larc.nasa.gov/api/temporal/monthly/point?"
        "parameters=T2M,PRECTOTCORR,RH2M"
        "&community=RE"
        f"&latitude={lat}"
        f"&longitude={lon}"
        f"&start={year_start}"
        f"&end={year_end}"
        "&format=json"
    )

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()

        if "properties" not in data:
            print(f"⚠️ No data for {state}")
            return pd.DataFrame()

        pars = data["properties"]["parameter"]

        records = []

        for year_month in pars["T2M"].keys():

         # Keep only YYYYMM (monthly data)
            if len(str(year_month)) != 6:
             continue

            records.append({
                "state": state,
                "year_month": year_month,
                "temperature_nasa": pars["T2M"].get(year_month),
                "rainfall_nasa": pars["PRECTOTCORR"].get(year_month),
                "humidity_nasa": pars["RH2M"].get(year_month)
            })

        return pd.DataFrame(records)

    except Exception as e:
        print(f"❌ Error fetching {state}: {e}")
        return pd.DataFrame()


# ==========================================================
# 3️⃣ BUILD FULL ANNUAL CLIMATE DATASET
# ==========================================================

def build_climate_dataset(year_start, year_end):

    all_data = []

    for state, (lat, lon) in tqdm(STATE_COORDS.items()):
        df = fetch_climate_for_state(state, lat, lon, year_start, year_end)

        if not df.empty:
            all_data.append(df)

        time.sleep(0.5)  # avoid API throttling

    if not all_data:
        raise ValueError("No climate data fetched.")

    # ----------------------------------------------------------
    # Combine all states
    # ----------------------------------------------------------

    climate_df = pd.concat(all_data, ignore_index=True)

    # ----------------------------------------------------------
    # Convert YYYYMM → Year + Month
    # ----------------------------------------------------------

# ----------------------------------------------------------
# Extract year and month safely
# ----------------------------------------------------------

    climate_df["year_month"] = climate_df["year_month"].astype(str)

   # Keep only YYYYMM format
    climate_df = climate_df[
      climate_df["year_month"].str.match(r"^\d{6}$")
    ]

   # Extract year and month
    climate_df["year"] = climate_df["year_month"].str[:4].astype(int)
    climate_df["month"] = climate_df["year_month"].str[4:].astype(int)

   # Remove invalid months (NASA includes 13 for annual summary)
    climate_df = climate_df[
      (climate_df["month"] >= 1) &
      (climate_df["month"] <= 12)
   ]

    climate_df.drop(columns=["year_month"], inplace=True)

    # ----------------------------------------------------------
    # Convert rainfall (mm/day) → true monthly total
    # ----------------------------------------------------------

    climate_df["days_in_month"] = pd.to_datetime(
        climate_df["year"].astype(str) + "-" +
        climate_df["month"].astype(str) + "-01"
    ).dt.days_in_month

    climate_df["rainfall_monthly_total"] = (
        climate_df["rainfall_nasa"] * climate_df["days_in_month"]
    )

    # ----------------------------------------------------------
    # Aggregate Monthly → Annual
    # ----------------------------------------------------------

    annual_climate = (
        climate_df
        .groupby(["state", "year"])
        .agg({
            "temperature_nasa": "mean",
            "rainfall_monthly_total": "sum",
            "humidity_nasa": "mean"
        })
        .reset_index()
    )

    annual_climate.rename(
        columns={"rainfall_monthly_total": "rainfall_nasa"},
        inplace=True
    )

    return annual_climate


# ==========================================================
# 4️⃣ MAIN EXECUTION
# ==========================================================

if __name__ == "__main__":

    print("Loading cleaned crop dataset...")

    crop_path = "data/cleaned/final_state_crop_dataset.csv"
    df = pd.read_csv(crop_path)

    raw_start = int(df["year"].min())
    raw_end = int(df["year"].max())

    year_start = max(raw_start, 1981)
    year_end = raw_end

    print(f"Fetching NASA POWER climate data from {year_start} to {year_end}...")

    annual_climate = build_climate_dataset(year_start, year_end)

    # Sanity check
    print("\n=== Annual Climate Summary ===")
    print(annual_climate.describe())

    os.makedirs("data/cleaned", exist_ok=True)

    climate_path = "data/cleaned/nasa_power_annual_climate.csv"
    annual_climate.to_csv(climate_path, index=False)

    print("\n✅ Annual climate data saved successfully.")
    print(annual_climate.head())