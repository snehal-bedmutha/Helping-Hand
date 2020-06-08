"""helpinghand URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.conf.urls import url
from django.contrib import admin
from user import views as user_views
from course import views as course_views
from jobs import views as job_view


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('django.contrib.auth.urls')),
    path('signup/', user_views.SignUpView.as_view(), name='signup'),
    path('signup/student/', user_views.StudentSignUpView.as_view(), name='student_signup'),
    path('signup/instructor/', user_views.InstructorSignUpView.as_view(), name='instructor_signup'),
    path('signup/recruiter/', user_views.RecruiterSignUpView.as_view(), name='recruiter_signup'),
    url(r'^user/update/(?P<pk>[\-\w]+)/$', user_views.edit_user, name='profile_update'),
    path('dashboard/', course_views.dashboard, name='dashboard'),
    path('course/<int:c_pk>/',include('course.urls', namespace='course')),
    path('', user_views.home, name='home'),
    path('jobs/', job_view.job, name='job'),
    path('jobs/listing/', job_view.job_listing_page, name='job_listing'),

]
