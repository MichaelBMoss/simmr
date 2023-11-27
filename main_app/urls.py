from django.urls import path
from . import views 

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('accounts/signup/', views.signup, name='signup'),
    path('recipes/create/', views.RecipeCreateView.as_view(), name='recipes_create'),
    path('recipes/list/', views.RecipesListView.as_view(), name='recipes_list'),
    path('recipes/<int:pk>/', views.RecipeDetailView.as_view(), name='recipe_detail'),
    path('recipes/<int:pk>/update/', views.RecipeUpdateView.as_view(), name='recipes_update'),
    path('recipes/<int:pk>/delete/', views.RecipeDeleteView.as_view(), name='recipes_delete'),
    path('profile/<int:pk>/', views.profile, name='profile'),
    path('recipes/bookmark/<int:recipe_id>/', views.bookmark_recipe, name='bookmark_recipe'),

]