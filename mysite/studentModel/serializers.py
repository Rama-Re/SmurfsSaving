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

#
#
#     def send_verification_code_email(self, email, code):
#         subject = 'Verification code'
#         message = f'Your verification code is {code}.'
#         from_email = settings.EMAIL_HOST_USER
#         recipient_list = [email]
#         send_mail(subject, message, from_email, recipient_list)
#
#
#     def create(self, validated_data):
#         password = validated_data.pop('password',None)
#
#         instance = self.Meta.model(**validated_data)
#         gender = ChoiceField(choices=self.GenderChoice)
#         shown_name = ChoiceField(choices=self.ShowNameChoice)
#         if password is not None:
#             instance.set_password(password)
#         instance.gender = gender.to_internal_value(validated_data.pop('gender'))
#         instance.shown_name = shown_name.to_internal_value(validated_data.pop('shown_name'))
#         code = secrets.token_urlsafe(6)
#         self.send_verification_code_email(validated_data['email'], code)
#         instance.verification_code = code
#         instance.is_verified = False
#         instance.save()
#         return instance