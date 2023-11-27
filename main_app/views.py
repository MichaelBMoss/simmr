from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from .models import Recipe, Review
from .forms import ReviewForm
from django.contrib.auth.models import User

# NOTE: For later when we need to implement authorization for specific actions 
# from django.contrib.auth.decorators import login_required
# from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
def home(request):
    return render(request, 'home.html')


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
  fields = ['name', 'category', 'description', 'time', 'servings', 'ingredients', 'directions',]

  def form_valid(self, form):
    form.instance.author = self.request.user
    return super().form_valid(form)


class RecipesListView(ListView):
    model = Recipe


class RecipeDetailView(DetailView):
    model = Recipe
    # template_name = 'recipe_detail.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['review_form'] = ReviewForm()
        return context


class RecipeUpdateView(UpdateView):
  model = Recipe
  fields = ['name', 'category', 'description', 'time', 'servings', 'ingredients', 'directions',]


class RecipeDeleteView(DeleteView):
  model = Recipe
#   delete should be updated to redirect to the users profile or the users list of authored recipes when posssible
  success_url = '/recipes/list/'

