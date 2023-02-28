from django.db import models
from utils.model_abstracts import Model
from django_extensions.db.models import (
    TimeStampedModel,
    ActivatorModel,
    TitleSlugDescriptionModel
)
from django.contrib.auth.models import User


class Project(
    TimeStampedModel,
    ActivatorModel,
    TitleSlugDescriptionModel,
    Model
):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = 'Project'
        verbose_name_plural = "Projects"
        ordering = ["id"]

    title = models.TextField(verbose_name="Project Name", unique=True)
    max_collaborators = models.IntegerField(default=1)

    # def complete(self, user):
    #     if self.user == user:
    #         self.status = 0
    #         self.save(update_fields=['status'])
    #         return self
    #     else:
    #         return None

    def __str__(self):
        return self.title


class Collaborator(
    TimeStampedModel,
    ActivatorModel,
    Model
):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Collaborator'
        verbose_name_plural = "Collaborators"
        ordering = ["id"]

    def __str__(self):
        return 'Colab' + self.project.title + self.user.username


class Candidate(
    TimeStampedModel,
    ActivatorModel,
    Model
):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    reply_status = models.IntegerField(default=0)  # 0: interested, 1: accepted, 2: rejected

    class Meta:
        verbose_name = 'Candidate'
        verbose_name_plural = "Candidates"
        ordering = ["id"]

    def __str__(self):
        return 'Cand_' + self.project.title + '_' + self.user.username
