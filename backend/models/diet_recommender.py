"""
Diet recommendation engine based on user profile and menopause predictions.
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class DietRecommender:
    """Diet recommendation engine for menopause management."""
    
    def __init__(self, usda_data_path: str = "../datasets/FoodData_Central_foundation_food_csv_2025-04-24"):
        self.usda_path = Path(usda_data_path)
        self.food_df = None
        self.nutrient_df = None
        self.food_nutrient_df = None
        self.nutrient_info = None
        self._load_usda_data()
        
    def _load_usda_data(self):
        """Load USDA FoodData Central data."""
        logger.info("Loading USDA FoodData Central...")
        
        # Load food data
        food_file = self.usda_path / "food.csv"
        if food_file.exists():
            self.food_df = pd.read_csv(food_file, low_memory=False)
            logger.info(f"Loaded {len(self.food_df)} foods")
        
        # Load nutrient data
        nutrient_file = self.usda_path / "nutrient.csv"
        if nutrient_file.exists():
            self.nutrient_info = pd.read_csv(nutrient_file, low_memory=False)
            logger.info(f"Loaded {len(self.nutrient_info)} nutrients")
        
        # Load food-nutrient relationships
        food_nutrient_file = self.usda_path / "food_nutrient.csv"
        if food_nutrient_file.exists():
            self.food_nutrient_df = pd.read_csv(food_nutrient_file, low_memory=False)
            logger.info(f"Loaded {len(self.food_nutrient_df)} food-nutrient relationships")
    
    def _get_nutrient_id(self, nutrient_name: str) -> Optional[int]:
        """Get nutrient ID by name."""
        if self.nutrient_info is None:
            return None
        
        # Correct nutrient IDs from USDA FoodData Central
        nutrient_map = {
            'calcium': 1087,  # Calcium, Ca
            'vitamin_d': 1114,  # Vitamin D (D2 + D3)
            'magnesium': 1089,  # Magnesium, Mg
            'vitamin_c': 1162,  # Vitamin C, total ascorbic acid
            'fiber': 1079,  # Fiber, total dietary
            'omega_3': 10063,  # Fatty acids, total n-3
            'protein': 1003,  # Protein
            'vitamin_e': 1109,  # Vitamin E (alpha-tocopherol)
            'vitamin_b': 1175,  # Vitamin B-6
            'tryptophan': 1210,  # Tryptophan
        }
        
        nutrient_name_lower = nutrient_name.lower()
        if nutrient_name_lower in nutrient_map:
            return nutrient_map[nutrient_name_lower]
        
        # Try to find by name in nutrient info
        if self.nutrient_info is not None:
            matches = self.nutrient_info[
                self.nutrient_info['name'].str.contains(nutrient_name, case=False, na=False)
            ]
            if len(matches) > 0:
                return int(matches.iloc[0]['id'])
        
        # Special handling for iron
        if nutrient_name_lower == 'iron':
            iron_match = self.nutrient_info[
                self.nutrient_info['name'].str.contains('iron', case=False, na=False)
            ]
            if len(iron_match) > 0:
                return int(iron_match.iloc[0]['id'])
        
        return None
    
    def _get_foods_by_nutrient(self, nutrient_id: int, min_amount: float = 0) -> pd.DataFrame:
        """Get foods rich in a specific nutrient."""
        if self.food_nutrient_df is None or self.food_df is None:
            return pd.DataFrame()
        
        # Filter by nutrient
        nutrient_foods = self.food_nutrient_df[
            (self.food_nutrient_df['nutrient_id'] == nutrient_id) &
            (self.food_nutrient_df['amount'] >= min_amount)
        ]
        
        # Merge with food info
        if len(nutrient_foods) > 0:
            foods = nutrient_foods.merge(
                self.food_df[['fdc_id', 'description']],
                on='fdc_id',
                how='left'
            )
            # Remove rows with missing descriptions
            foods = foods.dropna(subset=['description'])
            return foods.sort_values('amount', ascending=False)
        
        return pd.DataFrame()
    
    def _get_fallback_foods(self, category: str) -> List[Dict]:
        """Get fallback food recommendations when nutrient lookup fails."""
        fallback_foods = {
            'hot_flashes': [
                {'food': 'Soy products (tofu, tempeh, edamame)', 'nutrient': 'phytoestrogens', 'reason': 'Natural phytoestrogens help balance hormones'},
                {'food': 'Flaxseeds', 'nutrient': 'phytoestrogens', 'reason': 'Rich in lignans, natural phytoestrogens'},
                {'food': 'Whole grains (oats, barley)', 'nutrient': 'fiber', 'reason': 'Help stabilize blood sugar and hormones'},
                {'food': 'Legumes (chickpeas, lentils)', 'nutrient': 'phytoestrogens', 'reason': 'Natural plant estrogens'},
            ],
            'sleep': [
                {'food': 'Almonds', 'nutrient': 'magnesium', 'reason': 'Rich in magnesium, promotes sleep'},
                {'food': 'Dairy products (milk, yogurt)', 'nutrient': 'calcium', 'reason': 'Calcium helps with sleep regulation'},
                {'food': 'Turkey', 'nutrient': 'tryptophan', 'reason': 'Contains tryptophan, promotes sleep'},
                {'food': 'Bananas', 'nutrient': 'magnesium', 'reason': 'Good source of magnesium and potassium'},
            ],
            'mood': [
                {'food': 'Fatty fish (salmon, mackerel)', 'nutrient': 'omega_3', 'reason': 'Omega-3 fatty acids support brain health'},
                {'food': 'Dark leafy greens (spinach, kale)', 'nutrient': 'folate', 'reason': 'Rich in B vitamins for mood support'},
                {'food': 'Nuts and seeds', 'nutrient': 'omega_3', 'reason': 'Healthy fats and nutrients for brain function'},
                {'food': 'Whole grains', 'nutrient': 'complex_carbs', 'reason': 'Stable energy and mood support'},
            ],
            'bone_health': [
                {'food': 'Dairy products (milk, cheese, yogurt)', 'nutrient': 'calcium', 'reason': 'Excellent source of calcium'},
                {'food': 'Leafy greens (kale, broccoli)', 'nutrient': 'calcium', 'reason': 'Good plant-based calcium source'},
                {'food': 'Fatty fish (salmon, sardines)', 'nutrient': 'vitamin_d', 'reason': 'Rich in vitamin D for calcium absorption'},
                {'food': 'Fortified foods', 'nutrient': 'vitamin_d', 'reason': 'Many foods are fortified with vitamin D'},
            ],
            'weight_management': [
                {'food': 'Vegetables (all types)', 'nutrient': 'fiber', 'reason': 'Low calorie, high fiber, filling'},
                {'food': 'Lean proteins (chicken, fish)', 'nutrient': 'protein', 'reason': 'High protein keeps you full longer'},
                {'food': 'Whole grains', 'nutrient': 'fiber', 'reason': 'High fiber promotes satiety'},
                {'food': 'Legumes', 'nutrient': 'fiber', 'reason': 'High fiber and protein, low calorie'},
            ],
        }
        return fallback_foods.get(category, [])
    
    def recommend_for_symptom(self, symptom: str, limit: int = 10) -> List[Dict]:
        """
        Recommend foods based on menopause symptom.
        
        Args:
            symptom: Symptom name (hot_flashes, sleep, mood, bone_health, etc.)
            limit: Maximum number of recommendations
            
        Returns:
            List of food recommendations with details
        """
        recommendations = []
        
        symptom_mapping = {
            'hot_flashes': {
                'nutrients': ['vitamin_e', 'calcium', 'magnesium'],
                'fallback': 'hot_flashes'
            },
            'sleep': {
                'nutrients': ['magnesium', 'calcium', 'tryptophan'],
                'fallback': 'sleep'
            },
            'mood': {
                'nutrients': ['omega_3', 'vitamin_d', 'vitamin_b'],
                'fallback': 'mood'
            },
            'bone_health': {
                'nutrients': ['calcium', 'vitamin_d', 'magnesium'],
                'fallback': 'bone_health'
            },
            'weight_management': {
                'nutrients': ['fiber', 'protein'],
                'fallback': 'weight_management'
            }
        }
        
        if symptom not in symptom_mapping:
            logger.warning(f"Unknown symptom: {symptom}")
            return self._get_fallback_foods(symptom)[:limit]
        
        config = symptom_mapping[symptom]
        
        # Try to get foods from nutrient database
        foods_found = False
        for nutrient_name in config.get('nutrients', []):
            nutrient_id = self._get_nutrient_id(nutrient_name)
            if nutrient_id:
                foods = self._get_foods_by_nutrient(nutrient_id, min_amount=1)
                if len(foods) > 0:
                    foods_found = True
                    for _, food in foods.head(limit).iterrows():
                        recommendations.append({
                            'food': food.get('description', 'Unknown'),
                            'nutrient': nutrient_name,
                            'amount': float(food.get('amount', 0)),
                            'reason': f"Rich in {nutrient_name.replace('_', ' ').title()} for {symptom.replace('_', ' ')} management"
                        })
        
        # If no foods found from database, use fallback
        if not foods_found or len(recommendations) == 0:
            fallback = self._get_fallback_foods(config.get('fallback', symptom))
            recommendations.extend(fallback)
        
        # Remove duplicates and sort
        seen = set()
        unique_recs = []
        for rec in recommendations:
            key = rec['food']
            if key not in seen:
                seen.add(key)
                unique_recs.append(rec)
        
        return unique_recs[:limit]
    
    def recommend_personalized(self, 
                              user_profile: Dict,
                              prediction_result: Dict,
                              limit: int = 15) -> Dict[str, List[Dict]]:
        """
        Generate personalized diet recommendations.
        
        Args:
            user_profile: User information (age, bmi, symptoms, etc.)
            prediction_result: ML model prediction results
            limit: Maximum recommendations per category
            
        Returns:
            Dictionary of recommendations by category
        """
        logger.info("Generating personalized diet recommendations...")
        
        recommendations = {
            'primary': [],
            'symptom_specific': {},
            'general_health': []
        }
        
        # Determine primary symptoms based on user profile and prediction
        symptoms = []
        
        # Check symptom thresholds (using the severity values from form: 0, 2, 5, 7, 10)
        # Also check for research questionnaire symptom names
        if user_profile.get('hot_flashes', 0) >= 2:
            symptoms.append('hot_flashes')
        
        if user_profile.get('sleep_disturbance', 0) >= 2 or user_profile.get('I feel no rest in my emotional life', 0) >= 3:
            symptoms.append('sleep')
            
        if (user_profile.get('mood_swings', 0) >= 2 or 
            user_profile.get('anxiety', 0) >= 2 or 
            user_profile.get('I feel moody in general', 0) >= 3 or 
            user_profile.get('I feel anxious', 0) >= 3):
            symptoms.append('mood')
        
        # Always include bone health for menopausal women or high-risk
        if prediction_result.get('is_menopausal', False) or prediction_result.get('probability', 0) > 0.4:
            symptoms.append('bone_health')
            recommendations['general_health'] = self.recommend_for_symptom('bone_health', limit=5)
        
        # Weight management if BMI is high
        if user_profile.get('bmi', 0) > 25:
            symptoms.append('weight_management')
        
        # Get symptom-specific recommendations
        for symptom in symptoms:
            recs = self.recommend_for_symptom(symptom, limit=limit)
            if recs:
                recommendations['symptom_specific'][symptom] = recs
        
        # Primary recommendations (top foods across all symptoms)
        all_recs = []
        for symptom_recs in recommendations['symptom_specific'].values():
            all_recs.extend(symptom_recs)
        
        # Rank by frequency and importance
        food_scores = {}
        for rec in all_recs:
            food = rec['food']
            if food not in food_scores:
                food_scores[food] = {'count': 0, 'rec': rec}
            food_scores[food]['count'] += 1
        
        # Sort by frequency
        sorted_foods = sorted(food_scores.items(), key=lambda x: x[1]['count'], reverse=True)
        recommendations['primary'] = [item[1]['rec'] for item in sorted_foods[:limit]]
        
        # If no primary recommendations, add general health ones
        if not recommendations['primary'] and recommendations['general_health']:
            recommendations['primary'] = recommendations['general_health'][:5]
        
        logger.info(f"Generated recommendations: {len(recommendations['primary'])} primary, {len(recommendations['symptom_specific'])} symptom categories")
        return recommendations
    
    def get_food_details(self, food_name: str) -> Optional[Dict]:
        """Get detailed nutritional information for a food."""
        if self.food_df is None or self.food_nutrient_df is None:
            return None
        
        # Find food
        food_match = self.food_df[
            self.food_df['description'].str.contains(food_name, case=False, na=False)
        ]
        
        if len(food_match) == 0:
            return None
        
        food_id = food_match.iloc[0]['fdc_id']
        
        # Get nutrients
        nutrients = self.food_nutrient_df[self.food_nutrient_df['fdc_id'] == food_id]
        
        # Merge with nutrient info
        if self.nutrient_info is not None:
            nutrients = nutrients.merge(
                self.nutrient_info[['id', 'name', 'unit_name']],
                left_on='nutrient_id',
                right_on='id',
                how='left'
            )
        
        return {
            'name': food_match.iloc[0]['description'],
            'nutrients': nutrients[['name', 'amount', 'unit_name']].to_dict('records')
        }
