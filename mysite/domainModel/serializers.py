from rest_framework import serializers
from django.conf import settings
from .models import *
import secrets
from django.core.mail import send_mail


class GeneralConceptSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneralConcept
        fields = ['name']


class SubConceptSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubConcept
        fields = ['name', 'generalConcept_id']


class TheoreticalDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheoreticalData
        fields = ['subheading', 'explanation', 'code', 'output', 'codeExplanation', 'title_id']


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['question', 'correctAnswerSample', 'output', 'explanation', 'hint', 'difficulty']
        extra_kwargs = {
            'correctAnswerSample': {
                'write_only': True
            }
        }

class KeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = ['name']


class OperatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operator
        fields = ['name']
