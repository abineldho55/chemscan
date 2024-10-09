from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    age = models.PositiveIntegerField(blank=True, null=True)


    def __str__(self):
        return self.user.username

class Product(models.Model):
    barcode = models.CharField(max_length=50, unique=True)  # Barcode
    common_name = models.CharField(max_length=255, )
    quantity = models.CharField(max_length=50, )
    brand = models.CharField(max_length=255, )
    categories = models.TextField()
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    health_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)

    def __str__(self):
        return self.common_name

class NutritionFacts(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)  # Link to product
    energy_kj = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)  # Default energy in kilojoules
    energy_kcal = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)  # Default energy in kcal
    fat = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  # Default fat value
    saturated_fat = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  # Default saturated fat
    carbohydrates = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  # Default carbohydrates
    sugars = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  # Default sugars
    proteins = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  # Default proteins
    salt = models.DecimalField(max_digits=5, decimal_places=3, default=0.000)  # Default salt

    def __str__(self):
        return f'Nutrition Facts for {self.product.common_name}'

class Ingredient(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Link to product
    name = models.CharField(max_length=255, )  # Default ingredient name
    percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)  # Optional percentage

    def __str__(self):
        return self.name
