from django.db import models

class GeneralConcept(models.Model):
    name = models.CharField()

class SubConcept(models.Model):
    name = models.CharField(unique = True)
    generalConcept = models.ForeignKey(GeneralConcept, on_delete=models.CASCADE)

class TheoreticalData(models.Model):
    title = models.ForeignKey(SubConcept, on_delete=models.CASCADE)
    subheading = models.CharField() # this is "section" in the csv file
    explanation = models.TextField()
    code = models.TextField() #try to find another way
    output = models.TextField()
    codeExplanation = models.TextField()




