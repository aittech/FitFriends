from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from tracker.forms import EmailAuthenticationForm
urlpatterns = [
    
    path('', views.landing, name='home'), # make landing the home
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # signup
    path('signup/', views.signup, name='signup'),
    
     # suggestions
    path('exercises/suggest/', views.suggest_exercise, name='suggest_exercise'),
    path('workouts/suggest/', views.suggest_workout, name='suggest_workout'),
    
    # Exercises
    path('exercises/', views.exercise_list, name='exercise_list'),
    path('exercises/search/', views.exercise_search, name='exercise_search'),
    path('exercises/<int:pk>/', views.exercise_detail, name='exercise_detail'),

    # Workouts
    path('workouts/', views.workout_list, name='workout_list'),
    path('workouts/<int:pk>/', views.workout_detail, name='workout_detail'),
    
    # auth
    path('login/', auth_views.LoginView.as_view(
    	template_name='tracker/login.html',
    	authentication_form=EmailAuthenticationForm
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(
        next_page='login'
    ), name='logout'),
    
    path("verify-email/<uidb64>/<token>/", views.verify_email, name="verify_email"),
]
