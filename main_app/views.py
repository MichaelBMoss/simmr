from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .models import Recipe
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView

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


class RecipeCreateView(CreateView):
  model = Recipe
  fields = ['name', 'category', 'description', 'time', 'servings', 'ingredients', 'directions',]

  def form_valid(self, form):
    form.instance.user = self.request.user
    return super().form_valid(form)


class RecipesListView(ListView):
    model = Recipe


class RecipeDetailView(DetailView):
    model = Recipe


class RecipeUpdateView(UpdateView):
  model = Recipe
  fields = ['name', 'category', 'description', 'time', 'servings', 'ingredients', 'directions',]


class RecipeDeleteView(DeleteView):
  model = Recipe
#   delete should be updated to redirect to the users profile or the users list of authored recipes when posssible
  success_url = '/recipes/list/'
