from rest_framework.views import APIView
from rest_framework.response import Response
from users.models import *
from users.views import *

from .models import *

import jwt, datetime

# from .serializers import UserSerializer
from .serializers import *


def profileId(request):
    user_id = userId(request)
    serializer = StudentProfileSerializer(StudentProfile.objects.filter(user_id=user_id).first())
    return serializer.data.get('id')


class AddPersonality(APIView):
    def post(self, request):
        profile_id = profileId(request)
        # # print(profile_id)
        request.data['studentProfile'] = profile_id
        serializer = PersonalitiesLettersSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response = {
                'message': 'SUCCESS',
                'data': serializer.data
            }
        else:
            response = {
                'message': 'FAILED'
            }
        return Response(response)


class GetPersonality(APIView):
    def get(self, request):
        profile_id = profileId(request)
        personality = PersonalitiesLetters.objects.filter(studentProfile=profile_id).first()
        serializer = PersonalitiesLettersSerializer(personality)
        response = {
            'message': 'SUCCESS',
            'data': serializer.data
        }
        return Response(response)

# edit profile
class PutPersonality(APIView):
    def put(self, request):
        pass
        # profile_id = profileId(request)
        # personality = PersonalitiesLetters.objects.filter(profile_id=profile_id).fiirst()
        # serializer = PersonalitiesLettersSerializer(personality)
        # if serializer.save():
        #     response = {
        #         'message': 'SUCCESS',
        #         'data': serializer.data
        #     }
        # response = {
        #     'message': 'FAILED',
        # }
        # return Response(response)

