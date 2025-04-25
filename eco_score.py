import os
import time
import pandas as pd
import google.generativeai as genai
from functools import lru_cache

# Constants
EMISSION_WEIGHTS = {
    "Agriculture": 0.35,
    "ILUC": 0.25,
    "Processing": 0.15,
    "Packaging": 0.10,
    "Transport": 0.10,
    "Retail": 0.05
}
REQUIRED_COLUMNS = ['Food product', 'kg CO2e/ pr. kg', 'Image Link'] + list(EMISSION_WEIGHTS.keys())

# Gemini setup
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

def load_emissions_data(file_path: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(file_path, encoding='latin1')

        missing_cols = set(REQUIRED_COLUMNS) - set(df.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        df = df[~df['kg CO2e/ pr. kg'].isna()].reset_index(drop=True)

        if 'Image Link' not in df.columns:
            df['Image Link'] = None
            print("Warning: Image Link column not found - using null values")

        return df

    except Exception as e:
        raise SystemError(f"Data loading failed: {str(e)}")

# Load full dataset
df = load_emissions_data("food_emissions.csv")

@lru_cache(maxsize=500)
def get_sustainability_score(food_item: str) -> dict:
    clean_item = food_item.strip().lower()
    matches = df[df['Food product'].str.lower().str.contains(clean_item)]

    if matches.empty:
        return {"error": "Item not found", "image_link": None}

    row = matches.iloc[0]
    eco_score = sum(row[comp] * weight for comp, weight in EMISSION_WEIGHTS.items())

    return {
        "label": _get_sustainability_category(eco_score),
        "eco_score": round(float(eco_score), 4),
        "rationale": _generate_rationale(row),
        "components": row[list(EMISSION_WEIGHTS)].to_dict(),
        "total_emissions": float(row['kg CO2e/ pr. kg']),
        "image_link": row['Image Link']
    }

def _get_sustainability_category(score: float) -> str:
    if score <= 0.5:
        return "High Sustainability"
    elif score <= 1.5:
        return "Medium Sustainability"
    else:
        return "Low Sustainability"

def _generate_rationale(row: pd.Series) -> str:
    if not os.environ.get("GEMINI_API_KEY"):
        return "Sustainability analysis unavailable: Missing Gemini API key"

    components_str = "\n".join(f"- {comp}: {row[comp]:.2f}" for comp in EMISSION_WEIGHTS)

    prompt = f"""
    You are a sustainability analysis assistant. A user is asking for a sustainability evaluation of a grocery item based on raw carbon emissions from various sources. Here are the unnormalized component emissions in kg CO2e per kg of product.

    Total Emissions: {row['kg CO2e/ pr. kg']:.2f}
    Breakdown:
    {components_str}

    Explain the environmental impact in a user friendly way as well as whether the user is suggested to purchase the product or not. Include an "Overall Summary: ", "Environmental Impact: ", and "Recommendation: " in your response. Only include some percentages relevent to your analysis, don't be overly verbose or technical. Be enthusiastic and friendly. Don't greet user, simply provide the sections requested.
    """

    try:
        response = model.generate_content(prompt)
        time.sleep(1)
        return response.text.replace("**", "").strip()
    except Exception as e:
        print(f"Gemini API Error: {str(e)}")
        return "Sustainability analysis unavailable: API error occurred"

def main():
    from pprint import pprint
    food_item = "Cocoa. powder"
    print(f"\n🔍 Checking sustainability score for: {food_item}")
    result = get_sustainability_score(food_item)
    pprint(result)

if __name__ == "__main__":
    main()
