import pandas as pd
from src.features.feature_engineering import run_feature_pipeline


def main():

    # ----------------------------------------------------------
    # Load merged dataset (WITH NASA climate)
    # ----------------------------------------------------------

    df = pd.read_csv("data/cleaned/final_state_crop_with_climate.csv")
    rules_df = pd.read_csv("data/cleaned/crop_disease_rules.csv")

    # ----------------------------------------------------------
    # Run feature engineering
    # ----------------------------------------------------------

    df = run_feature_pipeline(df, rules_df)
    
    
       # ----------------------------------------------------------
    # 🔎 Stress Sanity Check (Add Here)
    # ----------------------------------------------------------

    print("\n=== Stress Distribution Check ===")
    print(df[[
        "climate_stress_norm",
        "disease_risk_norm",
        "nutrient_stress_norm"
    ]].describe())

    # ----------------------------------------------------------
    # Save final enriched dataset
    # ----------------------------------------------------------

    df.to_csv("data/cleaned/final_enriched_dataset.csv", index=False)

    print("Feature engineering complete.")
    print("Rows:", len(df))
    print("Columns:", len(df.columns))

    # ----------------------------------------------------------
    # Sanity check for NASA climate
    # ----------------------------------------------------------

    print("\nClimate Summary:")
    print(df[["temperature_nasa","rainfall_nasa","humidity_nasa"]].describe())
    
    print(df["disease_risk_norm"].value_counts())
    print(df["disease_risk_norm"].describe())
    print(df["climate_stress_norm"].value_counts().head(10))
    print(df["climate_stress_norm"].describe())
    print(df.groupby("state")["climate_stress_norm"].mean().sort_values())
    print("Answer of groupby year -----")
    print(df.groupby("year")["climate_stress_norm"].mean())
    


if __name__ == "__main__":
    main()
    
    