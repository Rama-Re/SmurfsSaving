from studentModel.views import *
import re
import numpy as np
import pandas as pd
from .serializers import *
from django.db.models import Count, F, Sum, Q
from .models import Operator, Keyword, GeneralConcept

required_concepts = {'الأساسيات': [],
                     'أنواع البيانات': ['الأساسيات'],
                     'المتغيرات': ['الأساسيات'],
                     'التعامل مع الأعداد': ['أنواع البيانات', 'المتغيرات', 'الأساسيات'],
                     'التعامل مع النصوص': ['أنواع البيانات', 'المتغيرات', 'الأساسيات'],
                     'العوامل': ['أنواع البيانات', 'المتغيرات', 'الأساسيات'],
                     'المصفوفات': ['أنواع البيانات', 'المتغيرات', 'الأساسيات'],
                     'الدوال': ['أنواع البيانات', 'المتغيرات', 'الأساسيات'],
                     'الحلقات': ['العوامل', 'أنواع البيانات', 'المتغيرات', 'الأساسيات'],
                     'الشروط': ['العوامل', 'أنواع البيانات', 'المتغيرات', 'الأساسيات']}

university_path = {'الأساسيات': 1,
                   'أنواع البيانات': 2,
                   'المتغيرات': 3,
                   'التعامل مع الأعداد': 4,
                   'التعامل مع النصوص': 5,
                   'العوامل': 6,
                   'المصفوفات': 10,
                   'الدوال': 9,
                   'الحلقات': 8,
                   'الشروط': 7}


class GeneralConcepts(APIView):
    def get(self, request):
        student_profile = get_profile(request)

        generalConcepts = GeneralConcept.objects.all()
        serializer = GeneralConceptSerializer(generalConcepts, many=True)
        availability_data = []
        completed = []
        unavailable_data = []
        available = []
        closed = []
        for concept in generalConcepts:
            theoretical_skill = TheoreticalSkill.objects.filter(student=student_profile, generalConcept=concept).first()
            availability_data.append(theoretical_skill.availability if theoretical_skill else False)

        for data, availability in zip(serializer.data, availability_data):
            data['availability'] = availability
            if student_profile.learning_path == 'university_path':
                data['order'] = university_path[data['name']]
            else:
                data['required'] = required_concepts[data['name']]
            if availability:
                completed.append(data)
            else:
                unavailable_data.append(data)

        if student_profile.learning_path == 'university_path':
            if len(completed) == 0:
                max_order = 1
            else:
                max_order = max(completed, key=lambda x: x['order']) + 1
            available = [x for x in unavailable_data if x['order'] == max_order]
            closed = [x for x in unavailable_data if x['order'] > max_order]
        else:
            completed_names = [x['name'] for x in completed]
            available = [x for x in unavailable_data if all(elem in completed_names for elem in x['required'])]
            closed = [x for x in unavailable_data if not all(elem in completed_names for elem in x['required'])]

        response = {
            'message': 'SUCCESS',
            'data': {
                'completed': completed,
                'available': available,
                'closed': closed
            }
        }
        return Response(response, content_type='application/json; charset=utf-8')


class SubConcepts(APIView):
    def post(self, request):
        student_profile = get_profile(request)
        subConcepts = SubConcept.objects.filter(generalConcept_id=request.data['generalConcept'])
        serializer = SubConceptSerializer(subConcepts, many=True)
        studentKnowledge = student_profile.studentKnowledge.all()
        knowledges = [x.name for x in studentKnowledge]
        completed = [data for data in serializer.data if data['name'] in knowledges]
        uncompleted = [data for data in serializer.data if data['name'] not in knowledges]
        theoreticalSkill = TheoreticalSkill.objects.get(generalConcept=request.data['generalConcept'],
                                                        student=student_profile)
        skill = theoreticalSkill.skill
        response = {
            'message': 'SUCCESS',
            'data': {
                'completed': completed,
                'uncompleted': uncompleted,
                'quiz': {
                    'quiz_state': skill > 60,
                    'quiz_mark': skill
                }
            }
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


def getConceptItems(generalConceptName, itemType):
    concept = GeneralConcept.objects.get(name=generalConceptName)
    items = getattr(concept, itemType).all()
    return items


def line_filter(keyword, operator, line):
    comments_and_strings_pattern = re.compile(r'(//.*|/\*.*?\*/|".*?")')
    # Remove comments and strings from the code line
    code_line_without_comments_and_strings = comments_and_strings_pattern.sub('', line)
    if (operator is None or len(operator) == 0) and (keyword is None or len(keyword) == 0):
        return False
    elif operator is None or len(operator) == 0:
        word_pattern = re.compile(fr'(\b({"|".join(re.escape(k) for k in keyword)})\b)')
    elif keyword is None or len(keyword) == 0:
        word_pattern = re.compile(fr'(?:[{"|".join(re.escape(k) for k in operator)}])')
    else:
        word_pattern = re.compile(
            fr'(?:[{"|".join(re.escape(k) for k in operator)}])|(\b({"|".join(re.escape(k) for k in keyword)})\b)')
    match = word_pattern.search(code_line_without_comments_and_strings)
    return bool(match)


def patternLevel(level, keywords, operators):
    keyword_part = fr'(\b(?:{"|".join(re.escape(k) for k in keywords)})\b)' if keywords is not None else ''
    operator_part = fr'(?:[{"|".join(re.escape(op) for op in operators)}])' if operators is not None else ''
    digit_part = r'\d'
    letter_part = r'[a-zA-Z]'

    if level == 1:
        return re.compile(keyword_part) if keywords is not None else re.compile(operator_part)
    elif level == 2:
        return re.compile(fr'{keyword_part}|{operator_part}|{digit_part}')
    elif level == 4:
        return re.compile('.*')  # Match everything in the line
    else:
        return re.compile(fr'{keyword_part}|{operator_part}|{digit_part}|{letter_part}')


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
        student_profile = get_profile(request)
        general_concept = GeneralConcept.objects.get(name=request.data['generalConcept'])
        available_projects = getAvailableProjects(student_profile, general_concept)
        solved_projects = available_projects.filter(
            studentproject__student=student_profile,
            studentproject__solve_date__isnull=False,
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
        result = {key: map_skill(value) for key, value in
                  eval(hint_serializer.data[0]['required_concept_hint']).items()}
        hint_serializer.data[0]['required_concept_hint'] = str(result)
        response = {
            'message': 'SUCCESS',
            'data': {
                "project": serializer.data,
                "required_concept_hint": hint_serializer.data
            }
        }
        return Response(response, content_type='application/json; charset=utf-8')


def check_availability(obj, student_profile):
    generalConcepts = obj['generalConcepts']
    generalConcepts_names = [name for name in generalConcepts]
    theoretical_skills = TheoreticalSkill.objects.filter(student=student_profile,
                                                         generalConcept__name__in=generalConcepts_names)
    return all(theoretical_skill.availability for theoretical_skill in theoretical_skills)


class GetProjectGeneralConcepts(APIView):
    def get(self, request):
        student_profile = get_profile(request)
        projects_ids = Project.objects.values_list('id', flat=True)
        my_set = []
        for project_id in projects_ids:
            generalConcepts_set = set()
            generalConcepts_set.update(
                Project.objects.filter(id=project_id).values_list('generalConcepts', flat=True).order_by(
                    'generalConcepts'))
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


def returnCommentsAndStrings(endResult, comments, strings):
    for comment_start, comment_end, comment_text in zip(comments["start"], comments["end"], comments["comment"]):
        endResult = endResult[:comment_start] + comment_text + endResult[comment_end:]

    for string_start, string_end, string_text in zip(strings["start"], strings["end"], strings["string"]):
        endResult = endResult[:string_start] + string_text + endResult[string_end:]

    return endResult


class CodeDump(APIView):
    def post(self, request):
        project_id = request.data.get('project_id')
        concept_hint = request.data.get('concept_hint')

        project = Project.objects.filter(id=project_id).first()
        if not project:
            return Response({'message': 'Project not found'}, status=404)

        generalConcepts = eval(concept_hint)
        code = project.correctAnswerSample
        comments, strings = getCommentsAndStrings(code)
        result = code
        concept_keywords = {}
        concept_operators = {}

        for generalConcept, concept_value in generalConcepts.items():
            level = concept_value
            if generalConcept not in concept_keywords:
                concept_keywords[generalConcept] = getConceptItems(generalConcept, 'keywords')
            if generalConcept not in concept_operators:
                concept_operators[generalConcept] = getConceptItems(generalConcept, 'operators')

            keywords = {obj.name for obj in concept_keywords[generalConcept]}
            operators = {obj.name for obj in concept_operators[generalConcept]}
            lines = result.split('\n')

            if not keywords and not operators:
                continue

            code_lines = []
            for line in lines:
                if line_filter(["main"], None, line):
                    code_lines.append(line)
                    continue
                if line_filter(keywords, operators, line):
                    pattern = patternLevel(level, keywords, operators)
                    line = re.sub(pattern, lambda m: '_' * len(m.group()), line)
                code_lines.append(line)

            result = '\n'.join(code_lines)

        endResult = returnCommentsAndStrings(result, comments, strings)

        response = {
            'message': 'SUCCESS',
            'data': {
                "code": code,
                "result": endResult
            }
        }
        return Response(response, content_type='application/json; charset=utf-8')