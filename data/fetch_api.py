import requests
from typing import List, Dict, Any
from langchain.schema import Document
import time


def fetch_all_meals() -> List[Dict[str, Any]]:
   
    print("TheMealDB'den tarif verileri çekiliyor...")
    all_meals = []
    
    # A-Z harfleri için arama
    for letter in 'abcdefghijklmnopqrstuvwxyz':
        url = f"https://www.themealdb.com/api/json/v1/1/search.php?f={letter}"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('meals'):
                all_meals.extend(data['meals'])
                print(f"'{letter}' harfi için {len(data['meals'])} tarif bulundu")
            
            # Rate limiting için kısa bekleme
            time.sleep(0.1)
            
        except requests.RequestException as e:
            print(f"'{letter}' harfi için hata: {e}")
            continue
    
    print(f"Toplam {len(all_meals)} tarif çekildi")
    return all_meals


def process_meal_to_document(meals: List[Dict[str, Any]]) -> List[Document]:
    """Meals listesini Document listesine çevirir"""
    documents = []
    
    for meal in meals:
        text_parts = []
        
        # Temel bilgiler
        if meal.get('strMeal'):
            text_parts.append(f"Meal name: {meal['strMeal']}")
        if meal.get('strCategory'):
            text_parts.append(f"Category: {meal['strCategory']}")
        if meal.get('strArea'):
            text_parts.append(f"Cuisine: {meal['strArea']}")
        if meal.get('strTags'):
            text_parts.append(f"Tags: {meal['strTags']}")
        
        # Malzemeler
        ingredients = []
        for i in range(1, 21):
            ingredient = meal.get(f'strIngredient{i}')
            measure = meal.get(f'strMeasure{i}')
            if ingredient and ingredient.strip():
                if measure and measure.strip():
                    ingredients.append(f"{measure.strip()} {ingredient.strip()}")
                else:
                    ingredients.append(ingredient.strip())
        
        if ingredients:
            text_parts.append("Ingredients:")
            text_parts.extend([f"- {ing}" for ing in ingredients])
        
        # Yapılış
        if meal.get('strInstructions'):
            text_parts.append("Instructions:")
            text_parts.append(meal['strInstructions'])
        
        # Document objesi oluştur
        doc = Document(
            page_content="\n".join(text_parts),
            metadata={
                "meal_id": meal.get("idMeal", ""),
                "meal_name": meal.get("strMeal", ""),
                "category": meal.get("strCategory", ""),
                "cuisine": meal.get("strArea", ""),
                "text": "\n".join(text_parts)
            }
        )
        documents.append(doc)
    
    print(f"📄 {len(documents)} döküman oluşturuldu")
    return documents