import datetime

from studentModel.models import *


class GamificationFeature(models.Model):
    feature_name = models.TextField(default='')
    threshold = models.DecimalField(default=0, max_digits=3, decimal_places=2)


class FeaturePersonalityRelationship(models.Model):
    rr = models.DecimalField(default=0,max_digits=3, decimal_places=2)
    personality = models.ForeignKey(Personality, on_delete=models.CASCADE)
    gamificationFeature = models.ForeignKey(GamificationFeature, on_delete=models.CASCADE)


class ToReview(models.Model):
    owner = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    description = models.TextField(default='')
    shared_project = models.ForeignKey(StudentProject, on_delete=models.CASCADE)
    shared_date = models.DateTimeField(default=datetime.datetime.now())


class Reviewed(models.Model):
    reviewer = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    edited_code = models.TextField(default='')
    reviewed_date = models.DateTimeField(default=datetime.datetime.now())
    review = models.ForeignKey(ToReview, on_delete=models.CASCADE)


