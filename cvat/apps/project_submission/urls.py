from django.urls import path, include

from .views import SubmitAnnotation, Submissions, Leaderboard

app_name='project_submission'
urlpatterns = [
    path('', Submissions.as_view(), name='submissions'),
    path('submit/', SubmitAnnotation.as_view(), name='submit_annotation'),
    path('leaderboard/', Leaderboard.as_view(), name='leaderboard')
]
