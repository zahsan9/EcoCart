import pandas as pd
import google.generativeai as genai
from sklearn.preprocessing import MinMaxScaler
from functools import lru_cache
import os
import time

# ** need to use own key **
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

try:
    df = pd.read_excel("foodemissions.xlsx", sheet_name="ES")
    df = df[~df['Total kg CO2-eq/kg'].isna()].reset_index(drop=True)
except Exception as e:
    raise SystemError(f"Data loading failed: {str(e)}")

# emission components and weights
EMISSION_WEIGHTS = {
    "Agriculture": 0.35,
    "iLUC": 0.25,
    "Food processing": 0.15,
    "Packaging": 0.10,
    "Transport": 0.10,
    "Retail": 0.05
}

# normalize emission components
scaler = MinMaxScaler()
df[list(EMISSION_WEIGHTS)] = scaler.fit_transform(df[list(EMISSION_WEIGHTS)])


@lru_cache(maxsize=500)
def get_sustainability_score(food_item: str) -> dict:
    """Returns structured data for UI integration"""
    clean_item = food_item.strip().lower()
    matches = df[df['Food product'].str.lower().str.contains(clean_item)]

    if matches.empty:
        return {"error": "Item not found"}

    row = matches.iloc[0]
    weighted_score = sum(row[comp] * weight
                         for comp, weight in EMISSION_WEIGHTS.items())

    # classification
    if weighted_score < 0.3:
        category = "High"
    elif weighted_score < 0.7:
        category = "Medium"
    else:
        category = "Low"

    rationale = generate_rationale(row, category)

    return {
        "score": category,
        "rationale": rationale,
        "components": row[list(EMISSION_WEIGHTS)].to_dict(),
        "total_emissions": row['Total kg CO2-eq/kg']
    }


def generate_rationale(row, category) -> str:
    """Generates AI-powered explanation with guardrails"""
    prompt = f"""Analyze this food product's sustainability using actual emission data:
    Total CO2-eq/kg: {row['Total kg CO2-eq/kg']:.1f}
    {", ".join([f"{k}: {v:.2f}" for k,v in row[EMISSION_WEIGHTS].items()])}

    Explain why it's {category} sustainability in 3 bullet points using real-world comparisons."""

    try:
        response = model.generate_content(prompt)
        time.sleep(2)
        return response.text.replace("**", "")
    except genai.types.BlockedPromptException:
        return "Sustainability analysis unavailable"
