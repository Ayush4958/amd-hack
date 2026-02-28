import pandas as pd
import os

# ==========================================================
# 1️ BUILD STATE-LEVEL BACKBONE (HISTORICAL DATASET)
# ==========================================================

hist_path = "data/data_raw/indian-historical-crop-yield-and-weather-data/Custom_Crops_yield_Historical_Dataset.csv"
hist = pd.read_csv(hist_path)

# Standardize column names
hist.columns = hist.columns.str.lower().str.strip()

# Rename important columns
hist.rename(columns={
    'state name': 'state',
    'dist name': 'district',
    'yield_kg_per_ha': 'yield',
    'rainfall_mm': 'rainfall',
    'temperature_c': 'temperature',
    'humidity_%': 'humidity'
}, inplace=True)

# Standardize text fields
hist['state'] = hist['state'].str.lower().str.strip()
hist['crop'] = hist['crop'].str.lower().str.strip()

# ----------------------------------------------------------
# 🚨 REMOVE historical climate (NASA will replace this)
# ----------------------------------------------------------

hist.drop(columns=['rainfall', 'temperature', 'humidity'], inplace=True)

print("\nHistorical Raw Shape:", hist.shape)

# ----------------------------------------------------------
# Aggregate District → State level
# ----------------------------------------------------------

state_df = (
    hist.groupby(['state', 'crop', 'year'])
    .agg({
        'yield': 'mean',
        'n_req_kg_per_ha': 'mean',
        'p_req_kg_per_ha': 'mean',
        'k_req_kg_per_ha': 'mean'
    })
    .reset_index()
)

# Enforce numeric
state_df['year'] = state_df['year'].astype(int)
state_df['yield'] = pd.to_numeric(state_df['yield'], errors='coerce')

print("\nState-Level Shape:", state_df.shape)
print("\nStates:", state_df['state'].nunique())
print("Crops:", state_df['crop'].nunique())
print("Year Range:", state_df['year'].min(), "-", state_df['year'].max())
print("\nNull Check Before Soil Merge:")
print(state_df.isnull().sum())


# ==========================================================
# 2️ CLEAN SOIL DATASET
# ==========================================================

soil_path = "data/data_raw/crop-yield-data-with-soil-and-weather-dataset/state_soil_data.csv"
soil_df = pd.read_csv(soil_path)

soil_df.columns = soil_df.columns.str.lower().str.strip()
soil_df['state'] = soil_df['state'].str.lower().str.strip()

# Fix naming mismatches
state_mapping = {
    "orissa": "odisha"
}
state_df['state'] = state_df['state'].replace(state_mapping)

# Remove trailing spaces
state_df['state'] = state_df['state'].str.strip()
soil_df['state'] = soil_df['state'].str.strip()

print("\nState Mismatch Check:")
print("Missing from soil:", set(state_df['state']) - set(soil_df['state']))
print("Extra in soil:", set(soil_df['state']) - set(state_df['state']))


# ==========================================================
# 3️ MERGE SOIL INTO STATE DATA
# ==========================================================

state_df = state_df.merge(soil_df, on='state', how='left')

print("\nNull Check After Soil Merge:")
print(state_df[['n','p','k','ph']].isnull().sum())

# Drop Rajasthan only if soil truly missing
if state_df[state_df['state'] == 'rajasthan'][['n','p','k','ph']].isnull().any().any():
    state_df = state_df[state_df['state'] != 'rajasthan']
    print("\nRajasthan removed due to missing soil data.")

print("\nStates After Soil Merge:", state_df['state'].nunique())


# ==========================================================
# 4️ DROP PRE-1981 YEARS (Climate alignment)
# ==========================================================

state_df = state_df[state_df['year'] >= 1981]

print("\nAfter Filtering Year >= 1981:")
print("Year Range:", state_df['year'].min(), "-", state_df['year'].max())


# ==========================================================
# 5️ CREATE STRUCTURED DISEASE RULE DATASET
# ==========================================================

disease_rules = [
    {"crop": "rice", "disease": "rice blast",
     "temp_min": 20, "temp_max": 28, "humidity_min": 80, "rainfall_min": 100},

    {"crop": "rice", "disease": "bacterial leaf blight",
     "temp_min": 25, "temp_max": 34, "humidity_min": 75, "rainfall_min": 120},

    {"crop": "rice", "disease": "sheath blight",
     "temp_min": 24, "temp_max": 30, "humidity_min": 85, "rainfall_min": 110},

    {"crop": "maize", "disease": "maize rust",
     "temp_min": 18, "temp_max": 25, "humidity_min": 70, "rainfall_min": 80},

    {"crop": "maize", "disease": "northern leaf blight",
     "temp_min": 18, "temp_max": 27, "humidity_min": 75, "rainfall_min": 90},

    {"crop": "cotton", "disease": "cotton leaf curl virus",
     "temp_min": 25, "temp_max": 35, "humidity_min": 60, "rainfall_min": 60},

    {"crop": "cotton", "disease": "bacterial blight",
     "temp_min": 25, "temp_max": 32, "humidity_min": 70, "rainfall_min": 80},

    {"crop": "chickpea", "disease": "fusarium wilt",
     "temp_min": 20, "temp_max": 30, "humidity_min": 60, "rainfall_min": 50},

    {"crop": "chickpea", "disease": "ascochyta blight",
     "temp_min": 15, "temp_max": 25, "humidity_min": 80, "rainfall_min": 70},
]

disease_df = pd.DataFrame(disease_rules)

os.makedirs("data/cleaned", exist_ok=True)
disease_df.to_csv("data/cleaned/crop_disease_rules.csv", index=False)

print("\nDisease Rule Dataset Created.")


# ==========================================================
# 6️⃣ FINAL SAVE
# ==========================================================

state_df.to_csv("data/cleaned/final_state_crop_dataset.csv", index=False)

print("\nFinal Dataset Saved Successfully.")
print("Final Shape:", state_df.shape)
print(state_df.head())