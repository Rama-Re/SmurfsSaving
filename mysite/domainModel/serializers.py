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


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['name', 'subConcept_id']


class ParagraphDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParagraphData
        fields = ['subheading', 'explanation', 'nb', 'img_src', 'title_id']


class CodeDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeData
        fields = ['prefix_text', 'code', 'output', 'codeExplanation', 'paragraph_id']


class ExampleDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExampleData
        fields = ['prefix_text', 'example', 'paragraph_id']


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'question', 'correctAnswerSample', 'output', 'explanation', 'hint', 'difficulty', 'img_src']
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
