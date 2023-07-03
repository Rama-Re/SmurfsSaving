import datetime

from rest_framework import serializers
from .models import *


class ChoiceField(serializers.ChoiceField):

    def to_representation(self, obj):
        return self._choices[obj]

    def to_internal_value(self, data):
        # To support inserts with the value
        for key, val in self._choices.items():
            if val == data:
                return key
        self.fail('invalid_choice', input=data)


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


class ChallengeSerializer(serializers.ModelSerializer):
    TargetChoice = (
        ("Theoretical", "Th"), ("XP", "XP"), ("Projects", "P")
    )

    class Meta:
        model = Challenge
        fields = ['challenger', 'challenge_type', 'challenge_target', 'challenge_state', 'challenge_date']
