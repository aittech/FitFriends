from django.db import models
from django.contrib.auth.models import User


class Exercise(models.Model):
    name = models.CharField(max_length=150)
    muscle_group = models.CharField(max_length=100, blank=True)
    equipment = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    video_url = models.URLField(blank=True)

    # NEW
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='exercises_created'
    )
    is_approved = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Workout(models.Model):
    CATEGORY_CHOICES = [
        ('cardio', 'Cardio'),
        ('full_body_strength', 'Full Body Strength'),
        ('upper_body_strength', 'Upper Body Strength'),
        ('lower_body_strength', 'Lower Body Strength'),
        ('mobility', 'Mobility / Stretching'),
        ('bodyweight', 'Bodyweight Only'),
        # you can add more as needed
    ]

    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    total_time_minutes = models.IntegerField(
        null=True,
        blank=True,
        help_text="Approximate time in minutes"
    )
    difficulty = models.CharField(
        max_length=20,
        choices=[
            ('easy', 'Easy'),
            ('moderate', 'Moderate'),
            ('hard', 'Hard'),
        ],
        default='easy'
    )

    # 👇 NEW
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='cardio',
    )
    
    video_url = models.URLField(
        blank=True,
        help_text="Link to a video explaining or demonstrating this workout."
    )


    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='workouts_created'
    )
    
    is_approved = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    exercises = models.ManyToManyField(
        Exercise,
        through='WorkoutExercise',
        related_name='workouts'
    )
    
    def __str__(self):
        return self.name
    
    def author_name(self):
        """
        Human-friendly name of who created the workout.
        Falls back to 'FitFriends' if it's a built-in workout.
        """
        if self.created_by:
            # Try profile display name first
            profile = getattr(self.created_by, "profile", None)
            if profile and profile.display_name:
                return profile.display_name

            # Then full name, then username
            full_name = self.created_by.get_full_name()
            if full_name:
                return full_name
            return self.created_by.username

        return "FitFriends"


class WorkoutExercise(models.Model):
    """
    Join table between Workout and Exercise.
    Defines order, sets, reps, etc. for each exercise in a workout.
    """
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=1)
    sets = models.PositiveIntegerField(null=True, blank=True)
    reps = models.PositiveIntegerField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="For timed exercises like planks, in seconds"
    )
    notes = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['order']
        unique_together = ('workout', 'exercise', 'order')

    def __str__(self):
        return f"{self.workout.name} - {self.order}. {self.exercise.name}"

class DailyLog(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='daily_logs'
    )
    date = models.DateField()

    sleep_hours = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Total sleep for the night in hours, e.g. 7.5"
    )
    fasting_hours = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Hours fasted since last meal"
    )
    calories = models.IntegerField(
        null=True,
        blank=True,
        help_text="Estimated total calories for the day"
    )

    # 👇 single workout for now
    workout = models.ForeignKey(
        Workout,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='daily_logs',
        help_text="Workout you followed today (if any)",
    )
    
     # NEW: allow several workouts per day
    workouts = models.ManyToManyField(
        Workout,
        blank=True,
        related_name='daily_logs_multi',
        help_text="All workouts you did today (if any)",
    )

    workout_completed = models.BooleanField(default=False)

    notes = models.CharField(
        max_length=200,
        blank=True,
        help_text="Optional: how you felt, steps, etc."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} – {self.date}"




class Profile(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not', 'Prefer not to say'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    # NEW fields
    display_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Name shown on your profile and leaderboards."
    )

    is_public = models.BooleanField(
        default=False,
        help_text="If public, others can see your stats and you can appear on leaderboards."
    )

    profile_photo = models.ImageField(
        upload_to='profile_photos/',
        null=True,
        blank=True,
        help_text="Optional profile picture."
    )

    # Existing fields
    date_of_birth = models.DateField(null=True, blank=True)

    gender = models.CharField(
        max_length=20,
        choices=GENDER_CHOICES,
        blank=True
    )

    country = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Profile for {self.user.username}"

