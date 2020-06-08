from django.shortcuts import render
from user.decorators import *
from django.contrib.auth.decorators import login_required


# Create your views here.
from django.shortcuts import render
from .models import job as Job

from .forms import Jobform

# Create your views here.
@login_required
@recruiter_required
def job(request):
    jobs = Job.objects.all()
    jobForm = Jobform()
    if request.method == "POST":
        jobForm = Jobform(request.POST)
        if jobForm.is_valid():
            job_name = jobForm.cleaned_data["job_name"]
            job_description = jobForm.cleaned_data["job_description"]
            job_type = jobForm.cleaned_data["job_type"]
            skills_needed = jobForm.cleaned_data["skills_needed"]
            hourly_pay = jobForm.cleaned_data["hourly_pay"]
            jobForm.save()
    return render(request, 'job_upload.html', {"jobForm":jobForm})


def job_listing_page(request):
    jobs = Job.objects.all()
    return render(request,'job_listing.html',{"jobs":jobs})
