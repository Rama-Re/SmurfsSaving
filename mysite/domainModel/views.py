from studentModel.views import *
import re
import numpy as np
import pandas as pd
from .serializers import *
from django.db.models import Count, F, Sum, Q, Value, CharField
from .models import GeneralConcept

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
        # unavailable_data = []
        sorted_data = []
        # available = []
        # closed = []
        for concept in generalConcepts:
            theoretical_skill = TheoreticalSkill.objects.filter(student=student_profile, generalConcept=concept).last()
            availability_data.append(theoretical_skill.availability if theoretical_skill else False)

        for data, availability in zip(serializer.data, availability_data):
            data['availability'] = availability
            if student_profile.learning_path == 'university_path':
                data['order'] = university_path[data['name']]
            else:
                data['required'] = required_concepts[data['name']]
            if availability:
                data['state'] = 'completed'
            else:
                data['state'] = 'unavailable'
        if student_profile.learning_path == 'university_path':
            min_order = min((item['order'] for item in serializer.data if item['state'] != 'completed'), default=0)
            for data in serializer.data:
                if data['state'] == 'unavailable':
                    if data['order'] == min_order:
                        data['state'] = 'available'
                    else:
                        data['state'] = 'closed'
            sorted_data = sorted(serializer.data, key=lambda x: x['order'])
        else:
            completed_names = [x['name'] for x in serializer.data if x['state'] == 'completed']
            for data in serializer.data:
                if data['state'] == 'unavailable':
                    if all(elem in completed_names for elem in data['required']):
                        data['state'] = 'available'
                    else:
                        data['state'] = 'closed'
            sorted_data = sorted(serializer.data, key=lambda x: len(x['required']))

        # if student_profile.learning_path == 'university_path':
        #     if len(completed) == 0:
        #         max_order = 1
        #     else:
        #         max_order = max(completed, key=lambda x: x['order']) + 1
        #     available = [x for x in unavailable_data if x['order'] == max_order]
        #     closed = [x for x in unavailable_data if x['order'] > max_order]
        # else:
        #     completed_names = [x['name'] for x in completed]
        #     available = [x for x in unavailable_data if all(elem in completed_names for elem in x['required'])]
        #     closed = [x for x in unavailable_data if not all(elem in completed_names for elem in x['required'])]

        response = {
            'message': 'SUCCESS',
            'data': sorted_data
        }
        return Response(response, content_type='application/json; charset=utf-8')


class SubConcepts(APIView):
    def post(self, request):
        student_profile = get_profile(request)
        subConcepts = SubConcept.objects.filter(generalConcept_id=request.data['generalConcept']).order_by('order')
        serializer = SubConceptSerializer(subConcepts, many=True)
        studentKnowledge = student_profile.studentKnowledge.all()
        knowledges = [x.name for x in studentKnowledge]
        for data in serializer.data:
            if data['name'] in knowledges:
                data['state'] = 'completed'
            else:
                data['state'] = 'uncompleted'
        theoreticalSkill = TheoreticalSkill.objects.get(generalConcept=request.data['generalConcept'],
                                                        student=student_profile)
        skill = theoreticalSkill.skill
        response = {
            'message': 'SUCCESS',
            'data': {
                'subConcepts': serializer.data,
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
        paragraph_data_list = ParagraphData.objects.filter(title_id__in=titles).order_by('order')
        serialized_data = TheoreticalDataSerializer(paragraph_data_list, many=True).data
        response = {
            'message': 'SUCCESS',
            'data': serialized_data
        }
        return Response(response, content_type='application/json; charset=utf-8')


class GetQuiz(APIView):
    def post(self, request):
        quiz = QuizzesQuestion.objects.filter(generalConcept_id=request.data['generalConcept'])
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


# Recommendation Start
def get_available_projects(student_profile, general_concept):
    # Query the projects
    projects = Project.objects.filter(
        generalConcepts=general_concept,
        generalConcepts__theoreticalskill__availability=True,
        generalConcepts__theoreticalskill__student=student_profile,
    ).distinct()
    projects2 = Project.objects.filter(
        generalConcepts__theoreticalskill__availability=False,
        generalConcepts__theoreticalskill__student=student_profile,
    ).distinct()
    available_projects = projects.exclude(pk__in=projects2)
    return available_projects


def euclidean_distance(point1, point2):
    point1 = np.array(point1)
    point2 = np.array(point2)
    distance = np.linalg.norm(point1 - point2)
    return distance


def map_skill(skill):
    if skill <= 30:
        return 1.
    elif 30 < skill <= 80:
        return 2.
    elif 80 < skill <= 100:
        return 3.
    else:
        return 3.


class GetAllConceptProjects(APIView):
    def post(self, request):
        student_profile = get_profile(request)
        general_concept = GeneralConcept.objects.get(name=request.data['generalConcept'])
        available_projects = get_available_projects(student_profile, general_concept)
        solved_projects = available_projects.filter(
            studentproject__student=student_profile,
            studentproject__solve_date__isnull=False,
        ).annotate(state=Value("solved", output_field=CharField())).values('id', 'state')

        tried_solving_projects = available_projects.filter(
            studentproject__student=student_profile,
            studentproject__solve_date__isnull=True,
        ).annotate(state=Value("tried_solving", output_field=CharField())).values('id', 'state')

        rest_projects = available_projects.filter(
            studentproject__isnull=True,
        ).annotate(state=Value("recommended", output_field=CharField())).values('id', 'state')
        projects = solved_projects.union(tried_solving_projects)
        projects = projects.union(rest_projects)
        response = {
            'message': 'SUCCESS',
            'data':
                projects

        }
        return Response(response, content_type='application/json; charset=utf-8')


class GetRecommendedProjects(APIView):
    def post(self, request):
        student_profile = get_profile(request)
        general_concept = GeneralConcept.objects.get(name=request.data['generalConcept'])
        available_projects = get_available_projects(student_profile, general_concept)
        solved_projects = available_projects.filter(
            studentproject__student=student_profile,
            studentproject__solve_date__isnull=False,
        ).annotate(state=Value("solved", output_field=CharField())).values('id', 'state')

        tried_solving_projects = available_projects.filter(
            studentproject__student=student_profile,
            studentproject__solve_date__isnull=True,
        ).annotate(state=Value("tried_solving", output_field=CharField())).values('id', 'state')

        rest_projects = available_projects.filter(
            studentproject__isnull=True,
        )
        ## recommendation
        # Retrieve the difficulty performance
        difficulty_performance = DifficultyPerformance.objects.filter(student=student_profile).last()
        difficulty_performance = difficulty_performance.performance

        # Retrieve the time performance
        time_performance = TimePerformance.objects.filter(student=student_profile).last()
        time_performance = time_performance.performance

        # Retrieve the hint performance
        hint_performance = HintPerformance.objects.filter(student=student_profile).last()
        hint_performance = hint_performance.performance
        hint_performance = eval(hint_performance)
        harder_projects = []
        easier_projects = []
        # recommended_projects = []
        for project in rest_projects:
            project_difficulty = ProjectDifficulty.objects.filter(project=project).last()
            project_time = ProjectTime.objects.filter(project=project).last()
            project_hint = ProjectHint.objects.filter(project=project).last()

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

            distance = euclidean_distance(student_features, project_features)
            dist_min = [0] * 2 + [1] * (len(student_features) - 2)
            dist_max = [100] * 2 + [4] * (len(project_features) - 2)
            distance_max = euclidean_distance(dist_min, dist_max)
            S = 100 * (1 - (distance / distance_max))
            if float(project_difficulty) >= float(difficulty_performance) or float(project_time) >= float(
                    time_performance):
                harder_projects.append({"project_id": project.id, "similarity": S, "state": 'recommended'})
            else:
                if any(hint > p_hint for hint, p_hint in zip(hint_list, project_hint_list)):
                    harder_projects.append({"project_id": project.id, "similarity": S, "state": 'recommended'})
                else:
                    easier_projects.append({"project_id": project.id, "similarity": S, "state": 'recommended'})

        harder_projects = sorted(harder_projects, key=lambda x: x['similarity'], reverse=True)
        easier_projects = sorted(easier_projects, key=lambda x: x['similarity'], reverse=True)
        recommended_projects = harder_projects + easier_projects

        if len(recommended_projects) > 0:
            project = Project.objects.get(id=recommended_projects[0]['project_id'])
            recommend = Recommend.objects.create(student=student_profile, project=project)

        response = {
            'message': 'SUCCESS',
            'data':
                list(solved_projects.union(tried_solving_projects)) + recommended_projects

        }
        return Response(response, content_type='application/json; charset=utf-8')


class GetProject(APIView):
    def post(self, request):
        project = Project.objects.get(id=request.data['project_id'])
        serializer = ProjectSerializer(project)
        hints = ProjectHint.objects.filter(project=project).last()
        time = ProjectTime.objects.filter(project=project).last()
        serializer_data = serializer.data
        serializer_data['time'] = ProjectTimeSerializer(time).data['time']
        hint_serializer = ProjectHintSerializer(hints)
        result = {key: map_skill(value) for key, value in
                  eval(hint_serializer.data['required_concept_hint']).items()}
        hint_serializer.data['required_concept_hint'] = str(result)
        response = {
            'message': 'SUCCESS',
            'data': {
                "project": serializer_data,
                "required_concept_hint": str(result)
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


def remove_comments(code):
    code = re.sub(r'\/\/.*', '', code)
    code = re.sub(r'\/\*.*?\*\/', '', code, flags=re.DOTALL)
    code = code.strip()
    code = re.sub(r'^\s*\n', '', code, flags=re.MULTILINE)
    return code


def remove_main_function(code):
    lines = code.split('\n')
    new_lines = []
    is_main_function = False

    for line in lines:
        if 'int main(' in line:
            is_main_function = True
            new_lines.append('\n')
            continue
        elif 'return' in line and is_main_function:
            new_lines.append('\n')
            is_main_function = False
            continue

        new_lines.append(line)

    new_code = '\n'.join(new_lines)
    return new_code


def detect_concept(code):
    # Regular expressions for different declarations
    declaration_patterns = {
        'الحلقات': r'((?:for\s*\([^;]+;[^;]+;[^)]+\))|(?:while\s*\([^)]+\))|(?:do\s*\{[^}]+\}\s*while\s*\([^)]+\)))',
        'الشروط': r'((?:if\s*\([^)]+\)(?:\s*\{[^}]*\})*)|else\s*if\s*\([^)]+\)(?:\s*\{[^}]*\})*|else(?:\s*\{[^}]*\})*|switch\s*\([^)]+\)(?:\s*\{[^}]*\})*)',
        # 'المتغيرات': r'( (?:float|char|int|double|bool)\s+([a-zA-Z_]\w*)\s*(?:\[[^\]]+\])?(?:\s*=\s*(?:[^,;{}()]+|{.*}))?\s*(?:,|\[|\)|;|\{))',
        'أنواع البيانات': r'(\b(?:unsigned|signed|const|static|extern|volatile|register|auto|bool|char|short|int|long|float|double|string)[^;\)\(\[\]]*;)',
        'الأساسيات': r'((cin\s*>>.*|cout\s*<<.*|//.* ?|\/\*(.|\n)+?\*\/))',
        'التعامل مع الأعداد': r'(\b(?:acos|asin|atan|atan2|ceil|cos|cosh|exp|fabs|floor|fmod|frexp|ldexp|log|log10|modf|pow|sin|sinh|sqrt|tan|tanh)\b)',
        'التعامل مع النصوص': r'(\b(?:string|"?\.(append|substr|length|empty|insert|replace|find)\([^)]*\)))',
        'المصفوفات': r'(\b((?:unsigned|signed|const|static|extern|volatile|register|auto|bool|char|short|int|long|float|double|string)\s+)?\w+\[\d*\w*\][^;]*;)',
        # 'العوامل': r'((?:\+=|-=|\*=|/=|<=|>=|==|!=|&&|\|\||%=|<<|>>|>>=|<<=|&=|\|=|\^=|\+\+|--|\+|-|\*|/|%|<|>|&|\||\^|!|~|=))',
        'الدوال': r'(\b(?:\w+\s+)+\w+\s*\([^)]*\)\s*(?:const)?\s*(?=\{)|return[^;]*;)'
    }
    results = {}
    code = remove_main_function(code)

    # Extract declarations and positions for each pattern
    for key, pattern in declaration_patterns.items():
        matches = []
        for match in re.finditer(pattern, code):
            start, end = match.span()
            declaration = match.group(0)
            matches.append({'declaration': declaration, 'start': start, 'end': end})
        if len(matches) > 0:
            results[key] = matches

    return results


def replace_characters_with_spaces(input_string):
    # Define the regular expression pattern to match characters that should be replaced with spaces
    pattern = r'[^ \n\t]'

    # Replace matched characters with spaces
    output_string = re.sub(pattern, ' ', input_string)

    return output_string


def get_level_re(concept, level):
    keywords_to_preserve = []
    operators_to_preserve = []

    if level == 2:
        if concept == 'الأساسيات' or concept == 'أنواع البيانات':
            keywords_to_preserve = ['cout', 'cin', 'endl', 'unsigned', 'signed', 'const', 'static', 'bool', 'char',
                                    'short', 'int', 'long',
                                    'float', 'double', 'long long', 'string']

        if concept == 'التعامل مع الأعداد' or concept == 'التعامل مع النصوص':
            keywords_to_preserve = ['acos', 'asin', 'atan', 'atan2', 'ceil', 'cos', 'cosh', 'exp', 'fabs',
                                    'floor', 'fmod', 'frexp', 'ldexp', 'log', 'log10', 'modf', 'pow', 'sin', 'sinh',
                                    'sqrt', 'tan', 'tanh',
                                    'append', 'substr', 'length', 'empty', 'insert', 'replace', 'find']

        if concept == 'الشروط' or concept == 'الحلقات':
            keywords_to_preserve = ['if', 'else if', 'else', 'switch', 'case', 'default', 'break', 'continue', 'for',
                                    'while', 'do']

        if concept == 'الدوال':
            keywords_to_preserve = ['unsigned', 'signed', 'const', 'static', 'bool', 'char', 'short', 'int', 'long',
                                    'float', 'double', 'long long', 'string', 'void', 'return']

        if concept == 'المصفوفات':
            keywords_to_preserve = ['unsigned', 'signed', 'const', 'static', 'bool', 'char', 'short', 'int', 'long',
                                    'float', 'double', 'long long', 'string', '[a-zA-Z_].*(?=\[)']

    elif level == 1:
        if concept == 'الأساسيات' or concept == 'أنواع البيانات':
            keywords_to_preserve = ['cout', 'cin', 'endl', 'unsigned', 'signed', 'const', 'static', 'bool', 'char',
                                    'short', 'int', 'long',
                                    'float', 'double', 'long long', 'string']
            operators_to_preserve = ['>>', '<<', '=', ';']

        if concept == 'التعامل مع الأعداد' or concept == 'التعامل مع النصوص':
            keywords_to_preserve = ['acos', 'asin', 'atan', 'atan2', 'ceil', 'cos', 'cosh', 'exp', 'fabs',
                                    'floor', 'fmod', 'frexp', 'ldexp', 'log', 'log10', 'modf', 'pow', 'sin', 'sinh',
                                    'sqrt', 'tan', 'tanh',
                                    'append', 'substr', 'length', 'empty', 'insert', 'replace', 'find']
            operators_to_preserve = ['\(', '\)', '\.', '\,']

        if concept == 'الشروط' or concept == 'الحلقات':
            keywords_to_preserve = ['if', 'else if', 'else', 'switch', 'case', 'default', 'break', 'continue', 'for',
                                    'while', 'do']
            operators_to_preserve = ['>=', '<=', '\!=', '==', '\!', '>', '<', '\&\&', '\|\|']

        if concept == 'الدوال':
            keywords_to_preserve = ['unsigned', 'signed', 'const', 'static', 'bool', 'char', 'short', 'int', 'long',
                                    'float', 'double', 'long long', 'string', 'void']
            operators_to_preserve = ['\(', '\)', '\,', '\{', '\}', '[a-zA-Z_].*(?=\()']

        if concept == 'المصفوفات':
            keywords_to_preserve = ['unsigned', 'signed', 'const', 'static', 'bool', 'char', 'short', 'int', 'long',
                                    'float', 'double', 'long long', 'string', '[a-zA-Z_].*(?=\[)']
            operators_to_preserve = ['\[', '\]', '\[.*\]']

    return keywords_to_preserve, operators_to_preserve


def code_completion(code, concepts, level):
    # Replace concepts with spaces while preserving keywords and operators
    print(concepts)
    for name, concept in concepts.items():
        keywords_to_preserve, operators_to_preserve = get_level_re(name, level[name])
        for match in concept:
            declaration = match['declaration']
            start = match['start']
            end = match['end']
            subcode = code[start:end]
            for keyword in keywords_to_preserve:
                keyword_pattern = re.compile(r'\b' + keyword + r'\b')
                preserved_keywords = keyword_pattern.finditer(declaration)
                for preserved_keyword in preserved_keywords:
                    keyword_start = start + preserved_keyword.start()
                    keyword_end = start + preserved_keyword.end()
                    preserved_keyword_text = preserved_keyword.group()
                    subcode = subcode[:keyword_start - start] + preserved_keyword_text + subcode[keyword_end - start:]

            # Find and preserve operators
            for operator in operators_to_preserve:
                operator_pattern = re.compile(operator)
                preserved_operators = operator_pattern.finditer(declaration)
                for preserved_operator in preserved_operators:
                    operator_start = start + preserved_operator.start()
                    operator_end = start + preserved_operator.end()
                    preserved_operator_text = preserved_operator.group()
                    subcode = subcode[:operator_start - start] + preserved_operator_text + subcode[
                                                                                           operator_end - start:]

            code = code[:start] + subcode + code[end:]

    return code


class CodeComplete(APIView):
    def post(self, request):
        project_id = request.data.get('project_id')
        concept_hint = request.data.get('concept_hint')

        project = Project.objects.filter(id=project_id).first()
        if not project:
            return Response({'message': 'Project not found'}, status=404)

        concept_hint = eval(concept_hint)
        code = project.correctAnswerSample
        code_without_comments = remove_comments(code)
        code_without_strings = re.sub(r'\".*?\"', '', code_without_comments)
        # comments, strings = getCommentsAndStrings(code)
        output_string = replace_characters_with_spaces(code_without_strings)

        concepts = detect_concept(code_without_strings)

        updated_code = code_completion(output_string, concepts, concept_hint)

        response = {
            'message': 'SUCCESS',
            'data': {
                "code": code,
                "result": updated_code
            }
        }
        return Response(response, content_type='application/json; charset=utf-8')


class GetAllProjects(APIView):
    def get(self, request):
        projects = Project.objects.all()
        serializer = ProjectAllDataSerializer(projects, many=True)
        response = {
            'data': serializer.data
        }
        return Response(response, content_type='application/json; charset=utf-8')
