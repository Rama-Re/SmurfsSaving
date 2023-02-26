from django.db import models
from users.models import User
from domainModel.models import Project, TheoreticalData

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)


class PersonalitiesLetters(models.Model):
    '''
    each number attached to a letter represents the proportion that student's personality holds from that letter
    '''
    e = models.DecimalField()  # acronym of extraverted
    i = models.DecimalField()  # acronym of introverted

    s = models.DecimalField()  # acronym of observant
    n = models.DecimalField()  # acronym of intuitive

    t = models.DecimalField()  # acronym of thinking
    f = models.DecimalField()  # acronym of feeling

    j = models.DecimalField()  # acronym of judging
    p = models.DecimalField()  # acronym of prospecting

    studentProfile = models.OneToOneField(StudentProfile, on_delete=models.CASCADE)

class PersonalitiesNames(models.Model):
    architect = models.ForeignKey(PersonalitiesLetters, on_delete=models.CASCADE, null=True)
    logician = models.ForeignKey(PersonalitiesLetters, on_delete=models.CASCADE, null=True)
    commander = models.ForeignKey(PersonalitiesLetters, on_delete=models.CASCADE, null=True)
    debater = models.ForeignKey(PersonalitiesLetters, on_delete=models.CASCADE, null=True)

    advocate = models.ForeignKey(PersonalitiesLetters, on_delete=models.CASCADE, null=True)
    mediator = models.ForeignKey(PersonalitiesLetters, on_delete=models.CASCADE, null=True)
    protagonist = models.ForeignKey(PersonalitiesLetters, on_delete=models.CASCADE, null=True)
    campaigner = models.ForeignKey(PersonalitiesLetters, on_delete=models.CASCADE, null=True)

    logistician = models.ForeignKey(PersonalitiesLetters, on_delete=models.CASCADE, null=True)
    defender = models.ForeignKey(PersonalitiesLetters, on_delete=models.CASCADE, null=True)
    executive = models.ForeignKey(PersonalitiesLetters, on_delete=models.CASCADE, null=True)
    consul = models.ForeignKey(PersonalitiesLetters, on_delete=models.CASCADE, null=True)

    virtuoso = models.ForeignKey(PersonalitiesLetters, on_delete=models.CASCADE, null=True)
    adventurer = models.ForeignKey(PersonalitiesLetters, on_delete=models.CASCADE, null=True)
    entrepreneur = models.ForeignKey(PersonalitiesLetters, on_delete=models.CASCADE, null=True)
    entertainer = models.ForeignKey(PersonalitiesLetters, on_delete=models.CASCADE, null=True)

class StudentProject(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    errorsNumber = models.IntegerField()
    spentTime = models.DurationField()
    solutionCode = models.TextField()
    projectCodeCompletionLevel = models.CharField() # to be edited maybe? as enuums: easy, medium, hard

class StudentKnowledge(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    knowledge = models.ForeignKey(TheoreticalData, on_delete=models.CASCADE)







