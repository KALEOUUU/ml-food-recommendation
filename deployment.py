from flask import Flask, request, jsonify
import uuid
import datetime
import pickle
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
from sklearn.metrics.pairwise import cosine_similarity

class FoodRecommendationSystem:
    def __init__(self, dataset):
        self.dataset = dataset
        self.scaler = MinMaxScaler()

        # OneHotEncode categorical columns
        self.encoder = OneHotEncoder(sparse_output=False)
        encoded_cats = self.encoder.fit_transform(dataset[['Carb_Level', 'Protein_Level', 'Diet_Category']])
        encoded_df = pd.DataFrame(encoded_cats, columns=self.encoder.get_feature_names_out())

        # Normalize numerical features
        normalized_features = self.scaler.fit_transform(self.dataset[['calories', 'fat', 'proteins', 'carbohydrate', 'Nutrient_Density']])
        normalized_df = pd.DataFrame(normalized_features, columns=['calories', 'fat', 'proteins', 'carbohydrate', 'Nutrient_Density'])

        # Combine numerical and categorical data
        self.dataset = pd.concat([normalized_df, encoded_df, self.dataset[['name', 'Meal Type']]], axis=1)

    def get_recommendations(self, user_profile, top_n=5):
        user_profile_df = pd.DataFrame([user_profile], columns=['calories', 'fat', 'proteins', 'carbohydrate', 'Nutrient_Density', 'Carb_Level', 'Protein_Level', 'Diet_Category'])
        
        # Convert numerical columns to float
        numerical_cols = ['calories', 'fat', 'proteins', 'carbohydrate', 'Nutrient_Density']
        user_profile_df[numerical_cols] = user_profile_df[numerical_cols].astype(float)
        
        # Convert categorical columns to string
        categorical_cols = ['Carb_Level', 'Protein_Level', 'Diet_Category']
        user_profile_df[categorical_cols] = user_profile_df[categorical_cols].astype(str)

        user_profile_scaled = self.scaler.transform(user_profile_df[numerical_cols])
        user_cats = self.encoder.transform(user_profile_df[categorical_cols])
        user_profile_combined = np.concatenate((user_profile_scaled[0], user_cats[0]))

        recommendations_by_category = {}
        meal_type_names = {0: 'Breakfast', 1: 'Carbs', 2: 'Drink', 3: 'Lunch/Dinner', 4: 'Snack'}
        features = self.dataset.columns[:-2]

        for meal_type, meal_name in meal_type_names.items():
            filtered_dataset = self.dataset[self.dataset['Meal Type'] == meal_type]
            similarities = cosine_similarity([user_profile_combined], filtered_dataset[features])
            similarity_scores = list(enumerate(similarities[0]))

            similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
            top_items = similarity_scores[:top_n]

            recommendations = filtered_dataset.iloc[[i[0] for i in top_items]]
            recommendations_by_category[meal_name] = recommendations

        return recommendations_by_category

with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

app = Flask(__name__)

@app.route('/api/v1/recommendations', methods=['POST'])
def recommendations():
    try:
        user_profile = request.json
        recommendations = model.get_recommendations(user_profile)
        
        result = []
        for meal_type, df in recommendations.items():
            for _, row in df.iterrows():
                result.append({
                    "type": meal_type,
                    "food": {
                        "name": row['name'],
                        "calories": row['calories'],
                        "fat": row['fat'],
                        "proteins": row['proteins'],
                        "carbohydrate": row['carbohydrate'],
                        "Nutrient_Density": row['Nutrient_Density'],
                    }
                })
        response = {
            "UserID": str(uuid.uuid4()),
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "status": "success",
            "data": result
        }
        
        return jsonify(response), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=True)
        
    
    
 