import os
import time
import json
import google.generativeai as genai

# --- Setup Gemini ---
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

def build_meal_plan_prompt(cart_items: list, num_meals: int) -> str:
    ingredient_hint = ", ".join(cart_items)
    prompt = f"""
You are an experienced eco-conscious meal planner and recipe developer. Your job is to create a real-world meal plan using only the ingredients provided by the user from their shopping cart.

Use only the ingredients from this list: {ingredient_hint}.
Do not invent or assume any extra ingredients for the recipes themselves.
Each cart item should only be counted once within the plan; if a recipe needs more of an ingredient (e.g., 2 cups of broccoli), indicate it naturally inside the preparation steps without assuming the user has bought multiple units.

Attempt to create {num_meals} meals.

If there are not enough ingredients OR the available ingredients cannot form balanced, practical meals:
- Return a message saying that there are not enough items to create a meal plan.
- Provide specific, helpful suggestions for 2–3 additional ingredients that the user could add to their cart to enable the creation of balanced meals. Just display the ingredients without categorizing them.

If enough ingredients ARE available:
- Proceed to create the meal plan.
- Each meal must be based on real, recognized recipes that are simple, practical, healthy, and achievable by a home cook in about 30–40 minutes.
- For each meal:
    - Provide a Meal Name
    - List the Ingredients used (only from the cart)
    - Write a Preparation Method in 3–6 clear, logical steps based on real cooking techniques
    - Mention any necessary quantities inside the method naturally.

Provide the meal plan in a JSON format with fields:
{
  "meals": [
    {
      "meal_name": "...",
      "ingredients": ["...", "..."],
      "preparation_method": ["Step 1", "Step 2", "Step 3"]
    },
    (repeat for each meal)
  ]
}
If there is an alert, provide:
{
  "alert": "message",
  "suggestions": ["item1", "item2", "item3"]
}

Use a professional, clear, friendly, and helpful tone.
Focus on meals that are realistic, eco-friendly, healthy, and enjoyable to prepare.
"""
    return prompt

def meal_plan(cart_items: list, num_meals: int = 3) -> str:
    if not os.environ.get("GEMINI_API_KEY"):
        return json.dumps({"alert": "Meal plan unavailable: Missing Gemini API key"})

    if len(cart_items) < 2:
        return json.dumps({
            "alert": "Not enough ingredients to create a meal plan.",
            "suggestions": [
                "Tofu", "Chickpeas", "Lentils", "Rice", "Quinoa", "Whole Wheat Bread", "Spinach", "Broccoli", "Tomatoes"
            ]
        })

    prompt = build_meal_plan_prompt(cart_items, num_meals)

    try:
        response = model.generate_content(prompt)
        time.sleep(1)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini API Error (Meal Plan): {str(e)}")
        return json.dumps({"alert": "Meal plan unavailable: API error occurred"})

