from typing import Any
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.db.models import Avg, Count, Q
from .models import Recipe, Review, Photo
from .forms import ReviewForm, RecipeCreateForm, RecipeFilterForm, RecipeUpdateForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
import uuid, boto3, os, random


# Get highest rated recipes and append unrated recipes to the list
recipes_sorted_by_rating = Recipe.objects.annotate(avg_rating=Avg('review__rating')).order_by('-avg_rating')
recipes_with_ratings = [recipe for recipe in recipes_sorted_by_rating if recipe.avg_rating is not None]
recipes_without_ratings = [recipe for recipe in recipes_sorted_by_rating if recipe.avg_rating is None]
all_recipes_by_rating = recipes_with_ratings + recipes_without_ratings
top_recipes = all_recipes_by_rating[:3]


def home(request):
    # Randomly select a category and fetch 3 recipes from that category.
    random_category = random.choice(Recipe.CATEGORY_CHOICES)
    category_recipes = Recipe.objects.filter(category=random_category[0]).order_by('?')[:3]

    # Randomly select an appliance and fetch 3 recipes using that appliance.
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
            # Save the new user and log them in.
            user = form.save()
            login(request, user)
            return redirect('home')
        else:
            error_message = 'Invalid sign up - try again'
    form = UserCreationForm()
    context = { 'form': form, 'error_message': error_message }
    return render(request, 'registration/signup.html', context)


@login_required
def add_review(request, recipe_id):
    form = ReviewForm(request.POST)
    if form.is_valid():
      # Save the review, associating it with the logged-in user and the respective recipe.
      new_review = form.save(commit=False)
      new_review.user = request.user
      new_review.recipe_id = recipe_id
      new_review.save()
    return redirect('recipe_detail', pk=recipe_id)


def edit_review(request, recipe_id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        # Return a 403 Forbidden response if the user is not the author of the review.
        return render(request, '403.html')

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('recipe_detail', pk=recipe_id)
    else:
        form = ReviewForm(instance=review)
    return render(request, 'edit_review.html', {'form': form})


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user == review.user:
         # Delete the review only if the user is the author of the review.
         review.delete()
         return redirect('recipe_detail', pk=review.recipe.id)
    return redirect('recipe_detail', pk=review.recipe.id)


@login_required
def profile(request, username):
    user = get_object_or_404(User, username=username)
    authored_recipes = Recipe.objects.filter(author=user)
    bookmarked_recipes = user.bookmarked_recipes.all()
    return render(request, 'profile.html', {
        'user': user,
        'authored_recipes': authored_recipes,
        'bookmarked_recipes': bookmarked_recipes
    })


@login_required
def bookmark_recipe(request, recipe_id):
    if not request.user.is_authenticated:
        return redirect('login')
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    if request.user in recipe.bookmarks.all():
        # If the user has bookmarked the recipe, remove the bookmark.
        recipe.bookmarks.remove(request.user)
    else:
        # If the user has not bookmarked the recipe, add a bookmark.
        recipe.bookmarks.add(request.user)
    return redirect('recipe_detail', pk=recipe_id)


class RecipeCreateView(LoginRequiredMixin, CreateView):
    model = Recipe
    form_class = RecipeCreateForm

    def form_valid(self, form):
        form.instance.author = self.request.user

        recipe = form.save()

        # Upload a photo to Amazon S3 if provided in the form.
        photo_file = self.request.FILES.get('photo', None)
        if photo_file:
            s3 = boto3.client('s3')
            key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
            try:
                bucket = os.environ['S3_BUCKET']
                s3.upload_fileobj(photo_file, bucket, key)
                url = f"{os.environ['S3_BASE_URL']}{bucket}/{key}"

                # Create a Photo object and associate it with the recipe.
                Photo.objects.create(url=url, recipe=recipe)
            except Exception as e:
                print('An error occurred uploading file to S3')
                print(e)

        return super().form_valid(form)


class RecipeUpdateView(LoginRequiredMixin, UpdateView):
    model = Recipe
    form_class = RecipeUpdateForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        recipe = form.save()

        # Upload a new photo to Amazon S3 if provided in the form.
        photo_file = self.request.FILES.get('photo', None)
        if photo_file:
            s3 = boto3.client('s3')
            key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
            try:
                bucket = os.environ['S3_BUCKET']
                s3.upload_fileobj(photo_file, bucket, key)
                url = f"{os.environ['S3_BASE_URL']}{bucket}/{key}"
                
                # Replace any existing photos associated with the recipe.
                existing_photos = Photo.objects.filter(recipe=recipe)
                existing_photos.delete()
                Photo.objects.create(url=url, recipe=recipe)
            except Exception as e:
                print('An error occurred uploading file to S3')
                print(e)

        return super().form_valid(form)


class RecipesListView(ListView):
    model = Recipe
    template_name = 'main_app/recipe_list.html'
    context_object_name = 'recipe_list'
    form_class = RecipeFilterForm

    def get_queryset(self):
        filter_choice = self.request.GET.get('filter_choice')
        queryset = Recipe.objects.all()

        if filter_choice == 'ByRating':
            # If the user selects "By Rating," return the top_recipes queryset
            return all_recipes_by_rating
        elif filter_choice and filter_choice != 'All':
            queryset = queryset.filter(
                Q(category=filter_choice) | Q(appliance=filter_choice)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Calculate and add average ratings and total review counts to recipe objects in the context.
        for recipe in context['recipe_list']:
            reviews_info = recipe.review_set.aggregate(
                avg_rating=Avg('rating'), total_reviews=Count('id')
            )
            recipe.avg_rating = reviews_info['avg_rating']
            recipe.total_reviews = reviews_info['total_reviews']
        
        # Add the recipe filter form to the context.
        context['form'] = self.form_class(self.request.GET)

        return context


class RecipeDetailView(DetailView):
    model = Recipe

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['review_form'] = ReviewForm()  # Include a review form in the context.

        if self.request.user.is_authenticated:
            user = self.request.user
            recipe = self.get_object()
            has_reviewed = recipe.review_set.filter(user=user).exists()
            context['has_reviewed'] = has_reviewed  # Indicate if the user has already reviewed the recipe.

        # Get the first associated photo for the recipe and add it to the context.
        photo = Photo.objects.filter(recipe=context['recipe']).first()
        context['photo'] = photo

        return context


class RecipeDeleteView(LoginRequiredMixin, DeleteView):
    model = Recipe
    success_url = '/recipes/list/'  # Redirect to the recipe list page after successful deletion.


@login_required
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
                # Delete existing photos associated with the recipe and create a new Photo object.
                recipe.photo_set.all().delete()
                Photo.objects.create(url=url, recipe=recipe)
            except Exception as e:
                print('An error occurred uploading file to S3')
                print(e)
    
    return redirect('recipe_detail', pk=recipe_id)