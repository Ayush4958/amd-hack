import pandas as pd
LOW_YIELD_THRESHOLD = 0.40

# ---------------------------------------------------
# 1️ State-Level Policy Summary
# ---------------------------------------------------
def state_level_summary(df):

    summary = (
        df.groupby("state")
        .agg(
            avg_agro_stress=("agro_stress_index", "mean"),
            avg_resilience=("resilience_score", "mean"),
            high_priority_pct=("intervention_priority",
                               lambda x: (x == "High Priority").mean() * 100),
            fragile_system_pct=("fragile_system", "mean")
        )
        .reset_index()
    )

    summary["fragile_system_pct"] *= 100

    return summary.sort_values("avg_agro_stress", ascending=False)


# ---------------------------------------------------
# 2️ Crop-Level Resilience Ranking
# ---------------------------------------------------
def crop_resilience_ranking(df):

    ranking = (
        df.groupby("crop")
        .agg(
            avg_resilience=("resilience_score", "mean"),
            avg_stress=("agro_stress_index", "mean")
        )
        .reset_index()
        .sort_values("avg_resilience", ascending=False)
    )

    return ranking


# ---------------------------------------------------
# 3️ Top High-Risk Systems
# ---------------------------------------------------
def top_high_risk_systems(df, top_n=10):

    return (
        df.sort_values("agro_stress_index", ascending=False)
        [["state", "crop", "year",
          "agro_stress_index",
          "resilience_score",
          "intervention_priority"]]
        .head(top_n)
    )


# ---------------------------------------------------
# 4️ Most Fragile Systems
# ---------------------------------------------------
def most_fragile_systems(df, top_n=10):

    return (
        df.sort_values("resilience_score")
        [["state", "crop", "year",
          "resilience_score",
          "agro_stress_index",
          "fragile_system"]]
        .head(top_n)
    )


# ---------------------------------------------------
# 5️ Heatmap Pivot (State × Crop Stress)
# ---------------------------------------------------
def stress_heatmap_matrix(df):

    pivot = (
        df.pivot_table(
            values="agro_stress_index",
            index="state",
            columns="crop",
            aggfunc="mean"
        )
    )

    return pivot

def compute_prediction_confidence(df):

    df["predicted_low_yield"] = (
        df["agro_stress_index"] > LOW_YIELD_THRESHOLD
    ).astype(int)

    mean_yield = df.groupby(["state", "crop"])["yield"].transform("mean")
    std_yield = df.groupby(["state", "crop"])["yield"].transform("std")

    df["actual_low_yield"] = (
        df["yield"] < (mean_yield - std_yield)
    ).astype(int)

    summary = df.groupby(["state", "crop"]).agg(
        total_years=("yield", "count"),
        predicted_lows=("predicted_low_yield", "sum"),
        actual_lows=("actual_low_yield", "sum"),
        correct_lows=(
            "predicted_low_yield",
            lambda x: ((x == 1) & 
                       (df.loc[x.index, "actual_low_yield"] == 1)).sum()
        )
    ).reset_index()

    # Recall-based confidence
    summary["confidence_score"] = (
        summary["correct_lows"] /
        summary["actual_lows"].replace(0, 1)
    )
    # Penalize small sample sizes
    summary.loc[summary["actual_lows"] < 3, "confidence_score"] *= 0.5

    return summary


