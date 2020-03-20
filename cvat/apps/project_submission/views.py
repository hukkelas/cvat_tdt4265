from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.views import View

from .models import ProjectSubmission
from .forms import ProjectSubmissionForm

User = get_user_model()

class SubmitAnnotation(LoginRequiredMixin, View):
    template = "project_submission/submit_annotation.html"
    form = ProjectSubmissionForm

    def get(self, request):
        return render(request, self.template, {
            'form': self.form(),
        })
    def post(self, request):
        submission_form = self.form(request.POST)
        if submission_form.is_valid():
            submission = submission_form.save(commit=False)
            submission.user = request.user
            submission.save()
            return redirect("submissions")
        # handle else

class Submissions(LoginRequiredMixin, View):
    template = "project_submission/submissions.html"

    def get(self, request):
        return render(request, self.template, {
            'submissions': ProjectSubmission.objects.all()
        })
