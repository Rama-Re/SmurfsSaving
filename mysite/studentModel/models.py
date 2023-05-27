from django.db import models

# from django.apps import apps
from users.models import *
from domainModel.models import *
# from ..domainModel.models import TheoreticalData, Project


class StudentProfile(models.Model):
    # user = models.OneToOneField(apps.get_model('users','User'), on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    studentKnowledge = models.ManyToManyField(ParagraphData)

class PersonalitiesNames(models.Model):
    personalityName = models.CharField(primary_key=True, max_length=255)

class PersonalitiesLetters(models.Model):
    '''
    each number attached to a letter represents the proportion that student's personality holds from that letter
    '''
    e = models.DecimalField(max_digits=6, decimal_places=2)  # acronym of extraverted
    i = models.DecimalField(max_digits=6, decimal_places=2)  # acronym of introverted

    s = models.DecimalField(max_digits=6, decimal_places=2)  # acronym of observant
    n = models.DecimalField(max_digits=6, decimal_places=2)  # acronym of intuitive

    t = models.DecimalField(max_digits=6, decimal_places=2)  # acronym of thinking
    f = models.DecimalField(max_digits=6, decimal_places=2)  # acronym of feeling

    j = models.DecimalField(max_digits=6, decimal_places=2)  # acronym of judging
    p = models.DecimalField(max_digits=6, decimal_places=2)  # acronym of prospecting

    personalityName = models.ForeignKey(PersonalitiesNames, on_delete=models.CASCADE, null=True)
    studentProfile = models.OneToOneField(StudentProfile, on_delete=models.CASCADE)


class StudentProject(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    # errorsNumber = models.IntegerField()
    # spentTime = models.DurationField()
    solve_date = models.DateTimeField(default=None)
    solutionCode = models.TextField()
    used_concept_difficulty = models.IntegerField()
    hint_levels = models.CharField(max_length=255, default='') # like enuums: easy, medium, hard



class TheoreticalSkill(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    generalConcept = models.ForeignKey(GeneralConcept, on_delete=models.CASCADE)
    skill = models.IntegerField()
    self_rate = models.IntegerField()
    availability = models.BooleanField()


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
    performance = models.DecimalField(max_digits=6, decimal_places=3)
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)


class SolveTrying(models.Model):
    time = models.DecimalField(max_digits=6, decimal_places=3)
    student_project = models.ForeignKey(StudentProject, on_delete=models.CASCADE)



# class StudentKnowledge(models.Model):
#     student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
#     knowledge = models.ForeignKey(TheoreticalData, on_delete=models.CASCADE)
#




