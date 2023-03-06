from rest_framework.views import APIView
from rest_framework.response import Response
from .models import *

import jwt, datetime

# from .serializers import UserSerializer
from .serializers import GeneralConceptSerializer, SubConceptSerializer, TheoreticalDataSerializer


class GeneralConcepts(APIView):
    def get(self, request):
        generalConcepts = GeneralConcept.objects.all()
        serializer = GeneralConceptSerializer(generalConcepts, many=True)
        response = {
            'message' : 'SUCCESS',
            'data' : serializer.data
        }
        return Response(response)


class SubConcepts(APIView):
    def get(self, request):
        subConcepts = SubConcept.objects.filter(generalConcept_id=request.data['generalConcept'])
        serializer = SubConceptSerializer(subConcepts, many=True)
        response = {
            'message' : 'SUCCESS',
            'data' : serializer.data
        }
        return Response(response)


class GetTheoreticalData(APIView):
    def get(self, request):
        subConcepts = TheoreticalData.objects.filter(title_id=request.data['subConcept'])
        serializer = TheoreticalDataSerializer(subConcepts, many=True)
        response = {
            'message' : 'SUCCESS',
            'data' : serializer.data
        }
        return Response(response)


def conceptKeywords(subConceptName):
    subConcept = SubConcept.objects.get(name=subConceptName)
    keywords = subConcept.keywords.all()
    return keywords


def conceptOperators(subConceptName):
    subConcept = SubConcept.objects.get(name=subConceptName)
    operators = subConcept.operators.all()
    return operators

