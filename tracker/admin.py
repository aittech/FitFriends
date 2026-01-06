from django.contrib import admin
from .models import Exercise, Workout, WorkoutExercise, DailyLog


@admin.action(description="Mark selected as approved")
def approve_items(modeladmin, request, queryset):
    queryset.update(is_approved=True)

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('name', 'muscle_group', 'equipment', 'is_approved', 'created_by')
    list_filter = ('is_approved', 'muscle_group')
    search_fields = ('name', 'muscle_group')
    actions = [approve_items]


class WorkoutExerciseInline(admin.TabularInline):
    model = WorkoutExercise
    extra = 1


@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ('name', 'difficulty', 'total_time_minutes', 'category', 'is_approved', 'created_by', 'created_at')
    list_filter = ('is_approved', 'difficulty', 'category')
    search_fields = ('name', 'description')
    inlines = [WorkoutExerciseInline]
    actions = [approve_items]


@admin.register(WorkoutExercise)
class WorkoutExerciseAdmin(admin.ModelAdmin):
    list_display = ('workout', 'order', 'exercise', 'sets', 'reps', 'duration_seconds')

@admin.register(DailyLog)
class DailyLogAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'date',
        'sleep_hours',
        'fasting_hours',
        'calories',
        'workouts_display',
        'workout_completed',
    )
    list_filter = ('user', 'date', 'workout_completed')

    def workouts_display(self, obj):
        """
        Show a comma-separated list of workouts for this day in the admin list.
        """
        names = [w.name for w in obj.workouts.all()]
        return ", ".join(names) if names else "-"
    workouts_display.short_description = "Workouts"
