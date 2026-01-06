from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import SignUpForm

from .models import Exercise, Workout, DailyLog
from .forms import (
    DailyLogForm,
    UserExerciseSuggestionForm,
    UserWorkoutSuggestionForm,
    SignUpForm,
)


# ---------- EXERCISES ----------

def exercise_list(request):
    """
    List all approved exercises.
    """
    exercises = Exercise.objects.filter(is_approved=True).order_by('name')
    return render(request, 'tracker/exercise_list.html', {
        'exercises': exercises,
    })


def exercise_search(request):
    """
    Search approved exercises by name or muscle group.
    """
    query = request.GET.get('q', '').strip()
    exercises = Exercise.objects.filter(is_approved=True)

    if query:
        exercises = exercises.filter(
            name__icontains=query
        ) | exercises.filter(
            muscle_group__icontains=query
        )

    exercises = exercises.order_by('name')

    return render(request, 'tracker/exercise_search.html', {
        'query': query,
        'exercises': exercises,
    })


def exercise_detail(request, pk):
    """
    Show one exercise with description and video link.
    """
    exercise = get_object_or_404(Exercise, pk=pk, is_approved=True)
    return render(request, 'tracker/exercise_detail.html', {
        'exercise': exercise,
    })


# ---------- WORKOUTS ----------

def workout_list(request):
    """
    List all approved workouts.
    """
    workouts = Workout.objects.filter(is_approved=True).order_by('name')
    return render(request, 'tracker/workout_list.html', {
        'workouts': workouts,
    })


def workout_detail(request, pk):
    """
    Show a single workout with its exercises in order.
    """
    workout = get_object_or_404(Workout, pk=pk, is_approved=True)
    workout_exercises = workout.workoutexercise_set.select_related('exercise').all()

    return render(request, 'tracker/workout_detail.html', {
        'workout': workout,
        'workout_exercises': workout_exercises,
    })
    
def landing(request):
    """
    Public landing page.
    If the user is logged in, send them straight to the dashboard.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    return render(request, 'tracker/landing.html')



# ---------- DASHBOARD (DAILY LOG) ----------

@login_required
def dashboard(request):
    today = timezone.localdate()

    # get or create today's log for this user
    log, _ = DailyLog.objects.get_or_create(
        user=request.user,
        date=today,
    )

    if request.method == 'POST':
        form = DailyLogForm(request.POST, instance=log, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your daily log has been saved.")
    else:
        form = DailyLogForm(instance=log, user=request.user)

    recent_logs = DailyLog.objects.filter(user=request.user).order_by('-date')[:7]

    return render(request, 'tracker/dashboard.html', {
        'form': form,
        'today': today,
        'recent_logs': recent_logs,
    })


# ---------- USER SUGGESTIONS ----------

@login_required
def suggest_exercise(request):
    """
    Allow a logged-in user to suggest a new exercise.
    It will be saved as not approved and only visible after admin approval.
    """
    if request.method == 'POST':
        form = UserExerciseSuggestionForm(request.POST)
        if form.is_valid():
            exercise = form.save(commit=False)
            exercise.created_by = request.user
            exercise.is_approved = False  # must be approved in admin
            exercise.save()
            messages.success(request, "Thank you! Your exercise has been submitted for review.")
            return redirect('exercise_list')
    else:
        form = UserExerciseSuggestionForm()

    return render(request, 'tracker/suggest_exercise.html', {'form': form})


@login_required
def suggest_workout(request):
    """
    Allow a logged-in user to suggest a new workout.
    It will be saved as not approved and only visible after admin approval.
    """
    if request.method == 'POST':
        form = UserWorkoutSuggestionForm(request.POST)
        if form.is_valid():
            workout = form.save(commit=False)
            workout.created_by = request.user
            workout.is_approved = False  # must be approved in admin
            workout.save()
            messages.success(request, "Thank you! Your workout has been submitted for review.")
            return redirect('workout_list')
    else:
        form = UserWorkoutSuggestionForm()

    return render(request, 'tracker/suggest_workout.html', {'form': form})

def signup(request):
    """
    Allow a new user to sign up with email, password, DOB, gender and country.
    """
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Welcome to FitFriends! Your account has been created.")
            auth_login(request, user)  # log them in immediately
            return redirect('dashboard')
    else:
        form = SignUpForm()

    return render(request, 'tracker/signup.html', {'form': form})
