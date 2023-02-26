from django.db import models

class GeneralConcept(models.Model):
    name = models.CharField(primary_key = True)

class SubConcept(models.Model):
    name = models.CharField(primary_key = True)
    generalConcept = models.ForeignKey(GeneralConcept, on_delete=models.CASCADE)

class TheoreticalData(models.Model):
    title = models.ForeignKey(SubConcept, on_delete=models.CASCADE)
    subheading = models.CharField() # this is "section" in the csv file
    explanation = models.TextField()
    code = models.TextField() #try to find another way to represent it
    output = models.TextField()
    codeExplanation = models.TextField()

class Project(models.Model):
    question = models.TextField() # this is "required" in the csv file
    correctAnswerSample = models.TextField() # this is "code" in the csv file
    output = models.TextField()
    explanation = models.TextField()
    hint = models.TextField(null = True)
    difficulty = models.DecimalField(max_digits= 6, decimal_places=3)
    subConcepts = models.ManyToManyField(SubConcept)





