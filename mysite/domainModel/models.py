from django.db import models

class GeneralConcept(models.Model):
    name = models.CharField(primary_key=True, max_length=255)


class SubConcept(models.Model):
    name = models.CharField(primary_key=True, max_length=255)
    generalConcept = models.ForeignKey(GeneralConcept, on_delete=models.CASCADE)


class TheoreticalData(models.Model):
    title = models.ForeignKey(SubConcept, on_delete=models.CASCADE)
    subheading = models.CharField(max_length=255)  # this is "section" in the csv file
    explanation = models.TextField()
    code = models.TextField()  # try to find another way to represent it
    output = models.TextField()
    codeExplanation = models.TextField()


class Project(models.Model):
    question = models.TextField()  # this is "required" in the csv file
    correctAnswerSample = models.TextField()  # this is "code" in the csv file
    output = models.TextField()
    explanation = models.TextField()
    hint = models.TextField(null=True)
    difficulty = models.DecimalField(max_digits=6, decimal_places=3)
    img_src = models.TextField(null=True)
    subConcepts = models.ManyToManyField(SubConcept)


class Operator(models.Model):
    name = models.CharField(primary_key=True, max_length=6)  # this is "required"
    subConcepts = models.ManyToManyField(SubConcept,  related_name='operators')


class Keyword(models.Model):
    name = models.CharField(primary_key=True, max_length=50)  # this is "required"
    subConcepts = models.ManyToManyField(SubConcept,  related_name='keywords')

#
# class SubConceptFeatures(models.Model):
#     subConcept = models.ForeignKey(SubConcept, on_delete=models.CASCADE)
#     keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE)
#     operator = models.ForeignKey(Operator, on_delete=models.CASCADE)
