import streamlit as st
import requests
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="FIT AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #34495e;
        margin-bottom: 1rem;
    }
    .card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .food-card {
        background-color: white;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    .metric-container {
        display: flex;
        justify-content: space-between;
        flex-wrap: wrap;
    }
    .footer {
        text-align: center;
        margin-top: 40px;
        color: #7f8c8d;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# App header
st.markdown("<h1 class='main-header'>FIT AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Get personalized food recommendations based on your nutritional preferences</p>", unsafe_allow_html=True)

# API endpoints
API_URL = "http://127.0.0.1:4000"  # Change this to your actual API endpoint when deployed
RECOMMENDATIONS_ENDPOINT = f"{API_URL}/api/v1/recommendations"
DAILY_MEAL_ENDPOINT = f"{API_URL}/api/v1/dailyMeal"

# Sidebar
st.sidebar.markdown("<h2 style='text-align: center;'>Nutrient Preferences</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<p>Adjust the sliders to set your nutritional preferences:</p>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    calories = st.slider("Calories (kcal)", 0, 1000, 300)
    fat = st.slider("Fat (g)", 0, 100, 20)
    proteins = st.slider("Proteins (g)", 0, 100, 30)
    carbohydrate = st.slider("Carbohydrates (g)", 0, 200, 50)
    
    # Calculate nutrient density for display
    if calories > 0:
        nutrient_density = (proteins + carbohydrate - fat) / calories
    else:
        nutrient_density = 0
    
    st.metric("Calculated Nutrient Density", f"{nutrient_density:.2f}")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Get Recommendations</h3>", unsafe_allow_html=True)
    get_recommendations = st.button("Get Personalized Recommendations", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Daily Optimal Meal</h3>", unsafe_allow_html=True)
    get_daily_meal = st.button("Get Optimal Daily Meal", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Main content area
tab1, tab2 = st.tabs(["Recommendations", "Nutrition Analysis"])

with tab1:
    if get_recommendations:
        try:
            # Show spinner while making API request
            with st.spinner("Getting personalized recommendations..."):
                # Prepare request payload
                payload = {
                    "calories": calories,
                    "fat": fat,
                    "proteins": proteins,
                    "carbohydrate": carbohydrate
                }
                
                # For local testing before API is ready
                try:
                    response = requests.post(RECOMMENDATIONS_ENDPOINT, json=payload)
                    if response.status_code == 200:
                        recommendations = response.json()["data"]["data"]
                    else:
                        st.error(f"API Error: {response.status_code}")
                        recommendations = []
                except requests.exceptions.RequestException:
                    # Fallback mock data for development/testing
                    st.warning("⚠️ Using mock data - API connection failed")
                    
                    # Mock data structure matching the API response
                    recommendations = [
                        {
                            "type": "Breakfast",
                            "food": {
                                "name": "Oatmeal with Berries",
                                "calories": 250,
                                "fat": 5,
                                "carbo": 40,
                                "nutrient_density": 1.4
                            }
                        },
                        {
                            "type": "Breakfast",
                            "food": {
                                "name": "Greek Yogurt with Honey",
                                "calories": 180,
                                "fat": 3,
                                "carbo": 25,
                                "nutrient_density": 1.2
                            }
                        },
                        # Add mock data for other meal types...
                        {
                            "type": "Lunch/Dinner",
                            "food": {
                                "name": "Grilled Chicken Salad",
                                "calories": 350,
                                "fat": 12,
                                "carbo": 20,
                                "nutrient_density": 0.9
                            }
                        },
                        {
                            "type": "Lunch/Dinner",
                            "food": {
                                "name": "Salmon with Vegetables",
                                "calories": 420,
                                "fat": 18,
                                "carbo": 15,
                                "nutrient_density": 0.8
                            }
                        },
                        {
                            "type": "Snack",
                            "food": {
                                "name": "Mixed Nuts",
                                "calories": 170,
                                "fat": 14,
                                "carbo": 6,
                                "nutrient_density": 0.5
                            }
                        },
                        {
                            "type": "Snack",
                            "food": {
                                "name": "Apple with Peanut Butter",
                                "calories": 200,
                                "fat": 8,
                                "carbo": 25,
                                "nutrient_density": 0.7
                            }
                        },
                        {
                            "type": "Drink",
                            "food": {
                                "name": "Green Smoothie",
                                "calories": 150,
                                "fat": 2,
                                "carbo": 30,
                                "nutrient_density": 1.1
                            }
                        },
                        {
                            "type": "Drink",
                            "food": {
                                "name": "Protein Shake",
                                "calories": 220,
                                "fat": 5,
                                "carbo": 15,
                                "nutrient_density": 1.0
                            }
                        },
                        {
                            "type": "Carbs",
                            "food": {
                                "name": "Brown Rice",
                                "calories": 180,
                                "fat": 1,
                                "carbo": 38,
                                "nutrient_density": 1.3
                            }
                        },
                        {
                            "type": "Carbs",
                            "food": {
                                "name": "Sweet Potato",
                                "calories": 150,
                                "fat": 0,
                                "carbo": 35,
                                "nutrient_density": 1.4
                            }
                        }
                    ]
            
            # Group by meal type
            meal_types = {}
            for item in recommendations:
                meal_type = item["type"]
                if meal_type not in meal_types:
                    meal_types[meal_type] = []
                meal_types[meal_type].append(item["food"])
            
            # Display recommendations
            st.markdown("<h2 class='sub-header'>Your Personalized Food Recommendations</h2>", unsafe_allow_html=True)
            
            # Create columns for each meal type
            cols = st.columns(len(meal_types))
            
            for i, (meal_type, foods) in enumerate(meal_types.items()):
                with cols[i]:
                    st.markdown(f"<h3 style='text-align: center;'>{meal_type}</h3>", unsafe_allow_html=True)
                    
                    for food in foods:
                        st.markdown("<div class='food-card'>", unsafe_allow_html=True)
                        st.markdown(f"<h4>{food['name']}</h4>", unsafe_allow_html=True)
                        st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
                        
                        # Create nutrition info
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"Calories: **{food['calories']} kcal**")
                            st.markdown(f"Fat: **{food['fat']} g**")
                        with col2:
                            st.markdown(f"Carbs: **{food['carbo']} g**")
                            st.markdown(f"Nutrient Density: **{food['nutrient_density']:.2f}**")
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
        
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    
    if get_daily_meal:
        try:
            with st.spinner("Getting optimal daily meal plan..."):
                # Try to fetch from API
                try:
                    response = requests.get(DAILY_MEAL_ENDPOINT)
                    if response.status_code == 200:
                        daily_meals = response.json()["data"]["data"]
                    else:
                        st.error(f"API Error: {response.status_code}")
                        daily_meals = []
                except requests.exceptions.RequestException:
                    # Fallback mock data
                    st.warning("⚠️ Using mock data - API connection failed")
                    daily_meals = [
                        {
                            "type": "Breakfast",
                            "food": {
                                "name": "Avocado Toast with Egg",
                                "calories": 320,
                                "fat": 18,
                                "carbo": 28,
                                "nutrient_density": 1.7
                            }
                        },
                        {
                            "type": "Lunch/Dinner",
                            "food": {
                                "name": "Quinoa Bowl with Vegetables",
                                "calories": 450,
                                "fat": 15,
                                "carbo": 60,
                                "nutrient_density": 1.9
                            }
                        },
                        {
                            "type": "Snack",
                            "food": {
                                "name": "Greek Yogurt with Berries",
                                "calories": 180,
                                "fat": 5,
                                "carbo": 20,
                                "nutrient_density": 1.5
                            }
                        },
                        {
                            "type": "Drink",
                            "food": {
                                "name": "Green Smoothie with Protein",
                                "calories": 220,
                                "fat": 3,
                                "carbo": 25,
                                "nutrient_density": 1.8
                            }
                        },
                        {
                            "type": "Carbs",
                            "food": {
                                "name": "Sweet Potato",
                                "calories": 180,
                                "fat": 0,
                                "carbo": 42,
                                "nutrient_density": 2.1
                            }
                        }
                    ]
            
            st.markdown("<h2 class='sub-header'>Optimal Daily Meal Plan</h2>", unsafe_allow_html=True)
            st.markdown("<p>These are the top foods with highest nutrient density for each meal type:</p>", unsafe_allow_html=True)
            
            # Calculate total nutrition values
            total_calories = sum(meal["food"]["calories"] for meal in daily_meals)
            total_fat = sum(meal["food"]["fat"] for meal in daily_meals)
            total_carbs = sum(meal["food"]["carbo"] for meal in daily_meals)
            avg_density = sum(meal["food"]["nutrient_density"] for meal in daily_meals) / len(daily_meals)
            
            # Display summary metrics
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<h3 style='text-align: center;'>Daily Nutrition Summary</h3>", unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Calories", f"{total_calories} kcal")
            col2.metric("Total Fat", f"{total_fat} g")
            col3.metric("Total Carbs", f"{total_carbs} g")
            col4.metric("Avg Nutrient Density", f"{avg_density:.2f}")
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Display meal plan
            for meal in daily_meals:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    st.markdown(f"<h3>{meal['type']}</h3>", unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"<h4>{meal['food']['name']}</h4>", unsafe_allow_html=True)
                    st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
                    st.markdown(f"Calories: **{meal['food']['calories']} kcal** | " +
                              f"Fat: **{meal['food']['fat']} g** | " +
                              f"Carbs: **{meal['food']['carbo']} g** | " +
                              f"Nutrient Density: **{meal['food']['nutrient_density']:.2f}**")
                    st.markdown("</div>", unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

with tab2:
    if get_recommendations or get_daily_meal:
        st.markdown("<h2 class='sub-header'>Nutrition Analysis</h2>", unsafe_allow_html=True)
        
        # Get data to visualize
        data = []
        if get_recommendations and 'recommendations' in locals():
            for item in recommendations:
                food = item["food"]
                data.append({
                    "Name": food["name"],
                    "Type": item["type"],
                    "Calories": food["calories"],
                    "Fat": food["fat"],
                    "Carbohydrates": food["carbo"],
                    "Nutrient Density": food["nutrient_density"]
                })
        elif get_daily_meal and 'daily_meals' in locals():
            for item in daily_meals:
                food = item["food"]
                data.append({
                    "Name": food["name"],
                    "Type": item["type"],
                    "Calories": food["calories"],
                    "Fat": food["fat"],
                    "Carbohydrates": food["carbo"],
                    "Nutrient Density": food["nutrient_density"]
                })
        
        if data:
            df = pd.DataFrame(data)
            
            # Create visualizations
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("<h3 style='text-align: center;'>Nutrient Composition</h3>", unsafe_allow_html=True)
                fig = px.bar(df, 
                        x="Name", 
                        y=["Calories", "Fat", "Carbohydrates"],
                        title="Nutrient Composition by Food Item",
                        barmode="group")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("<h3 style='text-align: center;'>Nutrient Density Comparison</h3>", unsafe_allow_html=True)
                fig = px.bar(df, 
                        x="Name", 
                        y="Nutrient Density",
                        color="Type",
                        title="Nutrient Density by Food Item")
                st.plotly_chart(fig, use_container_width=True)
            
            # Radar chart for each food item
            st.markdown("<h3 style='text-align: center;'>Nutrient Profile Radar Charts</h3>", unsafe_allow_html=True)
            
            # Create columns based on the number of food items (up to 3 per row)
            num_items = len(df)
            items_per_row = 3
            num_rows = (num_items + items_per_row - 1) // items_per_row
            
            for row in range(num_rows):
                cols = st.columns(items_per_row)
                for i in range(items_per_row):
                    idx = row * items_per_row + i
                    if idx < num_items:
                        food = df.iloc[idx]
                        with cols[i]:
                            # Normalize values for radar chart
                            calories_norm = food["Calories"] / df["Calories"].max()
                            fat_norm = food["Fat"] / df["Fat"].max()
                            carbs_norm = food["Carbohydrates"] / df["Carbohydrates"].max()
                            density_norm = food["Nutrient Density"] / df["Nutrient Density"].max()
                            
                            # Create radar chart
                            fig = go.Figure()
                            
                            fig.add_trace(go.Scatterpolar(
                                r=[calories_norm, fat_norm, carbs_norm, density_norm, calories_norm],
                                theta=['Calories', 'Fat', 'Carbohydrates', 'Nutrient Density', 'Calories'],
                                fill='toself',
                                name=food["Name"]
                            ))
                            
                            fig.update_layout(
                                polar=dict(
                                    radialaxis=dict(
                                        visible=True,
                                        range=[0, 1]
                                    )),
                                showlegend=False,
                                title=food["Name"]
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Adjust your nutrition preferences and click 'Get Personalized Recommendations' or 'Get Optimal Daily Meal' to see the analysis.")

# Footer
st.markdown("<div class='footer'>Food Nutrition Recommendation System © 2025</div>", unsafe_allow_html=True)