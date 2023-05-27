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
# class PutPersonality(APIView):
#     def put(self, request):
#         pass


class EditPracticalSkill(APIView):
    def post(self, request):
        profile_id = profileId(request)
        student_profile = StudentProfile.objects.get(id=profile_id)
        practical_skill = PracticalSkill.objects.filter(student=student_profile,
                                                        generalConcept=request.data['generalConcept']).first()
        practical_skill.skill = request.data['skill']
        practical_skill.save()
        response = {
            'message': 'SUCCESS'
        }
        return Response(response)


class EditTheoreticalSkill(APIView):
    def post(self, request):
        profile_id = profileId(request)
        student_profile = StudentProfile.objects.get(id=profile_id)
        theoretical_skills = request.data['TheoreticalSkill']
        for data in theoretical_skills:
            theoretical_skill = TheoreticalSkill.objects.filter(student=student_profile,
                                                                generalConcept=data['generalConcept']).first()
            theoretical_skill.skill = data['skill']
            theoretical_skill.self_rate = data['self_rate']
            theoretical_skill.availability = data['availability']
            theoretical_skill.save()
        response = {
            'message': 'SUCCESS'
        }
        return Response(response, content_type='application/json; charset=utf-8')


class AddSolveTrying(APIView):
    def post(self, request):
        profile_id = profileId(request)
        student_profile = StudentProfile.objects.get(id=profile_id)
        project_id = request.data['project_id']
        solve_time = request.data['time']
        student_project, created = StudentProject.objects.get_or_create(student=student_profile, project_id=project_id)
        solve_trying = SolveTrying.objects.create(time=solve_time, student_project=student_project)
        student_project.solutionCode = None
        student_project.used_concept_difficulty = None
        student_project.hint_levels = request.data['hint_levels']
        student_project.solve_date = None
        student_project.save()

        response = {
            'message': 'SUCCESS',
        }
        return Response(response, content_type='application/json; charset=utf-8')
