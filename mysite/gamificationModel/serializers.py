import datetime

from rest_framework import serializers
from .models import *


class GamificationFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = GamificationFeature
        fields = ['id', 'feature_name', 'threshold']


class FeaturePersonalityRelationshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeaturePersonalityRelationship
        fields = ['rr', 'personality', 'gamificationFeature']


class ToReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ToReview
        fields = ['owner', 'description', 'shared_project', 'shared_date']


class ReviewedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reviewed
        fields = ['reviewer', 'edited_code', 'reviewed_date']

