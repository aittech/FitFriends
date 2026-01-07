from django import forms
from django.contrib.auth.models import User
from django_countries.widgets import CountrySelectWidget
from django_countries import countries
from .models import DailyLog, Workout, Exercise, Profile
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm

class WorkoutMultipleChoiceField(forms.ModelMultipleChoiceField):
    """
    Multiple selection of workouts with nice labels.
    """
    def label_from_instance(self, obj):
        # obj.__str__ already gives "Name (25 min)"
        return f"{obj} (by {obj.author_name()})"



class DailyLogForm(forms.ModelForm):
    # Multiple workouts, shown as a scrollable multi-select
    workouts = WorkoutMultipleChoiceField(
        queryset=Workout.objects.filter(is_approved=True).order_by('name'),
        required=False,
        widget=forms.SelectMultiple(
            attrs={
                'class': 'form-select',
                'size': 6,   # how many items visible before scrolling
            }
        ),
    )

    class Meta:
        model = DailyLog
        fields = [
            'date',
            'sleep_hours',
            'fasting_hours',
            'calories',
            'workouts',          # 👈 plural
            'workout_completed',
            'notes',
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)



class UserExerciseSuggestionForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ['name', 'muscle_group', 'equipment', 'description', 'video_url']


class UserWorkoutSuggestionForm(forms.ModelForm):
    class Meta:
        model = Workout
        fields = ['name', 'description', 'total_time_minutes', 'difficulty', 'category', 'video_url']


class SignUpForm(forms.ModelForm):
    """
    Custom signup form: email + password + extra profile fields.
    We use email as the username behind the scenes.
    """
    email = forms.EmailField(label="Email")
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput
    )

    date_of_birth = forms.DateField(
        label="Date of birth",
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    gender = forms.ChoiceField(
        label="Gender",
        choices=Profile.GENDER_CHOICES,
        required=False,
    )

    country = forms.ChoiceField(
        label="Country",
        required=False,
        choices=[('', '---------')] + list(countries),
        widget=CountrySelectWidget()
    )

    display_name = forms.CharField(
        label="Display name",
        max_length=100,
        required=False,
        help_text="Name shown on your profile and leaderboards."
    )

    is_public = forms.BooleanField(
        label="Make my profile public (join leaderboards)",
        required=False,
        initial=False,
    )

    profile_photo = forms.ImageField(
        label="Profile photo",
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control'
        })
    )

    class Meta:
        model = User
        fields = ['email']  # only actual User model fields here

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        email = self.cleaned_data['email'].lower()
        password = self.cleaned_data['password1']

        # Use part before @ as username (and fall back if needed)
        base_username = email.split('@')[0]
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        user = User(username=username, email=email)
        user.set_password(password)

        if commit:
            user.save()
            Profile.objects.create(
                user=user,
                date_of_birth=self.cleaned_data.get('date_of_birth'),
                gender=self.cleaned_data.get('gender') or '',
                country=self.cleaned_data.get('country') or '',
                display_name=self.cleaned_data.get('display_name') or '',
                is_public=self.cleaned_data.get('is_public') or False,
                profile_photo=self.cleaned_data.get('profile_photo'),
            )
        return user

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label="Email",
        widget=forms.TextInput(attrs={"placeholder": "Enter your email address"})
    )
class BootstrapPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs.update({"class": "form-control"})


class BootstrapSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["new_password1"].widget.attrs.update({"class": "form-control"})
        self.fields["new_password2"].widget.attrs.update({"class": "form-control"})
