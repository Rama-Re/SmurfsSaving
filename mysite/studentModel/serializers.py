from rest_framework import serializers
from django.conf import settings
from .models import *
import secrets
from django.core.mail import send_mail


class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = ['id', 'user_id']


class PersonalitiesNamesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalitiesNames
        fields = ['personalityName']


class PersonalitiesLettersSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalitiesLetters
        fields = ['e', 'i', 's', 'n', 't', 'f', 'j', 'p', 'personalityName', 'studentProfile']


class StudentProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProject
        fields = ['errorsNumber', 'spentTime', 'solutionCode', 'projectCodeCompletionLevel', 'project_id', 'student_id']


class TheoreticalSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheoreticalSkill
        fields = ['student', 'generalConcept', 'skill']


class PracticalSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = PracticalSkill
        fields = ['student', 'generalConcept', 'skill']

