import pandas as pd
from src.features.feature_engineering import run_feature_pipeline
from src.analysis.analysis import compute_prediction_confidence
from src.dashboard.farmer_dashboard import generate_farmer_dashboard
from src.dashboard.researcher_dashboard import generate_researcher_dashboard


def main():

    df = pd.read_csv("data/cleaned/final_state_crop_with_climate.csv")
    rules_df = pd.read_csv("data/cleaned/crop_disease_rules.csv")

    df = run_feature_pipeline(df, rules_df)

    # Merge confidence score
    confidence_df = compute_prediction_confidence(df)

    df = df.merge(
        confidence_df[["state", "crop", "confidence_score"]],
        on=["state", "crop"],
        how="left"
    )

    df.to_csv("data/cleaned/final_enriched_dataset.csv", index=False)

    print("Feature engineering complete.")
    print("Rows:", len(df))
    print("Columns:", len(df.columns))

    generate_farmer_dashboard()
    generate_researcher_dashboard()


if __name__ == "__main__":
    main()
    
    