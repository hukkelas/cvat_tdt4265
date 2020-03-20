from django.urls import path, include

from .views import SubmitAnnotation, Submissions


urlpatterns = [
    path('', Submissions.as_view(), name="submissions"),
    path('submit/', SubmitAnnotation.as_view(), name="submit_annotation"),
]
