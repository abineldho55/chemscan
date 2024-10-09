import requests
import logging
from .models import Product, NutritionFacts, Ingredient

logger = logging.getLogger(__name__)


# Function to fetch product details from Open Food Facts API
def fetch_product_details_from_api(barcode):
    api_url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            if 'product' in data:
                product_data = data['product']

                # Extract nutrition facts
                nutrition_data = product_data.get('nutriments', {})
                nutrition_facts = {
                    'energy_kj': nutrition_data.get('energy-kj', 0),
                    'energy_kcal': nutrition_data.get('energy-kcal', 0),
                    'fat': nutrition_data.get('fat', 0),
                    'saturated_fat': nutrition_data.get('saturated-fat', 0),
                    'carbohydrates': nutrition_data.get('carbohydrates', 0),
                    'sugars': nutrition_data.get('sugars', 0),
                    'proteins': nutrition_data.get('proteins', 0),
                    'salt': nutrition_data.get('salt', 0),
                }

                # Extract ingredients
                ingredients_text = product_data.get('ingredients_text', 'No ingredients listed')
                ingredients_list = parse_ingredients(ingredients_text)

                # Return structured product data
                return {
                    'barcode': product_data.get('code', ''),
                    'common_name': product_data.get('product_name', 'Unknown'),
                    'quantity': product_data.get('quantity', 'Unknown'),
                    'brand': product_data.get('brands', 'Unknown'),
                    'categories': product_data.get('categories', ''),
                    'image_url': product_data.get('image_url', None),
                    'health_rating': product_data.get('nutriments', {}).get('nutrition_grade_fr', 'No rating'),
                    'nutrition_facts': nutrition_facts,
                    'ingredients': ingredients_list,
                }
        else:
            logger.error(f"API returned non-200 status code: {response.status_code}")
    except requests.RequestException as e:
        logger.error(f"Error fetching product details from API: {e}")

    return None


# Function to parse the ingredients text into a list
def parse_ingredients(ingredients_text):
    if ingredients_text == 'No ingredients listed':
        return []

    ingredients = []
    for ingredient in ingredients_text.split(','):
        name = ingredient.strip()
        ingredients.append({'name': name, 'percentage': None})  # Set percentage to None as it is optional

    return ingredients


# Function to save product details into the database
# Function to save product details into the database
def save_product_to_db(product_data):
    # Check if product already exists
    product, created = Product.objects.get_or_create(
        barcode=product_data.get('barcode', ''),
        defaults={
            'common_name': product_data.get('common_name', 'Unknown'),
            'quantity': product_data.get('quantity', 'Unknown'),
            'brand': product_data.get('brand', 'Unknown'),
            'categories': product_data.get('categories', ''),
            'image_url': product_data.get('image_url', ''),
            'health_rating': product_data.get('health_rating', 'No rating'),
        }
    )

    # If the product is newly created, save nutrition facts and ingredients
    if created:
        # Save the nutrition facts
        NutritionFacts.objects.create(
            product=product,
            energy_kj=product_data['nutrition_facts'].get('energy_kj', 0),
            energy_kcal=product_data['nutrition_facts'].get('energy_kcal', 0),
            fat=product_data['nutrition_facts'].get('fat', 0),
            saturated_fat=product_data['nutrition_facts'].get('saturated_fat', 0),
            carbohydrates=product_data['nutrition_facts'].get('carbohydrates', 0),
            sugars=product_data['nutrition_facts'].get('sugars', 0),
            proteins=product_data['nutrition_facts'].get('proteins', 0),
            salt=product_data['nutrition_facts'].get('salt', 0),
        )

        # Prepare ingredients for bulk creation
        ingredients = [
            Ingredient(product=product, name=ingredient['name'], percentage=ingredient.get('percentage', None))
            for ingredient in product_data['ingredients']
        ]
        Ingredient.objects.bulk_create(ingredients)

    return product
