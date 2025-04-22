import pandas as pd
import google.generativeai as genai
from sklearn.preprocessing import MinMaxScaler
import os
import time

gemini_api_key = os.environ["GEMINI_API_KEY"]
genai.configure(api_key=gemini_api_key)

df = pd.read_csv("foodemissions.xlsx - ES.csv")
df.dropna(subset=['Total kg CO2-eq/kg'], inplace=True)

emission_components = [
    "Agriculture", "iLUC", "Food processing", "Packaging", "Transport", "Retail"
]

scaler = MinMaxScaler()
df[emission_components] = scaler.fit_transform(df[emission_components])

sustainability_cache = {}

def get_sustainability_score(food_item: str) -> str:
    """Main function to be called by UI"""
    row = df[df['Food product'] == food_item]

    if row.empty:
        return "Food item not found"

    if food_item in sustainability_cache:
        return sustainability_cache[food_item]

    prompt = build_prompt(row.iloc[0])

    classification = get_gemini_label(prompt)

    sustainability_cache[food_item] = classification

    return classification

def build_prompt(row):
    """Helper function to create the prompt"""
    description = "\n".join([f"{comp}: {row[comp]:.2f}" for comp in emission_components])
    return f"""Given the following environmental impact of a food product, classify its sustainability as Low, Medium, or High. Consider lower values as more sustainable.

Environmental impact (normalized values):
{description}

Sustainability:"""

def get_gemini_label(prompt):
    """Helper function with rate limiting"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        time.sleep(4)  # delay between API calls
        return response.text.strip()
    except Exception as e:
        print(f"API Error: {str(e)}")
        return "Classification Error"
