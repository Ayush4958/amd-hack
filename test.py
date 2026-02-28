from src.analysis.analysis import state_level_summary
import pandas as pd

df = pd.read_csv("data/cleaned/final_enriched_dataset.csv")
print(state_level_summary(df).head(10))