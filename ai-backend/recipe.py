import os
import ast
import pandas as pd
import google.generativeai as genai

# Gemini setup
if "GEMINI_API_KEY" in os.environ:
    try:
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        model = genai.GenerativeModel(model_name='gemini-1.5-flash')
        print("✅ Gemini initialized successfully")
    except Exception as e:
        print(f"❌ Gemini initialization failed: {str(e)}")
        model = None
else:
    print("❌ GEMINI_API_KEY not found in environment variables")
    model = None

# Constants
MYPLATE_GROUPS = ["vegetables", "fruits", "grains", "protein", "dairy"]
EMISSION_WEIGHTS = {
    "Agriculture": 0.50,
    "ILUC": 0.20,
    "Processing": 0.10,
    "Packaging": 0.14,
    "Transport": 0.03,
    "Retail": 0.03
}

category_mapping = {
    "vegetables and vegetable products": "vegetables",
    "fruits and fruit products": "fruits",
    "cereals and cereal products": "grains",
    "bread and bakery products": "grains",
    "meat and poultry": "protein",
    "seafood": "protein",
    "nuts and seeds": "protein",
    "legumes and legume products": "protein",
    "milk. dairy products and eggs": "dairy",
    "plant products and drinks": "dairy"
}


def load_emissions_data(file_path):
    df = pd.read_csv(file_path)
    df['Category'] = df['Category'].str.strip()
    df['Food product'] = df['Food product'].str.strip()
    return df.dropna(subset=['Food product'])


def get_clean_label(food_item):
    return food_item.split('.')[0].title()


def build_grouped_foods(df, category_mapping):
    grouped = {group: [] for group in MYPLATE_GROUPS}
    for _, row in df.iterrows():
        category = row['Category'].lower()
        mapped_group = category_mapping.get(category)
        if mapped_group in grouped:
            clean_name = get_clean_label(row['Food product'])
            grouped[mapped_group].append(clean_name)
    return grouped


def gemini_suggest_full_meal(cart_items, grouped_foods, df):
    if not model:
        return []

    # Analyze current cart's group coverage
    cart_groups = set()
    for item in cart_items:
        match = df[df['Food product'].str.lower() == item.lower()]
        if not match.empty:
            category = match.iloc[0]['Category'].lower()
            mapped_group = category_mapping.get(category)
            if mapped_group:
                cart_groups.add(mapped_group)

    missing_groups = [g for g in MYPLATE_GROUPS if g not in cart_groups]

    prompt = f"""Create a USDA MyPlate-compliant meal using mostly these items: {', '.join(cart_items)}.
{('Add 1-2 items from these missing categories: ' + ', '.join(missing_groups)) if missing_groups else ''}

Available ingredients by category:
{str(grouped_foods)}

Return ONLY a Python list of food names. Prioritize items that:
1. Complete missing food groups
2. Create balanced nutrition
3. Pair well with existing items"""

    try:
        response = model.generate_content(prompt)
        return ast.literal_eval(response.text.strip())
    except Exception as e:
        print(f"Gemini suggestion error: {str(e)}")
        # Fallback to dataset-based suggestions
        suggestions = []
        for group in missing_groups:
            if grouped_foods.get(group):
                suggestions.extend(grouped_foods[group][:1])
        return list(set(cart_items + suggestions[:2]))


def generate_meal_description(meal_items, group_assignments):
    if not model:
        return "Enable Gemini API for full recipe details"

    prompt = f"""Create a simple recipe using: {', '.join(meal_items)}
Format:
1. Ingredients: List exact food names
2. Instructions: 3-5 clear steps
3. MyPlate Compliance: 
   - Vegetables: {group_assignments.get('vegetables', 'None')}
   - Fruits: {group_assignments.get('fruits', 'None')}
   - Grains: {group_assignments.get('grains', 'None')}
   - Protein: {group_assignments.get('protein', 'None')}
   - Dairy: {group_assignments.get('dairy', 'None')}"""

    try:
        response = model.generate_content(prompt)
        return response.text.replace("**", "").strip()
    except:
        return "Meal description unavailable"


def suggest_meal_from_cart(cart_items, df, grouped_foods):
    # Get clean item names
    clean_cart = [get_clean_label(item) for item in cart_items]

    # Get full meal suggestion
    full_meal_items = gemini_suggest_full_meal(cart_items, grouped_foods, df)

    # Build breakdown
    breakdown = {}
    for item in full_meal_items:
        match = df[df['Food product'].str.lower() == item.lower()]
        if not match.empty:
            category = match.iloc[0]['Category'].lower()
            mapped_cat = category_mapping.get(category, "other")
            if mapped_cat in MYPLATE_GROUPS:
                breakdown[mapped_cat] = get_clean_label(item)

    return {
        "meal_items": [get_clean_label(i) for i in full_meal_items],
        "missing_groups": [g for g in MYPLATE_GROUPS if g not in breakdown],
        "breakdown": breakdown,
        "meal_description": generate_meal_description(full_meal_items,
                                                      breakdown)
    }
