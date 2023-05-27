from rest_framework import serializers
from django.conf import settings
from .models import *
import secrets
from django.core.mail import send_mail


class GeneralConceptSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneralConcept
        fields = ['name', 'concept_level']


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


class TheoreticalDataSerializer(serializers.ModelSerializer):
    code_data = CodeDataSerializer(many=True, read_only=True)
    example_data = ExampleDataSerializer(many=True, read_only=True)

    class Meta:
        model = ParagraphData
        fields = ['subheading', 'explanation', 'nb', 'img_src', 'title_id', 'code_data', 'example_data']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.code_data.filter(code='').exists():
            data['code_data'] = []
        if instance.example_data.filter(example='').exists():
            data['example_data'] = []
        return data


class QuizzesAnswersSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizzesAnswers
        fields = ['answer']


class QuizzesQuestionSerializer(serializers.ModelSerializer):
    answers = QuizzesAnswersSerializer(many=True, source='quizzesanswers_set')

    class Meta:
        model = QuizzesQuestion
        fields = ['generalConcept_id', 'question', 'correctAnswer', 'answers']


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'question', 'correctAnswerSample', 'output', 'explanation', 'hint', 'img_src', 'generalConcepts']
        # extra_kwargs = {
        #     'correctAnswerSample': {
        #         'write_only': True
        #     }
        # }


class KeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = ['name', 'generalConcepts']


class ProjectDifficultySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectDifficulty
        fields = ['difficulty', 'project']


class ProjectTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectTime
        fields = ['time', 'project']


class ProjectHintSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectHint
        fields = ['required_concept_hint', 'project']
