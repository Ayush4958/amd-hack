import pandas as pd
from src.analysis.analysis import compute_prediction_confidence
from src.analysis.analysis import (
    state_level_summary,
    crop_resilience_ranking,
    top_high_risk_systems,
    most_fragile_systems,
    stress_heatmap_matrix
)

REQUIRED_COLUMNS = [
    "temperature_nasa",
    "rainfall_nasa",
    "humidity_nasa",
    "nutrient_stress_norm",
    "climate_stress_norm",
    "disease_risk_norm"
]


def main():

    df = pd.read_csv("data/cleaned/final_enriched_dataset.csv")

    # ----------------------------------------------------------
    # Sanity Checks
    # ----------------------------------------------------------

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    print("\nNull Check:")
    print(df[REQUIRED_COLUMNS].isnull().sum())

    # ----------------------------------------------------------
    # Analysis Outputs
    # ----------------------------------------------------------

    print("\n=== STATE LEVEL SUMMARY ===")
    print(state_level_summary(df).head())

    print("\n=== CROP RESILIENCE RANKING ===")
    print(crop_resilience_ranking(df))

    print("\n=== TOP HIGH RISK SYSTEMS ===")
    print(top_high_risk_systems(df))

    print("\n=== MOST FRAGILE SYSTEMS ===")
    print(most_fragile_systems(df))

    print("\n=== STRESS HEATMAP MATRIX ===")
    print(stress_heatmap_matrix(df))
    
    print("\n=== PREDICTION CONFIDENCE ===")
    confidence_df = compute_prediction_confidence(df)
    print(confidence_df.sort_values("confidence_score", ascending=False).head())

    print("\n=== Crop Stress Variability (STD) ===")
    print(df.groupby("crop")[[
        "nutrient_stress_norm",
        "climate_stress_norm",
        "disease_risk_norm"
    ]].std())
    print(
    df.groupby(["state","crop"])[
        ["predicted_low_yield","actual_low_yield"]
    ].sum())
    

    print("\n=== THRESHOLD SWEEP (RECALL) ===")
    for t in [0.40, 0.45, 0.50, 0.55, 0.60, 0.65]:
        print(f"{t} → Recall: {evaluate_threshold(df, t):.3f}")
    

    
# ---------------------------------------------------
# Threshold Evaluation (Recall-Based)
# ---------------------------------------------------

def evaluate_threshold(df, threshold):

    temp = df.copy()

    temp["predicted"] = (
        temp["agro_stress_index"] > threshold
    ).astype(int)

    mean_yield = temp.groupby(["state","crop"])["yield"].transform("mean")
    std_yield = temp.groupby(["state","crop"])["yield"].transform("std")

    temp["actual"] = (
        temp["yield"] < (mean_yield - std_yield)
    ).astype(int)

    recall = (
        ((temp["predicted"] == 1) &
         (temp["actual"] == 1)).sum()
        / temp["actual"].sum()
    )

    return recall


if __name__ == "__main__":
    main()