import string

from rest_framework import serializers
from .models import User
from studentModel.models import *
import secrets
from django.core.mail import send_mail
from django.conf import settings


class ChoiceField(serializers.ChoiceField):

    def to_representation(self, obj):
        return self._choices[obj]

    def to_internal_value(self, data):
        # To support inserts with the value
        for key, val in self._choices.items():
            if val == data:
                return key
        self.fail('invalid_choice', input=data)


class UserSerializer(serializers.ModelSerializer):
    GenderChoice = (
        ("Male", "M"), ("Female", "F")
    )
    ShowNameChoice = (
        ("username", "username"), ("nickname", "nickname")
    )

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password', 'username', 'register_year', 'birthday', 'gender', 'nickname',
                  'shown_name']
        # fields = ['id', 'name', 'email', 'password']
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

    def send_verification_code_email(self, email, code):
        subject = 'Verification code'
        message = f'Your verification code is {code}.'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]
        send_mail(subject, message, from_email, recipient_list)

    def generate_numeric_token(self, length):
        characters = string.digits
        token = ''.join(secrets.choice(characters) for _ in range(length))
        return token

    def create(self, validated_data):
        password = validated_data.pop('password', None)

        instance = self.Meta.model(**validated_data)
        gender = ChoiceField(choices=self.GenderChoice)
        shown_name = ChoiceField(choices=self.ShowNameChoice)
        if password is not None:
            instance.set_password(password)
        instance.gender = gender.to_internal_value(validated_data.pop('gender'))
        instance.shown_name = shown_name.to_internal_value(validated_data.pop('shown_name'))
        code = self.generate_numeric_token(8)
        self.send_verification_code_email(validated_data['email'], code)
        instance.verification_code = code
        instance.is_verified = False  # temp just not to need verification every time
        instance.save()
        return instance
