import pandas as pd
import google.generativeai as genai
from sklearn.preprocessing import MinMaxScaler
from functools import lru_cache
import os
import time

# ** Use your actual Gemini API key **
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# Load and preprocess data
try:
    df = pd.read_excel("foodemissions.xlsx", sheet_name="ES")
    df = df[~df['Total kg CO2-eq/kg'].isna()].reset_index(drop=True)
except Exception as e:
    raise SystemError(f"Data loading failed: {str(e)}")

# Emission component weights
EMISSION_WEIGHTS = {
    "Agriculture": 0.35,
    "iLUC": 0.25,
    "Food processing": 0.15,
    "Packaging": 0.10,
    "Transport": 0.10,
    "Retail": 0.05
}

# Normalize components using MinMaxScaler
scaler = MinMaxScaler()
df[list(EMISSION_WEIGHTS)] = scaler.fit_transform(df[list(EMISSION_WEIGHTS)])


@lru_cache(maxsize=500)
def get_sustainability_score(food_item: str) -> dict:
    """Returns structured sustainability score data for a given food item."""
    clean_item = food_item.strip().lower()
    matches = df[df['Food product'].str.lower() == clean_item]

    if matches.empty:
        matches = df[df['Food product'].str.lower().str.contains(clean_item)]

    if matches.empty:
        return {"error": "Item not found"}

    row = matches.iloc[0]
    weighted_score = sum(row[comp] * weight for comp, weight in EMISSION_WEIGHTS.items())

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
    """Generates an AI-powered sustainability explanation."""
    emission_components = ",\n".join([
        f'"{comp}": {row[comp]:.2f}' for comp in EMISSION_WEIGHTS
    ])

    prompt = f"""
You are a sustainability analysis assistant. Given data about a grocery food item’s carbon emissions from various sources, calculate its sustainability score and assign a label ("High", "Medium", or "Low") based on this scoring formula:

Use Min-Max normalization for each emission component (Agriculture, iLUC, Food processing, Packaging, Transport, Retail) across all products. Normalize each component to a value between 0 and 1.

Then calculate the sustainability score using this weighted sum:
S = (EAgriculture * 0.35) + (EiLUC * 0.25) + (EFoodprocessing * 0.15) + (EPackaging * 0.10) + (ETransport * 0.10) + (ERetail * 0.05)

Finally, assign a score label:
- "High" if S < 0.3
- "Medium" if 0.3 ≤ S < 0.7
- "Low" if S ≥ 0.7

Also, summarize your reasoning for the score in 2–3 bullet points, considering total emissions and individual component weights.

Here is the data:
Total CO2-eq/kg: {row['Total kg CO2-eq/kg']:.1f}
Components:
{emission_components}

Return your result in this format:
{{
  "score": "{category}",
  "rationale": "- <reason 1>\\n- <reason 2>\\n...",
  "components": {{
    "Agriculture": <normalized_value>,
    "iLUC": <normalized_value>,
    "Food processing": <normalized_value>,
    "Packaging": <normalized_value>,
    "Transport": <normalized_value>,
    "Retail": <normalized_value>
  }},
  "total_emissions": <raw_total_emissions>
}}
"""

    try:
        response = model.generate_content(prompt)
        time.sleep(2)  # Safety delay
        return response.text.replace("**", "")
    except genai.types.BlockedPromptException:
        return "Sustainability analysis unavailable"


# Optional: test example
# print(get_sustainability_score("beef (beef herd)"))
