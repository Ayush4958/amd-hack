from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pandas as pd
from fastapi.responses import PlainTextResponse

app = FastAPI()

# Mount static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="src/web/templates")

# Load dataset once
df = pd.read_csv("data/cleaned/final_enriched_dataset.csv")
def interpret_question(question, df):

    q = question.lower()

    result = {}

    detected_state = None
    for state in df["state"].unique():
        if state.lower() in q:
            detected_state = state
            break

    detected_crop = None
    for crop in df["crop"].unique():
        if crop.lower() in q:
            detected_crop = crop
            break

    if detected_state and detected_crop:

        subset = df[
            (df["state"] == detected_state) &
            (df["crop"] == detected_crop)
        ]

        avg = subset.mean(numeric_only=True)

        result = {
            "state": detected_state,
            "crop": detected_crop,
            "agro_stress": float(avg["agro_stress_index"]),
            "climate": float(avg["climate_stress_norm"]),
            "disease": float(avg["disease_risk_norm"]),
            "nutrient": float(avg["nutrient_stress_norm"]),
            "confidence": float(avg.get("confidence_score", 0))
        }

    else:
        # fallback highest stress
        top = (
            df.groupby(["state","crop"])["agro_stress_index"]
            .mean()
            .sort_values(ascending=False)
            .head(1)
        )

        state, crop = top.index[0]

        result = {
            "state": state,
            "crop": crop,
            "agro_stress": float(top.iloc[0]),
            "climate": 0,
            "disease": 0,
            "nutrient": 0,
            "confidence": 0
        }

    return result



@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home.html", {
        "request": request,
        "answer": None
    })


@app.post("/", response_class=HTMLResponse)
def ask(request: Request,
        question: str = Form(...),
        mode: str = Form(...)):

    structured = interpret_question(question, df)

    # deterministic formatting (no LLM yet)

    if mode == "farmer":
        answer = (
            f"{structured.get('crop', 'Crop')} in "
            f"{structured.get('state', 'Selected State')} "
            f"is experiencing stress level "
            f"{round(structured.get('agro_stress', 0), 2)}.\n\n"
            f"Recommended focus: Monitor irrigation and nutrient balance.\n"
            f"Confidence level: {round(structured.get('confidence', 0), 2)}"
        )

    else:  # research mode
        answer = (
            f"State: {structured.get('state')}\n"
            f"Crop: {structured.get('crop')}\n"
            f"Agro Stress Index: {round(structured.get('agro_stress', 0), 3)}\n"
            f"Climate Stress: {round(structured.get('climate', 0), 3)}\n"
            f"Disease Risk: {round(structured.get('disease', 0), 3)}\n"
            f"Nutrient Stress: {round(structured.get('nutrient', 0), 3)}\n"
            f"Confidence Score: {round(structured.get('confidence', 0), 3)}"
        )

    return templates.TemplateResponse("home.html", {
        "request": request,
        "answer": answer
    })


@app.post("/ask", response_class=PlainTextResponse)
def ask_api(question: str = Form(...), mode: str = Form("farmer")):
    structured = interpret_question(question, df)

    if mode == "farmer":
        return (
            f"{structured.get('crop', 'Crop')} in "
            f"{structured.get('state', 'Selected State')} "
            f"is experiencing stress level {round(structured.get('agro_stress', 0), 2)}.\n\n"
            f"Recommended focus: Monitor irrigation and nutrient balance.\n"
            f"Confidence level: {round(structured.get('confidence', 0), 2)}"
        )

    return (
        f"State: {structured.get('state')}\n"
        f"Crop: {structured.get('crop')}\n"
        f"Agro Stress Index: {round(structured.get('agro_stress', 0), 3)}\n"
        f"Climate Stress: {round(structured.get('climate', 0), 3)}\n"
        f"Disease Risk: {round(structured.get('disease', 0), 3)}\n"
        f"Nutrient Stress: {round(structured.get('nutrient', 0), 3)}\n"
        f"Confidence Score: {round(structured.get('confidence', 0), 3)}"
    )




