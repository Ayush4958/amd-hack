# Agro-Climate Knowledge Graph Backbone
## AMD Hackathon Project

---

## 📁 Project Structure

```
project-root/
│
├── data/
│   └── cleaned/
│       └── final_enriched_dataset.csv
│
├── src/
│   ├── processing/
│   ├── data_fetch/
│   ├── data_processing/
│   ├── features/
│   ├── graph/
│   ├── runner/
│   └── web/
│
├── static/
│   ├── css/
│   ├── images/
│   └── agro_knowledge_graph.html
│
├── requirements.txt
├── README.md
└── .gitignore
```

---



## Project Overview

This project builds a structured agro-intelligence backbone for state-level crop risk analysis and knowledge graph modeling.

The system integrates multiple agricultural dimensions into a unified analytical dataset:

* Historical crop yield data (1966–2017)
* Climate indicators (rainfall, temperature, humidity, variability, anomalies)
* Soil nutrient context (N, P, K, pH)
* Nutrient requirement benchmarks (N, P, K)
* Custom rule-based disease trigger thresholds

These components are engineered into a consolidated enriched dataset that computes:

* Climate stress index
* Nutrient stress index
* Disease risk score
* Agro stress index
* Resilience score
* Confidence score for low-yield signaling

The final dataset is graph-ready and enables:

* Crop–climate–yield relationship modeling
* Disease risk inference under environmental conditions
* Nutrient stress diagnostics
* State-level agricultural system analysis
* Knowledge graph visualization of agro relationships



## Crops Covered

- Rice
- Maize
- Cotton
- Chickpea

---

## Dataset Sources

The agricultural backbone was constructed using the following data sources:

1. **Indian Historical Crop Yield and Weather Data (Kaggle)**

   * State-level crop yield, rainfall, temperature, humidity
   * Years: 1966–2017
   * Used as the primary historical yield backbone

2. **Crop Yield Data with Soil and Weather Dataset (Kaggle)**

   * Soil nutrient values (N, P, K) and pH
   * Used to enrich crop context with soil features

3. **NASA POWER Climate Database**

   * Long-term climate indicators
   * Used to compute climate anomalies, volatility, and stress metrics

4. **Custom Rule-Based Disease Dataset (Manually Engineered)**

   * Structured disease trigger thresholds based on crop–climate relationships
   * Includes temperature range, humidity threshold, and rainfall threshold
   * Designed and encoded within this project
   * Exported as `data/cleaned/crop_disease_rules.csv`

All sources were processed and merged through the project’s pipeline to generate:

```
data/cleaned/final_enriched_dataset.csv
```

The enriched dataset is included in this repository.

No Kaggle API setup or external download is required to run the application.

External access is only required if rebuilding the full dataset from raw sources.


---


# How To Run (Step-by-Step)


## Step 1 — Install Dependencies

```bash
pip install -r requirements.txt
```

Recommended Python: 3.10+

---

## Step 2 — Generate Knowledge Graph

Run:

```bash
python src/graph/knowledge_graph.py
```

This generates:

```
static/agro_knowledge_graph.html
```

This step ensures the graph loads properly inside the web interface.

---

## Step 3 — (Optional) Rebuild Dataset From Pipeline

Only needed if you want to regenerate the enriched dataset.

Run in order:

```bash
python src/processing/clean.py
python src/data_fetch/nasa_power_climate.py
python src/data_processing/merge_climate.py
python src/features/feature_engineering.py
```

This recreates:

```
data/cleaned/final_enriched_dataset.csv
```

For normal usage, this step is not required.

---

## Step 4 — Start the Web Application

```bash
uvicorn src.web.app:app --reload
```

Open in browser:

```
http://127.0.0.1:8000
```

The application and knowledge graph will load.

---

## Project Structure

