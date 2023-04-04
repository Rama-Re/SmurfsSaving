from django.db import models


class GeneralConcept(models.Model):
    name = models.CharField(primary_key=True, max_length=255)


class SubConcept(models.Model):
    name = models.CharField(primary_key=True, max_length=255)
    generalConcept = models.ForeignKey(GeneralConcept, on_delete=models.CASCADE)


class Lesson(models.Model):
    name = models.CharField(primary_key=True, max_length=255)
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
    difficulty = models.DecimalField(max_digits=6, decimal_places=3)
    img_src = models.TextField(null=True)
    generalConcepts = models.ManyToManyField(GeneralConcept, related_name='projects')


class Operator(models.Model):
    name = models.CharField(primary_key=True, max_length=6)  # this is "required"
    generalConcepts = models.ManyToManyField(GeneralConcept, related_name='operators')


class Keyword(models.Model):
    name = models.CharField(primary_key=True, max_length=50)  # this is "required"
    generalConcepts = models.ManyToManyField(GeneralConcept, related_name='keywords')

#
# class SubConceptFeatures(models.Model):
#     subConcept = models.ForeignKey(SubConcept, on_delete=models.CASCADE)
#     keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE)
#     operator = models.ForeignKey(Operator, on_delete=models.CASCADE)
