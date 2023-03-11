from rest_framework.views import APIView
from rest_framework.response import Response
from .models import *
from studentModel.views import *
import re
import jwt, datetime

# from .serializers import UserSerializer
from .serializers import *


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
    if operator is None:
        word_pattern = re.compile(fr'(\b(?:{keyword})\b)')

    if keyword is None:
        word_pattern = re.compile(fr'(?:[{operator}])')
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
        return re.compile(fr'(\b(?:{"|".join(re.escape(k) for k in keywords)})\b)')
    if level == 1 and keywords is None:
        return re.compile(fr'(?:[{"|".join(re.escape(op) for op in operators)}])')
    elif level == 2:
        return re.compile(fr'((\b(?:{"|".join(re.escape(k) for k in keywords)})\b)|(?:[{"|".join(re.escape(op) for op in operators)}])|\d)')
    else:
        return re.compile(fr'((\b(?:{"|".join(re.escape(k) for k in keywords)})\b)|(?:[{"|".join(re.escape(op) for op in operators)}])|\d|[a-zA-Z])')

def getCommentsAndStrings(input_string):
    # Define regular expressions for comments and strings
    comment_pattern = r'(\/\/.*$|\/\*[\s\S]*?\*\/)'
    string_pattern = r'(\".*?\"|\'.*?\')'
    comments = {
        "start": [],
        "end": [],
        "comment": []
    }
    strings = {
        "start": [],
        "end": [],
        "string": []
    }
    # Find all comments and strings in the input string and print their start and end positions
    for match in re.finditer(comment_pattern + '|' + string_pattern, input_string, re.MULTILINE):
        if match.group().startswith('//') or match.group().startswith('/*'):
            comments["start"].append(match.start())
            comments["end"].append(match.end())
            comments["comment"].append(match.group())
        else:
            strings["start"].append(match.start())
            strings["end"].append(match.end())
            strings["string"].append(match.group())
    return comments, strings


class GetProject(APIView):
    def get(self, request):
        project = Project.objects.get(id=request.data['project_id'])
        serializer = ProjectSerializer(project)
        response = {
            'message': 'SUCCESS',
            'data': {
                "project": serializer.data
            }
        }
        return Response(response)




class CodeDump(APIView):
    def get(self, request):
        profile_id = profileId(request)
        student_profile = StudentProfile.objects.get(id=profile_id)
        # get concepts student know them
        theoretical_data_objects = student_profile.studentKnowledge.all()
        subconcepts = SubConcept.objects.filter(theoreticaldata__in=theoretical_data_objects).distinct()
        code = Project.objects.get(id=request.data['project_id'])
        code = code.correctAnswerSample
        level = request.data['level']
        print(code)
        keywords = set()
        operators = set()
        for subconcept in subconcepts:
            concept_keywords = conceptKeywords(subconcept.name)
            concept_operators = conceptOperators(subconcept.name)
            keywords.update(set([obj.name for obj in concept_keywords]))
            operators.update(set([obj.name for obj in concept_operators]))
        comments, strings = getCommentsAndStrings(code)
        lines = code.split('\n')
        result = ''

        for line in lines:
            if line_filter("|".join(keywords), None, line):
                pattern = patternLevel(level, keywords, operators)
                line = re.sub(pattern, lambda m: '_' * len(m.group()), line)
            if line_filter(None, "|".join(operators), line):
                pattern = patternLevel(level, keywords, operators)
                line = re.sub(pattern, lambda m: '_' * len(m.group()), line)

            result += line + '\n'

        endResult = result

        # restore strings and comments
        for i in range(len(comments["start"])):
            before = endResult[:comments["start"][i]]
            after = endResult[comments["end"][i]:]
            endResult = before + comments["comment"][i] + after

        for i in range(len(strings["start"])):
            before = endResult[:strings["start"][i]]
            after = endResult[strings["end"][i]:]
            endResult = before + strings["string"][i] + after
        # serializer = KeywordSerializer(subconcepts, many=True)
        print(endResult)
        response = {
            'message': 'SUCCESS',
            'data': {
                "keywords": keywords,
                "result" : endResult
            }
        }
        return Response(response)
