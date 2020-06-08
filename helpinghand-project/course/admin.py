from django.contrib import admin

from .models import *
# Register your models here.
admin.site.register(Course)
admin.site.register(Quiz)
admin.site.register(Videos)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Student)
admin.site.register(TakenQuiz)
admin.site.register(StudentAnswer)

