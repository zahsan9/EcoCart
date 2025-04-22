import pandas as pd
import google.generativeai as genai
from sklearn.preprocessing import MinMaxScaler
import os
from tqdm import tqdm

# my key - AIzaSyCkIMkcY6tfssOX-f8qowLvN8jI7GVF3Lk
gemini_api_key = os.environ["GEMINI_API_KEY"]
genai.configure(api_key=gemini_api_key)

df = pd.read_csv("foodemissions.xlsx - ES.csv")
df.dropna(subset=['Total kg CO2-eq/kg'], inplace=True)

emission_components = [
    "Agriculture", "iLUC", "Food processing", "Packaging", "Transport", "Retail"
]

scaler = MinMaxScaler()
df[emission_components] = scaler.fit_transform(df[emission_components])

def build_prompt(row):
    description = "\n".join([f"{comp}: {row[comp]:.2f}" for comp in emission_components])
    return f"""Given the following environmental impact of a food product, classify its sustainability as Low, Medium, or High. Consider lower values as more sustainable.

Environmental impact (normalized values):
{description}

Sustainability:"""

def get_gemini_label(prompt):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')  
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("Error:", e)
        return "Unknown"

print("Querying Gemini for sustainability classifications...")
df["sustainability_class_gemini"] = [
    get_gemini_label(build_prompt(row)) for _, row in tqdm(df.iterrows(), total=len(df))
]

df.to_csv("gemini_sustainability_scores.csv", index=False)
print("Saved Gemini classification results to CSV.")
