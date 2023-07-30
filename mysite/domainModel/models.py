import datetime

from django.db import models


class GeneralConcept(models.Model):
    name = models.CharField(primary_key=True, max_length=255)
    concept_level = models.IntegerField(default=0)


class SubConcept(models.Model):
    name = models.CharField(primary_key=True, max_length=255)
    order = models.IntegerField(default=0)
    generalConcept = models.ForeignKey(GeneralConcept, on_delete=models.CASCADE)


class Lesson(models.Model):
    name = models.CharField(primary_key=True, max_length=255)
    order = models.IntegerField(default=0)
    subConcept = models.ForeignKey(SubConcept, on_delete=models.CASCADE)


class ParagraphData(models.Model):
    title = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    subheading = models.CharField(max_length=255)  # this is "subLesson" in the csv file
    explanation = models.TextField()
    nb = models.TextField(null=True)
    img_src = models.TextField(null=True)


class CodeData(models.Model):
    paragraph = models.ForeignKey(ParagraphData, on_delete=models.CASCADE, related_name='code_data')
    prefix_text = models.TextField()
    code = models.TextField()
    output = models.TextField()
    codeExplanation = models.TextField()


class ExampleData(models.Model):
    paragraph = models.ForeignKey(ParagraphData, on_delete=models.CASCADE, related_name='example_data')
    prefix_text = models.TextField()
    example = models.TextField()


class QuizzesQuestion(models.Model):
    generalConcept = models.ForeignKey(GeneralConcept, on_delete=models.CASCADE)
    question = models.TextField()
    correctAnswer = models.TextField()


class QuizzesAnswers(models.Model):
    question = models.ForeignKey(QuizzesQuestion, on_delete=models.CASCADE)
    answer = models.TextField()


class Project(models.Model):
    question = models.TextField()  # this is "required" in the csv file
    correctAnswerSample = models.TextField()  # this is "code" in the csv file
    output = models.TextField()
    explanation = models.TextField()
    hint = models.TextField(null=True)
    # difficulty = models.DecimalField(max_digits=6, decimal_places=3)
    img_src = models.TextField(null=True)
    generalConcepts = models.ManyToManyField(GeneralConcept, related_name='projects')


class ProjectDifficulty(models.Model):
    difficulty = models.DecimalField(max_digits=6, decimal_places=3)
    date = models.DateTimeField(default=datetime.datetime.now())
    project = models.ForeignKey(Project, on_delete=models.CASCADE)


class ProjectTime(models.Model):
    time = models.DecimalField(max_digits=6, decimal_places=3)
    date = models.DateTimeField(default=datetime.datetime.now())
    project = models.ForeignKey(Project, on_delete=models.CASCADE)


class ProjectHint(models.Model):
    required_concept_hint = models.CharField(primary_key=False, max_length=500, default='')
    date = models.DateTimeField(default=datetime.datetime.now())
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

