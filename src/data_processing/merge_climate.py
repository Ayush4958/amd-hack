import pandas as pd


def main():

    print("\nLoading datasets...")

    crop_path = "data/cleaned/final_state_crop_dataset.csv"
    climate_path = "data/cleaned/nasa_power_annual_climate.csv"

    crop_df = pd.read_csv(crop_path)
    climate_df = pd.read_csv(climate_path)

    # ----------------------------------------------------------
    # Basic Validation
    # ----------------------------------------------------------

    print("\nCrop dataset shape:", crop_df.shape)
    print("Climate dataset shape:", climate_df.shape)

    # Ensure lowercase + strip (safety)
    crop_df["state"] = crop_df["state"].str.lower().str.strip()
    climate_df["state"] = climate_df["state"].str.lower().str.strip()

    # Ensure year is int
    crop_df["year"] = crop_df["year"].astype(int)
    climate_df["year"] = climate_df["year"].astype(int)

    # ----------------------------------------------------------
    # Merge (INNER JOIN)
    # ----------------------------------------------------------

    merged = crop_df.merge(
        climate_df,
        on=["state", "year"],
        how="inner"
    )

    print("\nMerged shape:", merged.shape)

    # ----------------------------------------------------------
    # Null Check (Climate)
    # ----------------------------------------------------------

    climate_cols = ["temperature_nasa", "rainfall_nasa", "humidity_nasa"]

    print("\nClimate Null Check:")
    print(merged[climate_cols].isnull().sum())

    # ----------------------------------------------------------
    # Validate year coverage
    # ----------------------------------------------------------

    print("\nYear range after merge:",
          merged["year"].min(), "-", merged["year"].max())

    print("States after merge:", merged["state"].nunique())

    # ----------------------------------------------------------
    # Save
    # ----------------------------------------------------------

    output_path = "data/cleaned/final_state_crop_with_climate.csv"
    merged.to_csv(output_path, index=False)

    print("\nMerged dataset saved successfully.")
    print("Saved to:", output_path)


if __name__ == "__main__":
    main()