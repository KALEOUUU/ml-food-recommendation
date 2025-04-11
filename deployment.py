from flask import Flask, request, jsonify, Response
import uuid
import datetime
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
import joblib
from collections import OrderedDict
import json

df = pd.read_csv('Dataset/processed_dataset.csv')
scaler = joblib.load('scaler.pkl')

if not isinstance(scaler, MinMaxScaler):
    raise ValueError("Loaded scaler is not a MinMaxScaler instance")

# normalize the dataset
numeric_cols = ['calories', 'fat', 'proteins', 'carbohydrate', 'Nutrient_Density']
df_scaled = pd.DataFrame(scaler.transform(df[numeric_cols]), columns=numeric_cols)
meal_type_names = {0: 'Breakfast', 1: 'Carbs', 2: 'Drink', 3: 'Lunch_Dinner', 4: 'Snack'}

app = Flask(__name__)

# endpoint to get food recommendations
@app.route("/api/v1/recommendations", methods=["POST"])
def recommend():
    try:
        data = request.get_json()
        user_id = data["userid"]
        calories = data["calories"]
        fat = data["fat"]
        proteins = data["proteins"]
        carbohydrate = data["carbohydrate"]

        # density calculation
        nutrient_density = (proteins + carbohydrate - fat) / (calories + 1e-6)
        input_features = np.array([[calories, fat, proteins, carbohydrate, nutrient_density]])
        input_scaled = scaler.transform(input_features)
        sim_scores = cosine_similarity(input_scaled, df_scaled).flatten()

        recommendations = []
        for meal_type, meal_category in meal_type_names.items():
            meal_indices = df[df['Meal Type'] == meal_type].index
            meal_similarities = sorted(
                [(idx, sim_scores[idx]) for idx in meal_indices], key=lambda x: x[1], reverse=True
            )[:5]

            for idx, _ in meal_similarities:
                food_item = {
                    "type": meal_category,
                    "food": {
                        "name": df.iloc[idx]["name"],
                        "proteins": df.iloc[idx]["proteins"],
                        "calories": df.iloc[idx]["calories"],
                        "fat": df.iloc[idx]["fat"],
                        "carbo": df.iloc[idx]["carbohydrate"],
                        "nutrient_density": df.iloc[idx]["Nutrient_Density"]
                    }
                }
                recommendations.append(food_item)

        response_data = OrderedDict([
            ("success", True),
            ("data", OrderedDict([
                ("userID", user_id),
                ("date", datetime.datetime.now().strftime("%d-%m-%Y")),
                ("status", "success"),
                ("data", recommendations)
            ]))
        ])
        return Response(json.dumps(response_data, indent=4, sort_keys=False), mimetype="application/json")

    except Exception as e:
        error_response = {"success": False, "error": str(e)}
        return Response(json.dumps(error_response, indent=4, sort_keys=False), mimetype="application/json")

# endpoint to get optimal meal plan
@app.route("/api/v1/dailyMeal", methods=["GET"])
def optimal_meal():
    try:
        daily_meal_plan = []
        for meal_type, meal_category in meal_type_names.items():
            top_meal = df[df['Meal Type'] == meal_type].nlargest(1, 'Nutrient_Density')
            if not top_meal.empty:
                meal = top_meal.iloc[0]
                daily_meal_plan.append({
                    "type": meal_category,
                    "food": {
                        "name": meal["name"],
                        "calories": meal["calories"],
                        "fat": meal["fat"],
                        "carbo": meal["carbohydrate"],
                        "nutrient_density": meal["Nutrient_Density"]
                    }
                })
        response_data = OrderedDict([
            ("success", True),
            ("data", OrderedDict([
                ("date", datetime.datetime.now().strftime("%d-%m-%Y")),
                ("status", "success"),
                ("data", daily_meal_plan)
            ]))
        ])
        return Response(json.dumps(response_data, indent=4, sort_keys=False), mimetype="application/json")

    except Exception as e:
        error_response = {"success": False, "error": str(e)}
        return Response(json.dumps(error_response, indent=4, sort_keys=False), mimetype="application/json")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=True)
