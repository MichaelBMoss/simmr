from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


class Recipe(models.Model):
  name = models.CharField(max_length=200)
  category = models.CharField(max_length=200)
  description = models.TextField(max_length=2000)
  directions = models.TextField(max_length=2000)
  user = models.ForeignKey(User, on_delete=models.CASCADE)

  def __str__(self):
    return f'{self.name} ({self.id})'

  def get_absolute_url(self):
    return reverse('detail', kwargs={'recipe_id': self.id})

