import pandas as pd
import numpy as np


# ---------------------------------------------------
# Utility: Safe Group Normalization (0–1 scaling)
# ---------------------------------------------------
def _group_normalize(df, group_col, target_col, new_col_name):

    df[new_col_name] = (
        df.groupby(group_col)[target_col]
        .transform(lambda x: x / x.max() if x.max() != 0 else 0)
    )

    return df


# ---------------------------------------------------
# 1️. Nutrient Features
# ---------------------------------------------------
def add_nutrient_features(df):

    df["nutrient_stress"] = (
        abs(df["n_req_kg_per_ha"] - df["n"]) +
        abs(df["p_req_kg_per_ha"] - df["p"]) +
        abs(df["k_req_kg_per_ha"] - df["k"])
    )

    df = _group_normalize(
        df,
        "crop",
        "nutrient_stress",
        "nutrient_stress_norm"
    )

    return df

# ---------------------------------------------------
# 2️ Climate Features (Volatility-Based, Annual Data)
# ---------------------------------------------------

def add_climate_features(df):

    group_cols = ["state", "crop"]

    # ---------------------------------------------------
    # 1️ Local Mean Baseline
    # ---------------------------------------------------
    df["temp_mean"] = df.groupby(group_cols)["temperature_nasa"].transform("mean")
    df["rain_mean"] = df.groupby(group_cols)["rainfall_nasa"].transform("mean")

    # ---------------------------------------------------
    # 2️ Anomaly (Deviation From Local Normal)
    # ---------------------------------------------------
    df["temp_anomaly"] = df["temperature_nasa"] - df["temp_mean"]
    df["rain_anomaly"] = df["rainfall_nasa"] - df["rain_mean"]

    df["temp_anomaly_norm"] = (
        df.groupby(group_cols)["temp_anomaly"]
        .transform(lambda x: x / x.abs().max() if x.abs().max() != 0 else 0)
    )

    df["rain_anomaly_norm"] = (
        df.groupby(group_cols)["rain_anomaly"]
        .transform(lambda x: x / x.abs().max() if x.abs().max() != 0 else 0)
    )

    # ---------------------------------------------------
    # 3️ Extreme Events (Top/Bottom 10%)
    # ---------------------------------------------------
    temp_threshold = df.groupby(group_cols)["temperature_nasa"] \
        .transform(lambda x: x.quantile(0.90))
    df["heat_stress"] = (df["temperature_nasa"] >= temp_threshold).astype(int)

    rain_threshold = df.groupby(group_cols)["rainfall_nasa"] \
        .transform(lambda x: x.quantile(0.10))
    df["drought_stress"] = (df["rainfall_nasa"] <= rain_threshold).astype(int)

    # ---------------------------------------------------
    # 4️ Rolling 5-Year Volatility (Inter-Year Instability)
    # ---------------------------------------------------
    df = df.sort_values(["state", "crop", "year"])

    df["temp_volatility"] = (
        df.groupby(group_cols)["temperature_nasa"]
        .transform(lambda x: x.rolling(5, min_periods=3).std())
    )

    df["rain_volatility"] = (
        df.groupby(group_cols)["rainfall_nasa"]
        .transform(lambda x: x.rolling(5, min_periods=3).std())
    )

    df["temp_volatility"] = df["temp_volatility"].fillna(0)
    df["rain_volatility"] = df["rain_volatility"].fillna(0)

    df = _group_normalize(df, "crop", "temp_volatility", "temp_volatility_norm")
    df = _group_normalize(df, "crop", "rain_volatility", "rain_volatility_norm")

    # ---------------------------------------------------
    # 5️ Final Climate Stress Composite
    # ---------------------------------------------------
    df["climate_stress"] = (
        abs(df["temp_anomaly_norm"]) +
        abs(df["rain_anomaly_norm"]) +
        df["heat_stress"] +
        df["drought_stress"] +
        df["temp_volatility_norm"] +
        df["rain_volatility_norm"]
    )

    df = _group_normalize(df, "crop", "climate_stress", "climate_stress_norm")

    # ---------------------------------------------------
    # Clean Intermediate Columns
    # ---------------------------------------------------
    df.drop(columns=[
        "temp_mean",
        "rain_mean",
        "temp_anomaly",
        "rain_anomaly",
        "temp_volatility",
        "rain_volatility"
    ], inplace=True)

    return df
# ---------------------------------------------------
# 3️. Disease Risk (Rule-Based)
# ---------------------------------------------------

def add_disease_risk(df, rules_df):

    df["disease_risk_score"] = 0

    for _, rule in rules_df.iterrows():

        mask = (
            (df["crop"] == rule["crop"]) &
            (df["temperature_nasa"] >= rule["temp_min"]) &
            (df["temperature_nasa"] <= rule["temp_max"]) &
            (df["humidity_nasa"] >= rule["humidity_min"]) &
            (df["rainfall_nasa"] >= rule["rainfall_min"])
        )

        df.loc[mask, "disease_risk_score"] += 1

    # Normalize per crop
    df = _group_normalize(df, "crop", "disease_risk_score", "disease_risk_norm")

    return df
# ---------------------------------------------------
# 4️. Yield Stability Features
# ---------------------------------------------------
def add_yield_features(df):

    group_cols = ["state", "crop"]

    df["mean_yield"] = df.groupby(group_cols)["yield"].transform("mean")
    df["yield_anomaly"] = df["yield"] - df["mean_yield"]

    df["yield_volatility"] = (
        df.groupby(group_cols)["yield"]
        .transform("std")
    )

    # Replace NaN volatility (if single year) with 0
    df["yield_volatility"] = df["yield_volatility"].fillna(0)

    # Normalize volatility per crop
    df = _group_normalize(df, "crop", "yield_volatility", "yield_volatility_norm")

    # Stability score
    df["stability_score"] = 1 - df["yield_volatility_norm"]

    return df


# ---------------------------------------------------
# 5️. Composite Decision-Support Features
# ---------------------------------------------------
def add_decision_support_features(df):

    # Agro Stress Index (Primary Risk Indicator)
    df["agro_stress_index"] = (
        0.4 * df["nutrient_stress_norm"] +
        0.4 * df["climate_stress_norm"] +
        0.2 * df["disease_risk_norm"]
    )

    # Stress Interaction (Compound Risk)
    df["stress_interaction"] = (
        df["nutrient_stress_norm"] *
        df["climate_stress_norm"]
    )

    # Resilience Score
    df["resilience_score"] = (
        df["stability_score"] *
        (1 - df["agro_stress_index"])
    )

    return df

def add_priority_classification(df):

    high_cutoff = df["agro_stress_index"].quantile(0.80)
    moderate_cutoff = df["agro_stress_index"].quantile(0.50)

    conditions = [
        df["agro_stress_index"] >= high_cutoff,
        df["agro_stress_index"] >= moderate_cutoff
    ]

    choices = ["High Priority", "Moderate Priority"]

    df["intervention_priority"] = np.select(
        conditions,
        choices,
        default="Low Priority"
    )

    df["fragile_system"] = (
        (df["agro_stress_index"] >= high_cutoff) &
        (df["resilience_score"] <= df["resilience_score"].quantile(0.30))
    ).astype(int)

    return df

# ---------------------------------------------------
# MASTER PIPELINE
# ---------------------------------------------------
def run_feature_pipeline(df, rules_df):

    df = add_nutrient_features(df)
    df = add_climate_features(df)
    df = add_disease_risk(df, rules_df)
    df = add_yield_features(df)
    df = add_decision_support_features(df)
    df = add_priority_classification(df)

    return df



 

