from rest_framework.views import APIView
from rest_framework.response import Response
from .models import *
from studentModel.views import *
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
import re
import jwt, datetime
import numpy as np
# from .serializers import UserSerializer
from .serializers import *


class GeneralConcepts(APIView):
    def get(self, request):
        profile_id = profileId(request)
        generalConcepts = GeneralConcept.objects.all()
        serializer = GeneralConceptSerializer(generalConcepts, many=True)
        availability_data = []
        student_profile = StudentProfile.objects.get(id=profile_id)
        for concept in generalConcepts:
            theoretical_skill = TheoreticalSkill.objects.filter(student=student_profile, generalConcept=concept).first()
            availability_data.append(theoretical_skill.availability if theoretical_skill else False)

        for data, availability in zip(serializer.data, availability_data):
            data['availability'] = availability
        response = {
            'message': 'SUCCESS',
            'data': serializer.data
        }
        return Response(response, content_type='application/json; charset=utf-8')


class SubConcepts(APIView):
    def post(self, request):
        subConcepts = SubConcept.objects.filter(generalConcept_id=request.data['generalConcept'])
        serializer = SubConceptSerializer(subConcepts, many=True)
        response = {
            'message': 'SUCCESS',
            'data': serializer.data
        }
        return Response(response, content_type='application/json; charset=utf-8')


class GetTheoreticalData(APIView):
    def post(self, request):
        titles = Lesson.objects.filter(subConcept_id=request.data['subConcept'])
        paragraph_data_list = ParagraphData.objects.filter(title_id__in=titles).prefetch_related('code_data',
                                                                                                 'example_data')
        serialized_data = TheoreticalDataSerializer(paragraph_data_list, many=True).data
        response = {
            'message': 'SUCCESS',
            'data': serialized_data
        }
        return Response(response, content_type='application/json; charset=utf-8')


class GetQuiz(APIView):
    def post(self, request):
        quiz = QuizzesQuestion.objects.prefetch_related('quizzesanswers_set').filter(
            generalConcept_id=request.data['generalConcept'])
        serializer = QuizzesQuestionSerializer(quiz, many=True)
        response = {
            'message': 'SUCCESS',
            'data': serializer.data
        }
        return Response(response, content_type='application/json; charset=utf-8')


def conceptKeywords(generalConceptName):
    concept = GeneralConcept.objects.get(name=generalConceptName)
    keywords = concept.keywords.all()
    return keywords


def conceptOperators(generalConceptName):
    concept = GeneralConcept.objects.get(name=generalConceptName)
    operators = concept.operators.all()
    return operators


def conceptOfOperator(operator):
    operators = Operator.objects.get(name=operator.name)
    general_concepts_with_operator = operators.generalConcepts.all()
    return general_concepts_with_operator


def conceptOfKeyword(keyword):
    keywords = Keyword.objects.get(name=keyword.name)
    general_concepts_with_keyword = keywords.generalConcepts.all()
    return general_concepts_with_keyword


def line_filter(keyword, operator, line):
    comments_and_strings_pattern = re.compile(r'(//.*|/\*.*?\*/|".*?")')
    # Remove comments and strings from the code line
    code_line_without_comments_and_strings = comments_and_strings_pattern.sub('', line)
    if operator is None and keyword is None:
        return False
    elif operator is None:
        word_pattern = re.compile(fr'(\b({"|".join(re.escape(k) for k in keyword)})\b)')
    elif keyword is None:
        word_pattern = re.compile(fr'(?:[{"|".join(re.escape(k) for k in operator)}])')
    else: word_pattern = re.compile(fr'(?:[{"|".join(re.escape(k) for k in operator)}])|(\b({"|".join(re.escape(k) for k in keyword)})\b)')
    match = word_pattern.search(code_line_without_comments_and_strings)

    return bool(match)


def conceptsInCode(code):
    generalConcepts = set()
    keywords = Keyword.objects.all()
    operators = Operator.objects.all()
    lines = code.split('\n')
    for line in lines:
        for keyword in keywords:
            if line_filter([keyword.name], None, line):
                for generalConcept in conceptOfKeyword(keyword):
                    generalConcepts.add(generalConcept)
        for operator in operators:
            if line_filter(None, [operator.name], line):
                for generalConcept in conceptOfOperator(operator):
                    generalConcepts.add(generalConcept)
    return generalConcepts


def patternLevel(level, keywords, operators):
    if keywords is not None:
        if level == 1:
            return re.compile(fr'(\b(?:{"|".join(re.escape(k) for k in keywords)})\b)')
        elif level == 2:
            if operators is not None:
                return re.compile(fr'((\b(?:{"|".join(re.escape(k) for k in keywords)})\b)|(?:[{"|".join(re.escape(op) for op in operators)}])|\d)')
            else:
                return re.compile(fr'((\b(?:{"|".join(re.escape(k) for k in keywords)})\b)|\d)')
        else:
            if operators is not None:
                return re.compile(fr'((\b(?:{"|".join(re.escape(k) for k in keywords)})\b)|(?:[{"|".join(re.escape(op) for op in operators)}])|\d|[a-zA-Z])')
            else:
                return re.compile(fr'((\b(?:{"|".join(re.escape(k) for k in keywords)})\b)|\d|[a-zA-Z])')

    else:
        if level == 1:
            return re.compile(fr'(?:[{"|".join(re.escape(op) for op in operators)}])')
        elif level == 2:
            return re.compile(fr'((?:[{"|".join(re.escape(op) for op in operators)}])|\d)')
        else:
            return re.compile(fr'((?:[{"|".join(re.escape(op) for op in operators)}])|\d|[a-zA-Z])')


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


class GetProjectsByIds(APIView):
    def post(self, request):
        id_list = request.data['project_ids']
        projects = Project.objects.filter(id__in=id_list)
        serializer = ProjectSerializer(projects, many=True)
        response = {
            'message': 'SUCCESS',
            'data': {
                "projects": serializer.data
            }
        }
        return Response(response)


## Recommendation Start
def getAvailableProjects(student_profile, general_concept):
    general_concepts = GeneralConcept.objects.filter(
        theoreticalskill__availability=True,
        theoreticalskill__student=student_profile
    ).all()

    # Query the projects
    projects = Project.objects.filter(
        generalConcepts=general_concept,
        generalConcepts__theoreticalskill__availability=True,
        generalConcepts__theoreticalskill__student=student_profile,
    ).exclude(
        generalConcepts__in=general_concepts,
        generalConcepts__theoreticalskill__availability=False,
        generalConcepts__theoreticalskill__student=student_profile,
    ).distinct()
    return projects


def euclidean_distance(point1, point2):
    point1 = np.array(point1)
    point2 = np.array(point2)
    distance = np.linalg.norm(point1 - point2)
    return distance


def map_skill(skill):
    if skill <= 17:
        return 1
    elif 17 < skill <= 51:
        return 2
    elif 51 <= skill < 100:
        return 3
    else:
        return 4


class GetRecommendedProjects(APIView):
    def post(self, request):
        profile_id = profileId(request)
        student_profile = StudentProfile.objects.get(id=profile_id)
        general_concept = GeneralConcept.objects.get(name=request.data['generalConcept'])
        available_projects = getAvailableProjects(student_profile, general_concept)
        solved_projects = available_projects.filter(
            studentproject__student = student_profile,
            studentproject__solve_date__isnull = False,
        )
        tried_solving_projects = available_projects.filter(
            studentproject__student=student_profile,
            studentproject__solve_date__isnull=True,
        )
        rest_projects = available_projects.filter(
            studentproject__isnull=True,
        )
        ## recommendation
        # Retrieve the difficulty performance
        difficulty_performance = DifficultyPerformance.objects.get(student=student_profile)
        difficulty_performance = difficulty_performance.performance

        # Retrieve the time performance
        time_performance = TimePerformance.objects.get(student=student_profile)
        time_performance = time_performance.performance

        # Retrieve the hint performance
        hint_performance = HintPerformance.objects.get(student=student_profile)
        hint_performance = hint_performance.performance
        # hint_performance = eval(hint_performance)
        hint_performance = eval("{'الأساسيات': 1, 'أنواع البيانات': 4, 'العوامل': 2}")
        # sorted_hint_dict = {k: hint_performance[k] for k in sorted(hint_performance.keys())}
        recommended_projects = []
        for project in rest_projects:
            project_difficulty = ProjectDifficulty.objects.get(project=project)
            project_time = ProjectTime.objects.get(project=project)
            project_hint = ProjectHint.objects.get(project=project)

            # Access the attributes of each object
            project_difficulty = project_difficulty.difficulty
            project_time = project_time.time
            project_hint = project_hint.required_concept_hint
            project_hint = eval(project_hint)
            project_hint = {k: project_hint[k] for k in sorted(project_hint.keys())}
            project_hint_list = list(project_hint.values())
            project_hint_list = [map_skill(value) for value in project_hint_list]
            project_features = [float(project_difficulty), float(project_time)] + project_hint_list
            hint_list = []
            for concept in project_hint.keys():
                hint_list.append(hint_performance[concept])

            hint_list = [map_skill(value) for value in hint_list]
            student_features = [float(difficulty_performance), float(time_performance)] + hint_list

            print(project_features)
            distance = euclidean_distance(student_features, project_features)
            dist_min = [0] * 2 + [1] * (len(student_features) - 2)
            dist_max = [100] * 2 + [4] * (len(project_features) - 2)
            distance_max = euclidean_distance(dist_min, dist_max)
            S = 100 * (1 - (distance / distance_max))
            print(S)
            recommended_projects.append((project.id, S))
            recommended_projects = sorted(recommended_projects, key=lambda x: x[1], reverse=True)

        # serializer = ProjectSerializer(recommended_projects, many=True)

        response = {
            'message': 'SUCCESS',
            'data': recommended_projects
        }
        return Response(response, content_type='application/json; charset=utf-8')


class GetProject(APIView):
    def post(self, request):
        project = Project.objects.get(id=request.data['project_id'])
        serializer = ProjectSerializer(project)
        hints = ProjectHint.objects.filter(project=project)
        hint_serializer = ProjectHintSerializer(hints, many=True)
        response = {
            'message': 'SUCCESS',
            'data': {
                "project": serializer.data,
                "required_concept_hint": hint_serializer.data
            }
        }
        return Response(response, content_type='application/json; charset=utf-8')


def getGeneralConcepts(subConcepts):
    generalConcepts = set()
    for concept in subConcepts:
        subConcept = SubConcept.objects.filter(name=concept).first()
        generalConcepts.add(subConcept.generalConcept.name)
    return generalConcepts


def check_availability(obj, student_profile):
    generalConcepts = obj['generalConcepts']
    for name in generalConcepts:
        generalConcept = GeneralConcept.objects.filter(name=name).first()
        # practical_skill = PracticalSkill.objects.filter(student=student_profile, generalConcept=generalConcept).first()
        theoretical_skill = TheoreticalSkill.objects.filter(student=student_profile, generalConcept=generalConcept).first()
        # if theoretical_skill['skill']
        if not theoretical_skill.availability:
            return False
    return True


class GetProjectGeneralConcepts(APIView):
    def get(self, request):
        profile_id = profileId(request)
        student_profile = StudentProfile.objects.get(id=profile_id)
        projects_ids = Project.objects.values_list('id', flat=True)
        my_set = []
        for project_id in projects_ids:
            generalConcepts_set = set()
            generalConcepts_set.update(
                Project.objects.filter(id=project_id).values_list('generalConcepts', flat=True).order_by('generalConcepts'))
            index = next((i for i, obj in enumerate(my_set) if obj['generalConcepts'] == generalConcepts_set), None)
            if index is not None:

                # subconcepts set already exists in my_set, add project_id to its related projects_ids
                my_set[index]['project_ids'].append(project_id)
            else:
                # subconcepts set does not exist in my_set, add it and its related project_id
                my_set.append({
                    'generalConcepts': generalConcepts_set,
                    'project_ids': [project_id],
                })
        i = -1
        project_sets = [{'set': obj, 'availability': check_availability(obj=obj, student_profile=student_profile)}
                        for obj in my_set]
        response = {
            'message': 'SUCCESS',
            'data': {
                # "projectConcepts": serializer.data
                "projectConcepts": project_sets
            }
        }
        return Response(response)


def check_practical_skill(skill):
    if skill <= 17:
        return 1
    elif 17 < skill <= 51:
        return 2
    else:
        return 3


def returnCommentsAndStrings(endResult, comments, strings):
    for i in range(len(comments["start"])):
        before = endResult[:comments["start"][i]]
        after = endResult[comments["end"][i]:]
        endResult = before + comments["comment"][i] + after

    for i in range(len(strings["start"])):
        before = endResult[:strings["start"][i]]
        after = endResult[strings["end"][i]:]
        endResult = before + strings["string"][i] + after
    return endResult


class CodeDump(APIView):
    def post(self, request):
        profile_id = profileId(request)
        student_profile = StudentProfile.objects.get(id=profile_id)
        project = Project.objects.get(id=request.data['project_id'])
        generalConcepts = project.generalConcepts.all()
        code = project.correctAnswerSample
        comments, strings = getCommentsAndStrings(code)
        result = code
        # get concepts student know them
        for generalConcept in generalConcepts:
            student_skill = PracticalSkill.objects.filter(student=student_profile, generalConcept=generalConcept).first()

            level = check_practical_skill(student_skill.skill)

            concept_keywords = conceptKeywords(generalConcept.name)
            concept_operators = conceptOperators(generalConcept.name)

            keywords = set([obj.name for obj in concept_keywords])
            operators = set([obj.name for obj in concept_operators])
            if len(operators) == 0: operators = None
            if len(keywords) == 0: keywords = None
            lines = result.split('\n')
            if operators is None and keywords is None:
                continue
            if level == 0:
                continue
            result = ''
            for line in lines:
                if line_filter(["main"], None, line):
                    result += line + '\n'
                    continue
                if line_filter(keywords, operators, line):
                    pattern = patternLevel(level, keywords, operators)
                    line = re.sub(pattern, lambda m: '_' * len(m.group()), line)

                result += line + '\n'

        endResult = result
        endResult = returnCommentsAndStrings(endResult, comments, strings)
        # restore strings and comments

        response = {
            'message': 'SUCCESS',
            'data': {
                "code": code,
                "result": endResult
            }
        }
        return Response(response, content_type='application/json; charset=utf-8')
