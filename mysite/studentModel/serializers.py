import datetime

from rest_framework import serializers
from django.conf import settings
from .models import *
import secrets
from django.core.mail import send_mail


class ChoiceField(serializers.ChoiceField):

    def to_representation(self, obj):
        return self._choices[obj]

    def to_internal_value(self, data):
        # To support inserts with the value
        for key, val in self._choices.items():
            if val == data:
                return key
        self.fail('invalid_choice', input=data)


class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = ['id', 'user_id', 'xp', 'learning_path']

    PathChoice = (
        ("university_path", "up"), ("free_path", "fp")
    )

    def create_profile(self, learning_path, user_id):
        student = self.Meta.model()
        learning_path_choice = ChoiceField(choices=self.PathChoice)
        student.user_id = user_id
        student.learning_path = learning_path_choice.to_internal_value(learning_path)
        student.xp = 0
        student.save()

        difficultyPerformance = DifficultyPerformance()
        difficultyPerformance.student = student
        difficultyPerformance.performance = 0
        difficultyPerformance.save()
        timePerformance = TimePerformance()
        timePerformance.student = student
        timePerformance.performance = 0
        timePerformance.save()
        hintPerformance = HintPerformance()
        hintPerformance.student = student
        hintPerformance.performance = "{'الأساسيات': 0, 'أنواع البيانات': 0, 'التعامل مع الأعداد': 0, 'التعامل مع النصوص': 0, 'المصفوفات': 0, 'الدوال': 0,'المتغيرات': 0,'العوامل': 0, 'الحلقات': 0, 'الشروط': 0}"
        hintPerformance.save()

        ### maybe deletehttps://github.com/Rama-Re/gradProject.git
        generalconcepts = GeneralConcept.objects.all()
        for generalconcept in generalconcepts:
            theoretical_skill = TheoreticalSkill.objects.create(generalConcept=generalconcept, student=student,
                                                                skill=0,
                                                                self_rate=0,
                                                                availability=False,
                                                                edit_date=datetime.datetime.now())
            practical_skill = PracticalSkill.objects.create(generalConcept=generalconcept, student=student, skill=0)

        return student


class PersonalitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Personality
        fields = ['name']


class StudentPersonalitySerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentPersonality
        fields = ['id', 'studentProfile', 'personality', 'pp']


class StudentProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProject
        fields = ['used_concept_difficulty', 'hint_levels', 'solutionCode', 'projectCodeCompletionLevel', 'project_id',
                  'student_id']


class TheoreticalSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheoreticalSkill
        fields = ['student', 'generalConcept', 'skill']


class PracticalSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = PracticalSkill
        fields = ['student', 'generalConcept', 'skill']


class DifficultyPerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DifficultyPerformance
        fields = ['student', 'performance']


class TimePerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimePerformance
        fields = ['student', 'performance']


class HintPerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = HintPerformance
        fields = ['student', 'performance']


class SolveTryingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolveTrying
        fields = ['time', 'student_project']


class StreakSerializer(serializers.ModelSerializer):
    class Meta:
        model = Streak
        fields = ['student', 'interactions', 'streak_date']
