import os
import time
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import google.generativeai as genai

# Returns: 'label', 'name', 'eco_score', 'rationale', 'components', 'total_emissions', 'image_link'


# Constants
EMISSION_WEIGHTS = {
    "Agriculture": 0.50,
    "ILUC": 0.20,
    "Processing": 0.10,
    "Packaging": 0.14,
    "Transport": 0.03,
    "Retail": 0.03
}
REQUIRED_COLUMNS = ['Food product', 'kg CO2e/ pr. kg', 'Image Link'] + list(EMISSION_WEIGHTS.keys())

# Gemini setup
if "GEMINI_API_KEY" in os.environ:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None


def load_emissions_data(file_path: str) -> pd.DataFrame:
    """Load and preprocess emissions dataset."""
    try:
        df = pd.read_excel(file_path)

        # Verify all required columns are present
        missing_cols = set(REQUIRED_COLUMNS) - set(df.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        # Drop rows with missing emission values
        df = df.dropna(subset=['kg CO2e/ pr. kg']).reset_index(drop=True)

        # Compute eco score using weighted emissions
        df['eco_score_raw'] = df.apply(
            lambda row: sum(row[comp] * EMISSION_WEIGHTS[comp] for comp in EMISSION_WEIGHTS),
            axis=1
        )

        # Normalize eco scores between 0 and 1
        scaler = MinMaxScaler()
        df['eco_score_normalized'] = scaler.fit_transform(df[['eco_score_raw']])
        df['eco_score_normalized'] = df['eco_score_normalized'].clip(0, 1)

        return df

    except Exception as e:
        raise SystemError(f"Data loading failed: {str(e)}")


def get_sustainability_score(food_item: str, df: pd.DataFrame) -> dict:
    """Get the sustainability score and rationale for a food item."""
    clean_item = food_item.strip().lower()
    matches = df[df['Food product'].str.lower().str.contains(clean_item, regex=False)]

    if matches.empty:
        return {"error": "Item not found", "image_link": None}

    row = matches.iloc[0]
    raw_score = row['eco_score_raw']
    label = _get_sustainability_category(row['eco_score_normalized'])

    return {
        "name": get_clean_label(row['Food product']),
        "label": label,
        "eco_score": round(float(raw_score) * 10, 1),
        "rationale": _generate_rationale(row, label),
        "components": row[list(EMISSION_WEIGHTS)].to_dict(),
        "total_emissions": float(row['kg CO2e/ pr. kg']),
        "image_link": row['Image Link']
    }


def get_clean_label(label: str) -> str:
    """Simplify messy product names for UI display."""
    if not model or not os.environ.get("GEMINI_API_KEY"):
        return label.strip()

    prompt = f"""
You are an expert in formatting product names cleanly for a grocery app UI.

Simplify and clean this food product name, making it natural, human-readable, and professional:
"{label}"

Rules:
- Fix word order if needed
- Capitalize properly
- Group details like fat % in parentheses
- Remove strange separators (periods, dashes)
- Keep meaning accurate, clean, short

Return only the cleaned name without extra explanation.
"""

    try:
        response = model.generate_content(prompt)
        time.sleep(1)
        return response.text.strip().replace('"', '')  # Remove quotes if present
    except Exception as e:
        print(f"Gemini clean label error: {str(e)}")
        return label.strip()


def _get_sustainability_category(score: float) -> str:
    """Categorize sustainability based on normalized score."""
    if score <= 0.33:
        return "High Sustainability"
    elif score <= 0.66:
        return "Medium Sustainability"
    else:
        return "Low Sustainability"


def _generate_rationale(row: pd.Series, label: str) -> str:
    """Generate a user-friendly sustainability rationale."""
    if not model or not os.environ.get("GEMINI_API_KEY"):
        return "Sustainability analysis unavailable: Missing Gemini API key"

    components_str = "\n".join(f"- {comp}: {row[comp]:.2f}" for comp in EMISSION_WEIGHTS)

    prompt = f"""
You are a sustainability analysis assistant. A user is asking for a sustainability evaluation of a grocery item based on carbon emissions.

- Sustainability Label: {label}
- Total Emissions: {row['kg CO2e/ pr. kg']:.2f}
- Breakdown:
{components_str}

Explain the eco-score in a friendly, user-centric way, not technical. Include:

- About this Eco-Score:
- Recommendation: (Explain decision. No yes/no answers.)

Be enthusiastic but concise. No greetings.
"""

    try:
        response = model.generate_content(prompt)
        time.sleep(1)
        return response.text.replace("**", "").strip()
    except Exception as e:
        print(f"Gemini API Error: {str(e)}")
        return "Sustainability analysis unavailable: API error occurred"

