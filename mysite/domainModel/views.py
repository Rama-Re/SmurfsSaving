from rest_framework.views import APIView
from rest_framework.response import Response
from .models import *
from studentModel.views import *
import re
import jwt, datetime

# from .serializers import UserSerializer
from .serializers import GeneralConceptSerializer, SubConceptSerializer, TheoreticalDataSerializer


class GeneralConcepts(APIView):
    def get(self, request):
        generalConcepts = GeneralConcept.objects.all()
        serializer = GeneralConceptSerializer(generalConcepts, many=True)
        response = {
            'message': 'SUCCESS',
            'data': serializer.data
        }
        return Response(response)


class SubConcepts(APIView):
    def get(self, request):
        subConcepts = SubConcept.objects.filter(generalConcept_id=request.data['generalConcept'])
        serializer = SubConceptSerializer(subConcepts, many=True)
        response = {
            'message': 'SUCCESS',
            'data': serializer.data
        }
        return Response(response)


class GetTheoreticalData(APIView):
    def get(self, request):
        subConcepts = TheoreticalData.objects.filter(title_id=request.data['subConcept'])
        serializer = TheoreticalDataSerializer(subConcepts, many=True)
        response = {
            'message': 'SUCCESS',
            'data': serializer.data
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


def subConceptOfOperator(operator):
    operators = Operator.objects.get(name=operator.name)
    sub_concepts_with_operator = operators.subConcepts.all()
    return sub_concepts_with_operator


def subConceptOfKeyword(keyword):
    keywords = Keyword.objects.get(name=keyword.name)
    sub_concepts_with_keyword = keywords.subConcepts.all()
    return sub_concepts_with_keyword


def allKeywords():
    keywords = Keyword.objects.all()
    return keywords


def allOperators():
    operators = Operator.objects.all()
    return operators


def line_filter(keyword, operator, line):
    comments_and_strings_pattern = re.compile(r'(//.*|/\*.*?\*/|".*?")')
    # Remove comments and strings from the code line
    code_line_without_comments_and_strings = comments_and_strings_pattern.sub('', line)
    # Define the regular expression to match the word

    if operator is None:
        word_pattern = re.compile(fr'(\b(?:{keyword})\b)')

    if keyword is None:
        word_pattern = re.compile(fr'(?:[{operator}])')
        # word_pattern = re.compile(fr"(?<!\S)({operator})(?!\S)(?!\S*\1)")

    # Search for the word in the code line without comments and strings
    match = word_pattern.search(code_line_without_comments_and_strings)

    return bool(match)


def subConceptsInCode(code):
    subConcepts = set()
    keywords = allKeywords()
    operators = allOperators()
    for line in code:
        for keyword in keywords:
            if line_filter(keyword.name, None, line):
                for subConcept in subConceptOfKeyword(keyword):
                    subConcepts.add(subConcept)
        for operator in operators:
            if line_filter(None, operator.name, line):
                for subConcept in subConceptOfOperator(operator):
                    subConcepts.add(subConcept)
    return subConcepts


def patternLevel(level, keywords, operators):
    if level == 1 and operators is None:
        # return re.compile(fr'(?:[{op}]|\d)')
        return re.compile(fr'(\b(?:{"|".join(re.escape(k) for k in keywords)})\b)')
    if level == 1 and keywords is None:
        return re.compile(fr'(?:[{"|".join(re.escape(op) for op in operators)}])')

    elif level == 2:
        return re.compile(fr'((\b(?:{"|".join(re.escape(k) for k in keywords)})\b)|(?:[{"|".join(re.escape(op) for op in operators)}])|\d)')
    else:
        return re.compile(fr'((\b(?:{"|".join(re.escape(k) for k in keywords)})\b)|(?:[{"|".join(re.escape(op) for op in operators)}])|\d|[a-zA-Z])')


class CodeDump(APIView):
    def get(self, request):
        profile_id = profileId(request)
        student_profile = StudentProfile.objects.filter(id=profile_id).first()
        # Get the subconcepts related to the student's theoretical data
        subconcepts = SubConcept.objects.filter(theoreticaldata__studentprofiles=student_profile).distinct()
        return subconcepts
        # subConcepts = TheoreticalData.objects.filter(title_id=request.data['subConcept'])
        # serializer = TheoreticalDataSerializer(subConcepts, many=True)
        # response = {
        #     'message' : 'SUCCESS',
        #     'data' : serializer.data
        # }
        # return Response(response)
