from django.db import models

# from django.apps import apps
from users.models import *
from domainModel.models import *
# from ..domainModel.models import TheoreticalData, Project


class StudentProfile(models.Model):
    # user = models.OneToOneField(apps.get_model('users','User'), on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    studentKnowledge = models.ManyToManyField(TheoreticalData)

class PersonalitiesNames(models.Model):
    personalityName = models.CharField(max_length=255)
    # architect = models.ForeignKey(PersonalitiesLetters, on_delete=models.CASCADE, null=True)
    # logician = models.ForeignKey(PersonalitiesLetters, on_delete=models.CASCADE, null=True)
    # commander = models.ForeignKey(PersonalitiesLetters, on_delete=models.CASCADE, null=True)
    # debater = models.ForeignKey(PersonalitiesLetters, on_delete=models.CASCADE, null=True)
    #
    # advocate = models.ForeignKey(PersonalitiesLetters, on_delete=models.CASCADE, null=True)
    # mediator = models.ForeignKey(PersonalitiesLetters, on_delete=models.CASCADE, null=True)
    # protagonist = models.ForeignKey(PersonalitiesLetters, on_delete=models.CASCADE, null=True)
    # campaigner = models.ForeignKey(PersonalitiesLetters, on_delete=models.CASCADE, null=True)
    #
    # logistician = models.ForeignKey(PersonalitiesLetters, on_delete=models.CASCADE, null=True)
    # defender = models.ForeignKey(PersonalitiesLetters, on_delete=models.CASCADE, null=True)
    # executive = models.ForeignKey(PersonalitiesLetters, on_delete=models.CASCADE, null=True)
    # consul = models.ForeignKey(PersonalitiesLetters, on_delete=models.CASCADE, null=True)
    #
    # virtuoso = models.ForeignKey(PersonalitiesLetters, on_delete=models.CASCADE, null=True)
    # adventurer = models.ForeignKey(PersonalitiesLetters, on_delete=models.CASCADE, null=True)
    # entrepreneur = models.ForeignKey(PersonalitiesLetters, on_delete=models.CASCADE, null=True)
    # entertainer = models.ForeignKey(PersonalitiesLetters, on_delete=models.CASCADE, null=True)

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

    # personalityName = models.ForeignKey(apps.get_model('domainModel','PersonalitiesNames'), on_delete=models.CASCADE, null=True)
    personalityName = models.ForeignKey(PersonalitiesNames, on_delete=models.CASCADE, null=True)
    studentProfile = models.OneToOneField(StudentProfile, on_delete=models.CASCADE)

class StudentProject(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    errorsNumber = models.IntegerField()
    spentTime = models.DurationField()
    solutionCode = models.TextField()
    projectCodeCompletionLevel = models.IntegerField() # to be edited maybe? as enuums: easy, medium, hard

# class StudentKnowledge(models.Model):
#     student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
#     knowledge = models.ForeignKey(TheoreticalData, on_delete=models.CASCADE)
#




