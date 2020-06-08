from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction

from .models import UserProfile, User

from course.models import Course


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class StudentSignUpForm(UserCreationForm):
    # interests = forms.ModelMultipleChoiceField(
    #     queryset=Course.objects.all(),
    #     widget=forms.CheckboxSelectMultiple,
    #     required=True
    # )
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username","first_name","last_name","email")
    
    email = forms.EmailField(max_length=75, required=True)
    first_name = forms.CharField(max_length=75, required=True)
    last_name = forms.CharField(max_length=75, required=True)

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_student = True
        user.save()
        # profile = UserProfile.objects.get(user=user)
        # profile.interests.add(*self.cleaned_data.get('interests'))
        return user


class InstructorSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username","first_name","last_name","email")

    email = forms.EmailField(max_length=75, required=True)
    first_name = forms.CharField(max_length=75, required=True)
    last_name = forms.CharField(max_length=75, required=True)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_instructor = True
        if commit:
            user.save()
        return user


class RecruiterSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username","first_name","last_name","email")

    email = forms.EmailField(max_length=75, required=True)
    first_name = forms.CharField(max_length=75, required=True)
    last_name = forms.CharField(max_length=75, required=True)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_recruiter = True
        if commit:
            user.save()
        return user