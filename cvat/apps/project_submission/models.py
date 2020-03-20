
import json

from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import models, transaction


from .eval_detection_voc import compute_submission_map
from .validators import validate_extension_is_json

User = get_user_model()

ground_truth_path="foo"


class ProjectSubmission(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        default=None,
        verbose_name="Group",
        related_name="project_submission"
    )
    submission_json = models.FileField(
        upload_to="submissions/%Y",
        validators=[validate_extension_is_json],
        verbose_name="Submission JSON"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Submission time"
    )
    mean_average_precision = models.FloatField(
        default=None,
        null=True)

    class Meta:
        ordering = ["-mean_average_precision"]
        verbose_name = "Project Submission"
        verbose_name_plural = "Project Submissions"


    def update_mean_average_precision(self):
        with transaction.atomic():
            self.mean_average_precision = compute_submission_map(self.submission_json.path)
            self.save()

    @classmethod
    def update_mean_average_precisions(cls, recompute_all=False):
        if recompute_all:
            submissions = ProjectSubmission.objects.all()
        else:
            submissions = ProjectSubmission.objects.filter(mean_average_precision=None)
        for s in submissions:
            s.update_mean_average_precision()
