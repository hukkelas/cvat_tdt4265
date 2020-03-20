

from django.contrib.auth import get_user_model
from django.forms import ModelForm

from .models import ProjectSubmission

User = get_user_model()

class ProjectSubmissionForm(ModelForm):
    class Meta:
        model=ProjectSubmission
        exclude=["user", "timestamp", "mean_average_precision"]
