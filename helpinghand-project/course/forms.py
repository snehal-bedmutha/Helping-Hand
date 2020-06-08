from django.forms import ModelForm, IntegerField
from .models import *
from django.db import transaction
from user.models import UserProfile
from django import forms


class EnrollForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EnrollForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['readonly'] = True

    class Meta:
        model = Course
        fields = ['name',]
    course_id = forms.IntegerField(widget = forms.HiddenInput(), required = False)


class CourseRegisterForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CourseRegisterForm, self).__init__(*args, **kwargs)
        
    class Meta:
        model = Course
        fields = ['name',]


class VideosForm(forms.ModelForm):
    class Meta:
        model = Videos
        fields = ['name','url',]


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ('text', )

class TakeQuizForm(forms.ModelForm):
    answer = forms.ModelChoiceField(
        queryset=Answer.objects.none(),
        widget=forms.RadioSelect(),
        required=True,
        empty_label=None)

    class Meta:
        model = StudentAnswer
        fields = ('answer', )

    def __init__(self, *args, **kwargs):
        question = kwargs.pop('question')
        super().__init__(*args, **kwargs)
        self.fields['answer'].queryset = question.answers.order_by('text')


class BaseAnswerInlineFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()

        has_one_correct_answer = False
        for form in self.forms:
            if not form.cleaned_data.get('DELETE', False):
                if form.cleaned_data.get('is_correct', False):
                    has_one_correct_answer = True
                    break
        if not has_one_correct_answer:
            raise ValidationError('Mark at least one answer as correct.', code='no_correct_answer')