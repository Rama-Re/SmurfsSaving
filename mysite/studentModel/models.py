from django.db import models

# from django.apps import apps
from users.models import *
from domainModel.models import *


# from ..domainModel.models import TheoreticalData, Project
class Personality(models.Model):
    name = models.CharField(primary_key=True, max_length=255, unique=True)


class StudentProfile(models.Model):
    # user = models.OneToOneField(apps.get_model('users','User'), on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    xp = models.IntegerField(default=0)
    learning_path = models.CharField(max_length=15, choices=[("up", "university_path"), ("fp", "free_path")],
                                     default="university_path")
    studentKnowledge = models.ManyToManyField(SubConcept)


class StudentPersonality(models.Model):
    studentProfile = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    personality = models.ForeignKey(Personality, on_delete=models.CASCADE)
    pp = models.DecimalField(max_digits=3, decimal_places=2, default=0)


class StudentProject(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    solve_date = models.DateTimeField(null=True)
    solutionCode = models.TextField(null=True)
    used_concept_difficulty = models.IntegerField(null=True)
    hint_levels = models.CharField(max_length=255, default="")  # like enuums: easy, medium, hard


class TheoreticalSkill(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    generalConcept = models.ForeignKey(GeneralConcept, on_delete=models.CASCADE)
    skill = models.IntegerField(default=0)
    self_rate = models.IntegerField(default=0)
    availability = models.BooleanField(default=False)
    edit_date = models.DateTimeField(null=True)


class PracticalSkill(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    generalConcept = models.ForeignKey(GeneralConcept, on_delete=models.CASCADE)
    skill = models.IntegerField(default=0)


class DifficultyPerformance(models.Model):
    performance = models.DecimalField(max_digits=6, decimal_places=3)
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)


class TimePerformance(models.Model):
    performance = models.DecimalField(max_digits=6, decimal_places=3)
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)


class HintPerformance(models.Model):
    performance = models.CharField(primary_key=False, max_length=500,
                                   default="")
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)


class SolveTrying(models.Model):
    time = models.DecimalField(max_digits=6, decimal_places=3)
    student_project = models.ForeignKey(StudentProject, on_delete=models.CASCADE)
