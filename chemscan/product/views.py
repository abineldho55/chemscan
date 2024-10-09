from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SignUpForm, CustomLoginForm, BarcodeForm, ProductForm
from .models import Product, UserProfile, NutritionFacts, Ingredient
from django.http import JsonResponse
from .services import fetch_product_details_from_api, save_product_to_db


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data.get('email')  # Use email as the username
            user.save()
            UserProfile.objects.create(
                user=user,
                full_name=form.cleaned_data.get('full_name'),
                age=form.cleaned_data.get('age'),
            )
            user = authenticate(username=user.username, password=form.cleaned_data.get('password1'))
            if user is not None:
                login(request, user)
            messages.success(request, 'Registration successful! You are now logged in.')
            return redirect('home')  # Redirect to a view named 'home'
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Successfully logged in!')
            return redirect('home')  # Redirect to a view named 'home'
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = CustomLoginForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'Successfully logged out!')
    return redirect('login')  # Redirect to the login page


@login_required
def scan_barcode(request):
    form = BarcodeForm()
    user_profile = UserProfile.objects.get(user=request.user)

    if request.method == 'POST':
        form = BarcodeForm(request.POST)
        if form.is_valid():
            barcode = form.cleaned_data['barcode']

            # Try to fetch product from local database
            product = Product.objects.get(barcode=barcode)

            if not product:
                # Fetch product from external API (Open Food Facts)
                product_data = fetch_product_details_from_api(barcode)

                if product_data:
                    # Save product data to the database (corrected line)
                    product = save_product_to_db(product_data)

            # Calculate health rating and intake limits based on user profile (age)
            intake_limits, health_rating = calculate_product_intake_and_rating(product, user_profile.age)

            # Render the product details template with data
            return render(request, 'product_details.html', {
                'product': product,
                'intake_limits': intake_limits,
                'health_rating': health_rating,
                'user_age': user_profile.age
            })

    return render(request, 'home.html', {'form': form})
# Function to calculate intake limits and health rating based on product and age
def calculate_product_intake_and_rating(product, age):

    nutrition_facts = NutritionFacts.objects.get(product=product)

    # Example intake limits based on age
    intake_limits = {
        'energy_kcal': nutrition_facts.energy_kcal * (0.5 if age < 18 else 1),
        'fat': nutrition_facts.fat * (0.5 if age < 18 else 1),
        'sugars': nutrition_facts.sugars * (0.5 if age < 18 else 1),
    }

    # Example health rating calculation (can be customized)
    health_rating = product.health_rating

    return intake_limits, health_rating


def product_details(request, barcode):
    # Fetch the product object using barcode
    product = Product.objects.get(barcode=barcode)

    # Query the NutritionFacts model based on the product
    nutrition_facts = NutritionFacts.objects.get(product=product)

    # Query the Ingredient model based on the product
    ingredients = Ingredient.objects.get(product=product)

    # Print the values for debugging
    print("Nutrition Facts:")
    print(nutrition_facts)

    print("Ingredients:")
    print(ingredients)

    return render(request, 'product_details.html', {
        'product': product,
        'nutrition_facts': nutrition_facts,
        'ingredients': ingredients
    })

def edit_product(request, barcode):
    product, created = Product.objects.get_or_create(barcode=barcode)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_details', barcode=barcode)
    else:
        form = ProductForm(instance=product)

    return render(request, 'edit_product.html', {'form': form})


def fetch_product_details(request):
    barcode = request.GET.get('barcode')

    if barcode:
        # First, check if the product exists in the local database
        try:
            product = Product.objects.get(barcode=barcode)
            # Fetch nutrition facts and ingredients
            nutrition_facts = product.nutrition_facts
            Ingredient = product.Ingredient_set.all()

            return JsonResponse({
                'barcode': product.barcode,
                'common_name': product.common_name,
                'quantity': product.quantity,
                'brand': product.brand,
                'categories': product.categories,
                'image_url': product.image.url if product.image else None,
                'health_rating': product.health_rating,
                'nutrition_facts': {
                    'energy_kcal': nutrition_facts.energy_kcal,
                    'fat': nutrition_facts.fat,
                    'saturated_fat': nutrition_facts.saturated_fat,
                    'carbohydrates': nutrition_facts.carbohydrates,
                    'sugars': nutrition_facts.sugars,
                    'proteins': nutrition_facts.proteins,
                    'salt': nutrition_facts.salt,
                },
                'ingredients': [{'name': ingredient.name, 'percentage': ingredient.percentage} for ingredient in Ingredient]
            })
        except Product.DoesNotExist:
            # If not found in the database, fetch from the external API
            product_data = fetch_product_details_from_api(barcode)
    if product_data:
                # Save the product to the local database
                product = save_product_to_db(product_data)
                return JsonResponse({
                    'barcode': product.barcode,
                    'common_name': product.common_name,
                    'quantity': product.quantity,
                    'brand': product.brand,
                    'categories': product.categories,
                    'image_url': product.image.url if product.image else None,
                    'health_rating': product.health_rating,
                    'nutrition_facts': {
                        'energy_kcal': product.nutrition_facts.energy_kcal,
                        'fat': product.nutrition_facts.fat,
                        'saturated_fat': product.nutrition_facts.saturated_fat,
                        'carbohydrates': product.nutrition_facts.carbohydrates,
                        'sugars': product.nutrition_facts.sugars,
                        'proteins': product.nutrition_facts.proteins,
                        'salt': product.nutrition_facts.salt,
                    },
                    'ingredients': [{'name': ingredient.name, 'percentage': ingredient.percentage} for ingredient in product.ingredient_set.all()]
                })

    return JsonResponse({'error': 'Product not found.'})


def home(request):
    if request.method == 'POST':
        form = BarcodeForm(request.POST)
        if form.is_valid():
            barcode = form.cleaned_data['barcode']
            return redirect('product_details', barcode=barcode)  # Pass barcode to details page
    else:
        form = BarcodeForm()

    return render(request, 'home.html', {'form': form})


def index(request):
    return render(request, 'index.html')
