import logging


from django.db.models import Max
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.views import View
from django.template import loader

from .models import ProjectSubmission, LeaderboardSettings
from .forms import ProjectSubmissionForm, LeaderboardSettingsForm

User = get_user_model()

logger = logging.getLogger(__name__)

class SubmitAnnotation(LoginRequiredMixin, View):
    """View to submit annotation files for project evaluation
    Supports:
        GET
            No args
        POST
            request.body corresponding to a ProjectSubmissionForm

    Returns:

        render self.template (possibly with form errors displayed)
    """
    template = 'project_submission/submit_annotation.html'
    form = ProjectSubmissionForm

    def get(self, request):
        return render(request, self.template, {
            'form': self.form(),
        })
    def post(self, request):
        submission_form = self.form(request.POST, request.FILES)
        print(request)
        print(request.POST)
        print(request.FILES)
        if submission_form.is_valid():
            submission = submission_form.save(commit=False)
            submission.user = request.user
            submission.is_solution = False
            submission.save()
            # I think this has to be done after save() to ensure that
            # The filefield we try to read has actually been created
            # (But I haven't checked)
            submission.update_mean_average_precision() # also saves after computation.
            return redirect('project_submission:submissions')
        else:
            return render(request, self.template, {
                'form': submission_form
            })

class Submissions(LoginRequiredMixin, View):
    template = 'project_submission/submissions.html'

    def get(self, request):
        return render(request, self.template, {
            'submissions': ProjectSubmission.objects.filter(user=request.user),
        })


class Leaderboard(LoginRequiredMixin, View):
    template = 'project_submission/leaderboard.html'
    form = LeaderboardSettingsForm

    def get(self, request):
        submissions = ProjectSubmission.objects.filter(is_solution=False)
        users_to_show_on_leaderboard = User.objects.filter(id__in=submissions.values('user__id')).select_related('leaderboard_settings').filter(leaderboard_settings__show_on_leaderboard=True)
        users_with_map_annotation = (users_to_show_on_leaderboard
                                     .prefetch_related('project_submissions')
                                     .annotate(map_leaderboard_score
                                               =Max('project_submissions__mean_average_precision_leaderboard'))).order_by('-map_leaderboard_score')

        show_this_group_on_leaderboard = request.user.leaderboard_settings.show_on_leaderboard
        form = self.form(initial={'show_on_leaderboard': show_this_group_on_leaderboard})
        return render(request, self.template, {
            'users_with_map_annotation': users_with_map_annotation,
            'form': form
        })

    def post(self, request):
        settings_form = self.form(request.POST)
        if settings_form.is_valid():
            settings = settings_form.save(commit=False)
            # This is a 1:1 relation so we can't save the form directly
            # Instead, get settings of the user and set the settings according to the form
            show_on_leaderboard = settings.show_on_leaderboard
            user_settings = request.user.leaderboard_settings
            user_settings.show_on_leaderboard = show_on_leaderboard
            user_settings.save()
        return redirect('project_submission:leaderboard')


class FinalScores(LoginRequiredMixin, View):
    template = 'project_submission/final_scores.csv'
    def get(self, request):
        submissions = ProjectSubmission.objects.filter(is_solution=False)
        users = User.objects.filter(id__in=submissions.values('user__id'))
        users_with_map_annotation = (users
                                     .prefetch_related('project_submissions')
                                     .annotate(map_final_score
                                               =Max('project_submissions__mean_average_precision_total'))
                                     .annotate(map_leaderboard_score
                                               =Max('project_submissions__mean_average_precision_leaderboard')))

        response = HttpResponse(content_type='text/csv')
        t = loader.get_template(self.template)
        response.write(t.render({
            'users_with_map_annotation': users_with_map_annotation
        }))
        return response
