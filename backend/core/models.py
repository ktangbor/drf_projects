from django.db import models
from utils.model_abstracts import Model
from django_extensions.db.models import (
    TimeStampedModel,
    ActivatorModel,
)
from django.contrib.auth.models import User
from django_countries.fields import CountryField


PROGRAMMING_SKILLS = ((1, 'C++'),
                      (2, 'Javascript'),
                      (3, 'Python'),
                      (4, 'Java'),
                      (5, 'Lua'),
                      (6, 'Rust'),
                      (7, 'GO'),
                      (8, 'Julia')
                      )


class Profile(
    TimeStampedModel,
    ActivatorModel,
    Model
):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Profiles"

    first_name = models.TextField(verbose_name="First Name")
    last_name = models.TextField(verbose_name="Last Name")
    address = models.TextField(verbose_name="Address")
    email = models.EmailField(verbose_name="Email")
    age = models.IntegerField(default=0, verbose_name="Age")
    country = CountryField(verbose_name="Country")

    def __str__(self):
        return self.user.username


class ProgrammingSkill(models.Model):
    skill = models.CharField(choices=PROGRAMMING_SKILLS, max_length=21)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

