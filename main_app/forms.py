from django.forms import ModelForm
from .models import Review, Recipe
from django import forms


class ReviewForm(ModelForm):
    class Meta: 
        model = Review
        fields = ['content', 'rating']


class RecipeCreateForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['name', 'category', 'appliance', 'description', 'time', 'servings', 'ingredients', 'directions']

    # Additional field definitions with specific requirements.
    name = forms.CharField(required=True)
    category = forms.ChoiceField(choices=Recipe.CATEGORY_CHOICES, required=True)
    description = forms.CharField(required=True, widget=forms.Textarea)
    ingredients = forms.CharField(required=True, widget=forms.Textarea)
    directions = forms.CharField(required=True, widget=forms.Textarea)
    photo = forms.ImageField(required=True) # Adding photo field to form though photo is not part of the recipe model allows us to send photo from the photo form to the photo model

# Form for the filter button on the all recipes page
class RecipeFilterForm(forms.Form):
    CATEGORY_CHOICES = Recipe.CATEGORY_CHOICES
    APPLIANCE_CHOICES = Recipe.APPLIANCE_CHOICES

    # Create choices with modified labels to categorize filter options.
    combined_choices = [
        ('Filter Options', [
            ('All', 'All'), 
            ('ByRating', 'By Rating'),
        ]),
        ('Filter By Category', [
            ('Breakfast', 'Breakfast'),
            ('Lunch', 'Lunch'),
            ('Dinner', 'Dinner'),
            ('Snack', 'Snack'),
            ('Sweets', 'Sweets'),
        ]),
        ('Filter By Appliance', [
            ('Air Fryer', 'Air Fryer'),
            ('Microwave', 'Microwave'),
            ('Oven', 'Oven'),
            ('Pressure Cooker', 'Pressure Cooker'),
            ('Slow Cooker', 'Slow Cooker'),
            ('Stove', 'Stove'),
        ]),
    ]

    filter_choice = forms.ChoiceField(choices=combined_choices, required=False)


class RecipeUpdateForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['name', 'category', 'appliance', 'description', 'time', 'servings', 'ingredients', 'directions']

    name = forms.CharField(required=True)
    category = forms.ChoiceField(choices=Recipe.CATEGORY_CHOICES, required=True)
    description = forms.CharField(required=True, widget=forms.Textarea)
    ingredients = forms.CharField(required=True, widget=forms.Textarea)
    directions = forms.CharField(required=True, widget=forms.Textarea)
    photo = forms.ImageField(required=False)