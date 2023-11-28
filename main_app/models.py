from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser



class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=200, null=True)
    CATEGORY_CHOICES = [
        ('Breakfast', 'Breakfast'),
        ('Lunch', 'Lunch'),
        ('Dinner', 'Dinner'),
        ('Snack', 'Snack'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, null=True)
    description = models.TextField(max_length=2000, null=True)
    time = models.IntegerField(null=True)
    servings = models.IntegerField(null=True)
    ingredients = models.TextField(max_length=2000, null=True)
    directions = models.TextField(max_length=2000, null=True)
    bookmarks = models.ManyToManyField(User, related_name='bookmarked_recipes', blank=True)

    def __str__(self):
      return f'{self.name} ({self.id})'

    def get_absolute_url(self):
      return reverse('recipe_detail', kwargs={'pk': self.id})


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=2000)
    RATING_CHOICES = [
      (1, '1'),
      (2, '2'),
      (3, '3'),
      (4, '4'),
      (5, '5'),
    ]
    rating = models.IntegerField(choices=RATING_CHOICES, default=5)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    def __str__(self):
        return f'Review by {self.user.username}'
   

class Photo(models.Model):
    url = models.CharField(max_length=500)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)