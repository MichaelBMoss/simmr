from typing import Any
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.db.models import Avg, Count
from .models import Recipe, Review, Photo
from .forms import ReviewForm, RecipeCreateForm
from django.contrib.auth.models import User
import uuid, boto3, os, random


# NOTE: For later when we need to implement authorization for specific actions 
# from django.contrib.auth.decorators import login_required
# from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.


def home(request):
    random_category = random.choice(Recipe.CATEGORY_CHOICES)
    category_recipes = Recipe.objects.filter(category=random_category[0]).order_by('?')[:3]

    top_recipes = Recipe.objects.annotate(avg_rating=Avg('review__rating')).order_by('avg_rating')[:3]

    random_appliance = random.choice(Recipe.APPLIANCE_CHOICES)
    appliance_recipes = Recipe.objects.filter(appliance=random_appliance[0]).order_by('?')[:3]

    context = {
        'category': random_category[0],
        'category_recipes': category_recipes,
        'top_recipes': top_recipes,
        'appliance': random_appliance[0],
        'appliance_recipes': appliance_recipes,
    }

    return render(request, 'home.html', context)



def about(request):
    return render(request, 'about.html')


def signup(request):
    error_message = ''
    if request.method == 'POST': 
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
        else:
            error_message = 'Invalid sign up - try again'
    form = UserCreationForm()
    context = { 'form': form, 'error_message': error_message }
    return render(request, 'registration/signup.html', context)


def add_review(request, recipe_id):
    form = ReviewForm(request.POST)
    if form.is_valid():
      new_review = form.save(commit=False)
      new_review.user = request.user
      new_review.recipe_id = recipe_id
      new_review.save()
    return redirect('recipe_detail', pk=recipe_id)


def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user == review.user:
      if request.method == 'POST':
         review.delete()
         return redirect('recipe_detail', pk=review.recipe.id)
    return redirect('recipe_detail', pk=review.recipe.id)


def profile(request, pk):
    user = get_object_or_404(User, pk=pk)
    authored_recipes = Recipe.objects.filter(author=user)
    bookmarked_recipes = user.bookmarked_recipes.all()
    return render(request, 'profile.html', {
        'user': user,
        'authored_recipes': authored_recipes,
        'bookmarked_recipes': bookmarked_recipes
    })


def bookmark_recipe(request, recipe_id):
    if not request.user.is_authenticated:
        return redirect('login')
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    if request.user in recipe.bookmarks.all():
        recipe.bookmarks.remove(request.user)
    else:
        recipe.bookmarks.add(request.user)
    return redirect('recipe_detail', pk=recipe_id)



class RecipeCreateView(CreateView):
    model = Recipe
    form_class = RecipeCreateForm

    def form_valid(self, form):
        form.instance.author = self.request.user

        recipe = form.save()

        photo_file = self.request.FILES.get('photo', None)
        if photo_file:

            s3 = boto3.client('s3')
            key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
            try:
                bucket = os.environ['S3_BUCKET']
                s3.upload_fileobj(photo_file, bucket, key)
                url = f"{os.environ['S3_BASE_URL']}{bucket}/{key}"

                Photo.objects.create(url=url, recipe=recipe)
            except Exception as e:
                print('An error occurred uploading file to S3')
                print(e)

        return super().form_valid(form)


class RecipesListView(ListView):
    model = Recipe

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for recipe in Recipe.objects.all():
            reviews_info = recipe.review_set.aggregate(avg_rating=Avg('rating'), total_reviews=Count('id'))
            recipe.avg_rating = reviews_info['avg_rating']
            recipe.total_reviews = reviews_info['total_reviews']

        return context


class RecipeDetailView(DetailView):
    model = Recipe

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['review_form'] = ReviewForm()

        if self.request.user.is_authenticated:
            user = self.request.user
            recipe = self.get_object()
            has_reviewed = recipe.review_set.filter(user=user).exists()
            context['has_reviewed'] = has_reviewed
        
        photo = Photo.objects.filter(recipe=context['recipe']).first()
        context['photo'] = photo
        
        return context


class RecipeUpdateView(UpdateView):
  model = Recipe
  fields = ['name', 'category', 'appliance', 'description', 'time', 'servings', 'ingredients', 'directions',]


class RecipeDeleteView(DeleteView):
  model = Recipe
#   delete should be updated to redirect to the users profile or the users list of authored recipes when posssible
  success_url = '/recipes/list/'



def recipe_add_photo(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    
    if request.method == 'POST':
        photo_file = request.FILES.get('photo-file', None)
        if photo_file:
            s3 = boto3.client('s3')
            key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
            try:
                bucket = os.environ['S3_BUCKET']
                s3.upload_fileobj(photo_file, bucket, key)
                url = f"{os.environ['S3_BASE_URL']}{bucket}/{key}"
                # First, delete existing photos only if a new photo is successfully uploaded.
                recipe.photo_set.all().delete()
                Photo.objects.create(url=url, recipe=recipe)
            except Exception as e:
                print('An error occurred uploading file to S3')
                print(e)
    
    return redirect('recipe_detail', pk=recipe_id)


   