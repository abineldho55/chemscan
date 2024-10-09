from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Product, NutritionFacts, Ingredient

class SignUpForm(UserCreationForm):
    full_name = forms.CharField(
        max_length=100,
        help_text='Required. Enter your full name.',
        widget=forms.TextInput(attrs={'id': 'id_full_name'})
    )
    email = forms.EmailField(
        max_length=254,
        help_text='Required. Provide a valid email address.',
        widget=forms.TextInput(attrs={'id': 'id_email'})
    )
    age = forms.IntegerField(
        required=False,
        help_text='Optional. Enter your age.',
        widget=forms.NumberInput(attrs={'id': 'id_age'})

    )

    class CustomUserCreationForm(forms.Form):
        password1 = forms.CharField(
            widget=forms.PasswordInput(attrs={'id': 'id_password1'})
        )
        password2 = forms.CharField(
            widget=forms.PasswordInput(attrs={'id': 'id_password2'})
        )

    class Meta:
        model = User
        fields = ('full_name', 'email', 'age', 'password1', 'password2')


    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']  # Use email as the username
        if commit:
            user.save()
        return user

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'autofocus': True}),
        help_text='Enter your username'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'id': 'id_password1'}),
        help_text='Enter your password'
    )

class BarcodeForm(forms.Form):
        barcode = forms.CharField(max_length=20, label="Enter or Scan Barcode")


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['barcode', 'common_name', 'quantity', 'brand', 'categories', 'image', 'health_rating']

# NutritionFacts form
class NutritionFactsForm(forms.ModelForm):
    class Meta:
        model = NutritionFacts
        fields = ['energy_kj', 'energy_kcal', 'fat', 'saturated_fat', 'carbohydrates', 'sugars', 'proteins', 'salt']

# Ingredient form
class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ['product', 'name', 'percentage']