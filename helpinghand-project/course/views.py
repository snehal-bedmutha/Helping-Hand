from django.shortcuts import HttpResponseRedirect,render, redirect, get_object_or_404
from  django.forms import formset_factory
from .forms import *
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from user.decorators import student_required, instructor_required
from django.contrib import messages
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,UpdateView)
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.db.models import Count, Avg
from django.forms import inlineformset_factory
from user.models import User
from .models import *
from speech2text.speech2text import transcription
from jobs.views import job as job

@login_required
def dashboard(request):
    user = User.objects.get(id=request.user.id)
    if user.is_student:
        return student_dashboard(request)
    else:
        if user.is_instructor:
            return instructor_dashboard(request)
        else:
            if user.is_recruiter:
                return job(request)
            else:
                return HttpResponseRedirect('/login')

@login_required
@student_required
def student_dashboard(request):
    user_profile = Student.objects.get(user_id=request.user.id)
    enrolled_course = user_profile.enrolled_courses.all().values_list('name', flat=True)
    available_courses = list(Course.objects.exclude(name__in=enrolled_course).values_list('name', flat=True))
    #print("enrolled_course -------- ",enrolled_course)
    #print("available_courses ------- ", available_courses)
    available_formset = []
    enrolled_formset = []
    for course in available_courses:
        available_formset.append(EnrollForm(initial={"name":course},prefix=course))
    for course in enrolled_course:
        enrolled_formset.append(EnrollForm(initial={"name":course, "course_id": Course.objects.get(name=course).pk },prefix=course))
    if request.method == 'POST':
        course = list(request.POST)[1].split("-")[0]
        available_form = EnrollForm(request.POST, prefix=course)
        if available_form.is_valid() and course in available_courses:
            name = available_form.cleaned_data["name"]
            request_enroll = Course.objects.get(name=name)
            user_profile.enrolled_courses.add(request_enroll)
            return HttpResponseRedirect('/course/{}'.format(request_enroll.pk))
        enrolled_form = EnrollForm(request.POST, prefix=course)
        if enrolled_form.is_valid() and course in enrolled_course:
            name=enrolled_form.cleaned_data["name"]
            request_unenroll = Course.objects.get(name=name)
            user_profile.enrolled_courses.remove(request_unenroll)
            messages.success(request, 'Successfully unenrolled from course ', name)
            return HttpResponseRedirect('/dashboard')
    return render(request, "course/dashboard.html", {"available_formset":available_formset, "enrolled_formset":enrolled_formset })

@login_required
@instructor_required
def instructor_dashboard(request):
    user_profile = Student.objects.get(user_id=request.user.id)
    enrolled_course = user_profile.enrolled_courses.all()
    form = CourseRegisterForm()
    if request.method == "POST":
        form = CourseRegisterForm(request.POST)
        if form.is_valid():
            name=form.cleaned_data["name"]
            if not Course.objects.filter(name=name).exists():
                user_profile.enrolled_courses.create(name=name)
                messages.success(request,"Course created")
                return HttpResponseRedirect('/dashboard')
            else:
                messages.success(request,"Course with same name exists")
                return HttpResponseRedirect('/dashboard')
    return render(request, 'course/dashboard.html', {"form":form, "enrolled_course":enrolled_course})


@login_required
def course(request,c_pk):
    user = User.objects.get(id=request.user.id)
    if user.is_student:
        return student_course(request,c_pk)
    else:
        if user.is_instructor:
            return instructor_course(request,c_pk)
        else:
            return HttpResponseRedirect('/login')

@login_required
@student_required
def student_course(request,c_pk):
    course_name = Course.objects.get(id=c_pk)
    all_videos = Videos.objects.filter(subject_id=c_pk)
    return render(request, "course/course.html", {"c_pk": c_pk, "course": course_name, "all_videos":all_videos})


@login_required
@instructor_required
def instructor_course(request,c_pk):
    course_name = Course.objects.get(id=c_pk)
    all_current_videos = Videos.objects.filter(owner_id=request.user.id).filter(subject_id=c_pk)
    video_form = VideosForm()
    if request.method == "POST":
        form = VideosForm(request.POST)
        if form.is_valid():
            video = form.save(commit=False)
            name = form.cleaned_data["name"]
            url = form.cleaned_data["url"]
            transcription(name,url)
            file1= open("transcript_"+name+".txt","r+")
            transcript = file1.read()
            video.owner_id = request.user.id
            video.subject_id = c_pk
            video.transcript = transcript
            video.save()
            messages.success(request,"Video added")
            return HttpResponseRedirect('/course/{}'.format(c_pk))
    return render(request, "course/course.html", {"c_pk": c_pk, "course": course_name, "video_form":video_form, "all_current_videos":all_current_videos})




@method_decorator([login_required, instructor_required], name='dispatch')
class InstructorQuizListView(ListView):
    model = Quiz
    ordering = ('name', )
    context_object_name = 'quizzes'
    template_name = 'course/quiz_change_list.html'

    def get_queryset(self):
        queryset = self.request.user.quizzes \
            .select_related('course') \
            .annotate(questions_count=Count('questions', distinct=True)) \
            .annotate(taken_count=Count('taken_quizzes', distinct=True))
        queryset = queryset.filter(course_id=self.request.path.split("/")[2])
        return queryset


@method_decorator([login_required, instructor_required], name='dispatch')
class QuizCreateView(CreateView):
    model = Quiz
    fields = ('name',)
    template_name = 'course/quiz_add_form.html'

    def form_valid(self, form):
        quiz = form.save(commit=False)
        quiz.owner = self.request.user
        quiz.course = Course.objects.get(id=self.request.path.split("/")[2])
        quiz.save()
        messages.success(self.request, 'The quiz was created with success! Go ahead and add some questions now.')
        return redirect('course:quiz_change', self.request.path.split("/")[2], quiz.pk)


@method_decorator([login_required, instructor_required], name='dispatch')
class QuizUpdateView(UpdateView):
    model = Quiz
    fields = ('name', )
    context_object_name = 'quiz'
    template_name = 'course/quiz_change_form.html'

    def get_context_data(self, **kwargs):
        kwargs['questions'] = self.get_object().questions.annotate(answers_count=Count('answers'))
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        '''
        This method is an implicit object-level permission management
        This view will only match the ids of existing quizzes that belongs
        to the logged in user.
        '''
        return self.request.user.quizzes.all()

    def get_success_url(self):
        return reverse('course:quiz_change', kwargs={'pk': self.object.pk, 'c_pk': self.request.path.split("/")[2]})


@method_decorator([login_required, instructor_required], name='dispatch')
class QuizDeleteView(DeleteView):
    model = Quiz
    context_object_name = 'quiz'
    template_name = 'course/quiz_delete_confirm.html'

    def get_success_url(self):
        c_pk = self.kwargs['c_pk']
        print(c_pk)
        return reverse_lazy('course:quiz_change_list', kwargs={'c_pk': self.request.path.split("/")[2]})

    def delete(self, request, *args, **kwargs):
        quiz = self.get_object()
        messages.success(request, 'The quiz %s was deleted with success!' % quiz.name)
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return self.request.user.quizzes.all()


@method_decorator([login_required, instructor_required], name='dispatch')
class QuizResultsView(DetailView):
    model = Quiz
    context_object_name = 'quiz'
    template_name = 'course/quiz_results.html'

    def get_context_data(self, **kwargs):
        quiz = self.get_object()
        taken_quizzes = quiz.taken_quizzes.select_related('student__user').order_by('-date')
        total_taken_quizzes = taken_quizzes.count()
        quiz_score = quiz.taken_quizzes.aggregate(average_score=Avg('score'))
        extra_context = {
            'taken_quizzes': taken_quizzes,
            'total_taken_quizzes': total_taken_quizzes,
            'quiz_score': quiz_score
        }
        kwargs.update(extra_context)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        return self.request.user.quizzes.all()

@login_required
@instructor_required
def question_add(request,c_pk, pk):
    # By filtering the quiz by the url keyword argument `pk` and
    # by the owner, which is the logged in user, we are protecting
    # this view at the object-level. Meaning only the owner of
    # quiz will be able to add questions to it.
    print(c_pk)
    quiz = get_object_or_404(Quiz, pk=pk, owner=request.user)

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
            messages.success(request, 'You may now add answers/options to the question.')
            return redirect('course:question_change', c_pk, quiz.pk, question.pk)
    else:
        form = QuestionForm()

    return render(request, 'course/question_add_form.html', {'quiz': quiz, 'form': form})

@login_required
@instructor_required
def question_change(request, c_pk, quiz_pk, question_pk):
    # Simlar to the `question_add` view, this view is also managing
    # the permissions at object-level. By querying both `quiz` and
    # `question` we are making sure only the owner of the quiz can
    # change its details and also only questions that belongs to this
    # specific quiz can be changed via this url (in cases where the
    # user might have forged/player with the url params.
    quiz = get_object_or_404(Quiz, pk=quiz_pk, owner=request.user)
    question = get_object_or_404(Question, pk=question_pk, quiz=quiz)

    AnswerFormSet = inlineformset_factory(
        Question,  # parent model
        Answer,  # base model
        formset=BaseAnswerInlineFormSet,
        fields=('text', 'is_correct'),
        min_num=2,
        validate_min=True,
        max_num=10,
        validate_max=True
    )

    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        formset = AnswerFormSet(request.POST, instance=question)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()
            messages.success(request, 'Question and answers saved with success!')
            return redirect('course:quiz_change', c_pk, quiz.pk)
    else:
        form = QuestionForm(instance=question)
        formset = AnswerFormSet(instance=question)

    return render(request, 'course/question_change_form.html', {
        'quiz': quiz,
        'question': question,
        'form': form,
        'formset': formset
    })


@method_decorator([login_required, instructor_required], name='dispatch')
class QuestionDeleteView(DeleteView):
    model = Question
    context_object_name = 'question'
    template_name = 'course/question_delete_confirm.html'
    pk_url_kwarg = 'question_pk'

    def get_context_data(self, **kwargs):
        question = self.get_object()
        kwargs['quiz'] = question.quiz
        return super().get_context_data(**kwargs)

    def delete(self, request, *args, **kwargs):
        question = self.get_object()
        messages.success(request, 'The question %s was deleted with success!' % question.text)
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return Question.objects.filter(quiz__owner=self.request.user)

    def get_success_url(self):
        question = self.get_object()
        return reverse('course:quiz_change', kwargs={'pk': question.quiz_id, 'c_pk': self.request.path.split("/")[2]})


@method_decorator([login_required, student_required], name='dispatch')
class StudentQuizListView(ListView):
    model = Quiz
    ordering = ('name', )
    context_object_name = 'quizzes'
    template_name = 'course/quiz_list.html'

    def get_queryset(self):
        student = self.request.user.student
        student_enrolled_courses = student.enrolled_courses.values_list('pk', flat=True)
        taken_quizzes = student.quizzes.values_list('pk', flat=True)
        queryset = Quiz.objects.filter(course__in=student_enrolled_courses) \
            .exclude(pk__in=taken_quizzes) \
            .annotate(questions_count=Count('questions')) \
            .filter(questions_count__gt=0)
        return queryset


@method_decorator([login_required, student_required], name='dispatch')
class TakenQuizListView(ListView):
    model = TakenQuiz
    context_object_name = 'taken_quizzes'
    template_name = 'course/taken_quiz_list.html'

    def get_queryset(self):
        queryset = self.request.user.student.taken_quizzes \
            .select_related('quiz', 'quiz__course') \
            .order_by('quiz__name')
        return queryset


@login_required
@student_required
def take_quiz(request, c_pk, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    student = request.user.student

    if student.quizzes.filter(pk=pk).exists():
        return render(request, 'course/taken_quiz.html')

    total_questions = quiz.questions.count()
    unanswered_questions = student.get_unanswered_questions(quiz)
    total_unanswered_questions = unanswered_questions.count()
    progress = 100 - round(((total_unanswered_questions - 1) / total_questions) * 100)
    question = unanswered_questions.first()

    if request.method == 'POST':
        form = TakeQuizForm(question=question, data=request.POST)
        if form.is_valid():
            with transaction.atomic():
                student_answer = form.save(commit=False)
                student_answer.student = student
                student_answer.save()
                if student.get_unanswered_questions(quiz).exists():
                    return redirect('course:take_quiz', c_pk, pk)
                else:
                    correct_answers = student.quiz_answers.filter(answer__question__quiz=quiz, answer__is_correct=True).count()
                    score = round((correct_answers / total_questions) * 100.0, 2)
                    TakenQuiz.objects.create(student=student, quiz=quiz, score=score)
                    if score < 50.0:
                        messages.warning(request, 'Better luck next time! Your score for the quiz %s was %s.' % (quiz.name, score))
                    else:
                        messages.success(request, 'Congratulations! You completed the quiz %s with success! You scored %s points.' % (quiz.name, score))
                    return redirect('course:quiz_list', c_pk)
    else:
        form = TakeQuizForm(question=question)

    return render(request, 'course/take_quiz_form.html', {
        'quiz': quiz,
        'question': question,
        'form': form,
        'progress': progress
    })