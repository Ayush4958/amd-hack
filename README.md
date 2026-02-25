# Agro-Climate Knowledge Graph Backbone
## AMD Hackathon Project

---

## 📁 Project Structure

```
project-root/
│
├── data/                     # Dataset storage
│   ├── raw/                  # Original raw datasets
│   └── cleaned/              # Processed datasets
│
├── src/                      # Source code
│   ├── preprocessing/        # Data cleaning & preparation scripts
│   ├── ml/                   # Machine learning models
│   ├── graph/                # Knowledge graph generation logic
│   ├── api/                  # FastAPI backend services
│   └── utils/                # Helper utilities
│
├── notebooks/                # Jupyter notebooks for experiments
├── models/                   # Saved trained models
├── outputs/                  # Generated results & logs
│
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation
├── LICENSE                   # License file
└── .gitignore                # Ignored files
```

---

## Project Overview

This project builds a structured agricultural backbone dataset for knowledge graph modeling.

The system integrates:

- State-level crop yield (1966–2017)
- Climate variables (rainfall, temperature, humidity)
- Nutrient requirements (N, P, K)
- Soil nutrient levels (N, P, K, pH)
- Structured disease trigger rules

The output dataset is graph-ready and enables:

- Crop–climate–yield relationship modeling
- Disease risk inference
- Nutrient stress reasoning
- State-level agricultural analytics

---

## Crops Covered

- Rice
- Maize
- Cotton
- Chickpea

---

## Dataset Sources

This project uses the following Kaggle datasets:

1. Indian Historical Crop Yield and Weather Data  
   - Provides yield, rainfall, temperature, humidity  
   - Years: 1966–2017  
   - Used as the primary backbone  

2. Crop Yield Data with Soil and Weather Dataset  
   - Provides state-level soil NPK and pH  
   - Used to enrich backbone with soil features  

Raw datasets are excluded from this repository for size and reproducibility reasons.

---

# Data Setup (Kaggle API Required)

## 1. Create a Kaggle Account

1. Go to https://www.kaggle.com  
2. Open **Account Settings**  
3. Under **API**, click **Create New API Token**  
4. Open the downloaded `kaggle.json` file  
5. Copy the values of:
   - `username`
   - `key`

---

## Python Dependencies

Install required Python packages using:

```bash
pip install -r requirements.txt
```

## 3. Set Kaggle Credentials (Environment Variables)

### Windows (PowerShell)


```powershell
setx KAGGLE_USERNAME "your_username"
setx KAGGLE_KEY "your_api_key"
````

After running the above commands, restart your terminal.

---

### macOS / Linux

```bash
export KAGGLE_USERNAME="your_username"
export KAGGLE_KEY="your_api_key"
```

---

### 4. Create Raw Data Directory

From the project root:

```bash
mkdir data_raw
```

---

### 5. Download Required Datasets

Run the following commands inside PowerShell (Windows) or terminal (macOS/Linux):

```bash
kaggle datasets download -d zoya77/indian-historical-crop-yield-and-weather-data -p data_raw

kaggle datasets download -d anshumish/crop-yield-data-with-soil-and-weather-dataset -p data_raw
```

---

### 6. Extract the Downloaded ZIP Files

#### Windows (PowerShell)

```powershell
cd data_raw
Expand-Archive *.zip
```

#### macOS / Linux

```bash
cd data_raw
unzip "*.zip"
```

---

### 7. Run the Data Cleaning Pipeline

Return to the project root and execute:

```bash
python clean.py
```

---

## Output Files

After successful execution, the following files will be generated:

```
data_clean/
│
├── final_state_crop_dataset.csv
└── crop_disease_rules.csv
```

---

### final_state_crop_dataset.csv

Contains:

* state
* crop
* year (1966–2017)
* yield
* rainfall
* temperature
* humidity
* n_req_kg_per_ha
* p_req_kg_per_ha
* k_req_kg_per_ha
* soil_n
* soil_p
* soil_k
* soil_ph

Cleaned dataset includes:

* 19 states
* 4 crops
* No null values
* No duplicates

---

### crop_disease_rules.csv

Contains structured disease trigger rules:

* crop
* disease
* temp_min
* temp_max
* humidity_min
* rainfall_min

This dataset enables rule-based disease risk inference within the knowledge graph.

```
```
