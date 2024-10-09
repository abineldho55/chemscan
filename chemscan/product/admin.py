from django.contrib import admin
from .models import UserProfile, Product, NutritionFacts, Ingredient

# Inline for NutritionFacts
class NutritionFactsInline(admin.StackedInline):
    model = NutritionFacts
    can_delete = False  # Prevent deletion since it's OneToOne with Product
    verbose_name_plural = 'Nutrition Facts'  # Plural name displayed in admin

# Inline for Ingredients
class IngredientInline(admin.TabularInline):
    model = Ingredient
    extra = 1  # Number of extra empty ingredient forms to display

# Product admin that shows NutritionFacts and Ingredients in the product form
class ProductAdmin(admin.ModelAdmin):
    inlines = [NutritionFactsInline, IngredientInline]  # Add the inlines to Product

# Register UserProfile and Product models
admin.site.register(UserProfile)
admin.site.register(Product, ProductAdmin)  # Use ProductAdmin to include NutritionFacts and Ingredients

# If you want to edit NutritionFacts and Ingredient separately from Product, you can register them directly
admin.site.register(NutritionFacts)
admin.site.register(Ingredient)
