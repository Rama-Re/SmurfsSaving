from rest_framework import serializers
from django.conf import settings

from studentModel.models import StudentProject
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
    code_data = CodeDataSerializer(many=True)
    example_data = ExampleDataSerializer(many=True)

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
        fields = ['id', 'answer']


class QuizzesQuestionSerializer(serializers.ModelSerializer):
    answers = QuizzesAnswersSerializer(many=True, source='quizzesanswers_set')

    class Meta:
        model = QuizzesQuestion
        fields = ['id', 'generalConcept_id', 'question', 'correctAnswer', 'answers']


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'question', 'correctAnswerSample', 'output', 'explanation', 'hint', 'img_src',
                  'generalConcepts']
        # extra_kwargs = {
        #     'correctAnswerSample': {
        #         'write_only': True
        #     }
        # }


class ProjectDifficultySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectDifficulty
        fields = ['difficulty', 'project']


class ProjectDifficultyDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectDifficulty
        fields = ['difficulty', 'date']


class ProjectTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectTime
        fields = ['time', 'project']


class ProjectTimeDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectTime
        fields = ['time', 'date']


class ProjectHintSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectHint
        fields = ['required_concept_hint', 'project']


class ProjectHintDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectHint
        fields = ['required_concept_hint', 'date']


class ProjectDataSerializer(serializers.ModelSerializer):
    difficulties = ProjectDifficultyDataSerializer(many=True, source='projectdifficulty_set')
    times = ProjectTimeDataSerializer(many=True, source='projecttime_set')
    hints = ProjectHintDataSerializer(many=True, source='projecthint_set')
    solved_count = serializers.SerializerMethodField()
    tried_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ['id', 'difficulties', 'times', 'hints', 'solved_count', 'tried_count']

    def get_solved_count(self, obj):
        solved_projects = StudentProject.objects.filter(project=obj, solve_date__isnull=False)
        solved_data = []
        for project in solved_projects:
            solved_data.append({'solve_date': project.solve_date})
        return solved_data

    def get_tried_count(self, obj):
        return StudentProject.objects.filter(project=obj, solve_date__isnull=True).count()