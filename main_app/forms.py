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

    name = forms.CharField(required=True)
    category = forms.ChoiceField(choices=Recipe.CATEGORY_CHOICES, required=True)
    description = forms.CharField(required=True, widget=forms.Textarea)
    ingredients = forms.CharField(required=True, widget=forms.Textarea)
    directions = forms.CharField(required=True, widget=forms.Textarea)
    photo = forms.ImageField(required=True)


class RecipeFilterForm(forms.Form):
    CATEGORY_CHOICES = [('All', 'All')] + Recipe.CATEGORY_CHOICES
    APPLIANCE_CHOICES = [('All', 'All')] + Recipe.APPLIANCE_CHOICES

    combined_choices = CATEGORY_CHOICES + APPLIANCE_CHOICES

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
