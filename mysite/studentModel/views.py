from datetime import date, timedelta
from decimal import Decimal

from users.views import *
from django.db.models import Sum
import re
import math
from django.utils import timezone
from .serializers import *
from domainModel.models import *

concepts_level = {'الأساسيات': 1,
                  'أنواع البيانات': 2,
                  'المتغيرات': 2,
                  'التعامل مع الأعداد': 3,
                  'التعامل مع النصوص': 3,
                  'العوامل': 3,
                  'المصفوفات': 3,
                  'الدوال': 3,
                  'الحلقات': 4,
                  'الشروط': 4}


def get_profile(request):
    user_id = userId(request)
    profile = StudentProfile.objects.filter(user_id=user_id).first()
    return profile


class AddPersonality(APIView):
    def post(self, request):
        student_profile = get_profile(request)
        for data in request.data['personalities']:
            personality_name = data['name']
            pp = data['pp']
            personality = Personality.objects.get(name=personality_name)
            student_personality = StudentPersonality.objects.create(studentProfile=student_profile,
                                                                    personality=personality, pp=pp)

        response = {
            'message': 'SUCCESS',
        }
        return Response(response, content_type='application/json; charset=utf-8')


class GetPersonality(APIView):
    def get(self, request):
        try:
            student_profile = get_profile(request)
            personality = StudentPersonality.objects.filter(studentProfile=student_profile)
        except Personality.DoesNotExist:
            response = {
                'message': 'FAILED'
            }
            return Response(response, content_type='application/json; charset=utf-8')

        serializer = StudentPersonalitySerializer(personality, many=True)
        response = {
            'message': 'SUCCESS',
            'data': serializer.data
        }
        return Response(response, content_type='application/json; charset=utf-8')


# class EditPersonality(APIView):
#     def post(self, request):
#         try:
#             studentProfile = get_profile(request)
#             personality = Personality.objects.get(studentProfile=studentProfile)
#             request.data['personality_id'] = personality.id
#             request.data['studentProfile'] = studentProfile.id
#         except Personality.DoesNotExist:
#             response = {
#                 'message': 'FAILED'
#             }
#             return Response(response, content_type='application/json; charset=utf-8')
#
#         serializer = PersonalitiesLettersSerializer(personality, request.data)
#         if serializer.is_valid():
#             serializer.save()
#             response = {
#                 'message': 'SUCCESS',
#                 'data': serializer.data
#             }
#         else:
#             response = {
#                 'message': serializer.errors
#             }
#         return Response(response, content_type='application/json; charset=utf-8')


class AddStudentKnowledge(APIView):
    def post(self, request):
        student_profile = get_profile(request)
        subConcept = SubConcept.objects.get(name=request.data['subConcept'])
        # student_profile.studentKnowledge.add(subConcept)
        # dxp = 5
        # student_profile.xp += dxp
        # student_profile.save()
        if subConcept in student_profile.studentKnowledge.all():
            dxp = 0
        else:
            student_profile.studentKnowledge.add(subConcept)
            dxp = 5
            student_profile.xp += dxp
            student_profile.save()

        response = {
            'message': 'success',
            'added_xp': dxp,
            'new_xp': student_profile.xp
        }
        return Response(response, content_type='application/json; charset=utf-8')


# class EditPracticalSkill(APIView):
#     def post(self, request):
#         profile_id = profileId(request)
#         student_profile = StudentProfile.objects.get(id=profile_id)
#         practical_skill = PracticalSkill.objects.filter(student=student_profile,
#                                                         generalConcept=request.data['generalConcept']).first()
#         practical_skill.skill = request.data['skill']
#         practical_skill.save()
#         response = {
#             'message': 'SUCCESS'
#         }
#         return Response(response)


class AddTheoreticalSkill(APIView):
    def post(self, request):
        student_profile = get_profile(request)
        theoretical_skills = request.data['TheoreticalSkill']
        for data in theoretical_skills:
            # theoretical_skill = TheoreticalSkill.objects.filter(student=student_profile,
            #                                                     generalConcept=data['generalConcept']).first()
            generalConcept = GeneralConcept.objects.filter(name=data['generalConcept']).first()
            theoretical_skill = TheoreticalSkill.objects.create(generalConcept=generalConcept,
                                                                student=student_profile,
                                                                skill=data['skill'],
                                                                self_rate=data['self_rate'],
                                                                availability=data['availability'],
                                                                edit_date=datetime.datetime.now())

            # theoretical_skill.skill = data['skill']
            # theoretical_skill.self_rate = data['self_rate']
            # theoretical_skill.availability = data['availability']
            # theoretical_skill.edit_date = datetime.datetime.now()
            #
            # theoretical_skill.save()
        response = {
            'message': 'SUCCESS'
        }
        return Response(response, content_type='application/json; charset=utf-8')


class AddSolveTrying(APIView):
    def post(self, request):
        student_profile = get_profile(request)
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


# add solve of project

def remove_comments(code):
    code = re.sub(r'\/\/.*', '\\n', code)
    code = re.sub(r'\/\*.*?\*\/', '/* */ \\n', code, flags=re.DOTALL)
    code = code.strip()
    code = re.sub(r'^\s*\n', '', code, flags=re.MULTILINE)
    return code


def detect_concept(code):
    # Regular expressions for different declarations
    declaration_patterns = {
        'الحلقات': r'(?:for\s*\([^;]+;[^;]+;[^)]+\))|(?:while\s*\([^)]+\))|(?:do\s*\{[^}]+\}\s*while\s*\([^)]+\))',
        'الشروط': r'(?:if\s*\([^)]+\)(?:\s*\{[^}]*\})*)|else\s*if\s*\([^)]+\)(?:\s*\{[^}]*\})*|else(?:\s*\{[^}]*\})*|switch\s*\([^)]+\)(?:\s*\{[^}]*\})*',
        'المتغيرات': r'(?: (?:float|char|int|double|bool)\s+)+([a-zA-Z_]\w*)\s*(?:\[[^\]]+\])?(?:\s*=\s*(?:[^,;{}()]+|{.*}))?\s*(?:,|\[|\)|;|\{)',
        'أنواع البيانات': r'\b(?:unsigned|signed|const|static|extern|volatile|register|auto|bool|char|short|int|long|float|double|void|string)\b',
        'الأساسيات': r'(cin\s*>>.*|cout\s*<<|//.* ?|\/\*(.|\n)+?\*\/)',
        'التعامل مع الأعداد': r'\b(?:acos|asin|atan|atan2|ceil|cos|cosh|exp|fabs|floor|fmod|frexp|ldexp|log|log10|modf|pow|sin|sinh|sqrt|tan|tanh)\b',
        'التعامل مع النصوص': r'\b(?: string|"?\.(append|substr|length|empty|insert|replace|find))\b',
        'المصفوفات': r'\b\w+\[\d*\w*\]',
        'العوامل': r'(?:\+=|-=|\*=|/=|<=|>=|==|!=|&&|\|\||%=|<<|>>|>>=|<<=|&=|\|=|\^=|\+\+|--|\+|-|\*|/|%|<|>|&|\||\^|!|~|=)',
        'الدوال': r'\b(?:\w+\s+)+\w+\s*\([^)]*\)\s*(?:const)?\s*(?:{[^}]*})?'
    }
    results = {}

    # Extract declarations for each pattern
    for key, pattern in declaration_patterns.items():
        if (len(re.findall(pattern, code)) != 0):
            results[key] = len(re.findall(pattern, code))
    return results


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


def minmax_mapping(value, min_range=54.60526315789474, max_range=62.769784172661865):
    return ((value - min_range) / (max_range - min_range)) * 100


def student_concepts_difficulty(code):
    code_without_comments = remove_comments(code)
    code_without_strings = re.sub(r'\".*?\"', '', code_without_comments)
    new_code = remove_main_function(code_without_strings)
    detected_concept = detect_concept(new_code)
    result = [{'generalConcepts_name': key, 'generalConcepts_concept_level': concepts_level[key], 'total_count': value}
              for
              key, value in detected_concept.items()]
    total_count_sum = sum(item['total_count'] for item in result)
    general_concepts = result
    difficulty_sum = 0

    for concept in general_concepts:
        difficulty = (concept['generalConcepts_concept_level'] / 4) * (concept['total_count'] / total_count_sum) * 100
        difficulty_sum += difficulty

    return minmax_mapping(difficulty_sum)


def linear_mapping(x, value):
    return (value * x) / 100


def calculate_updated_performance(student_profile, project_performance_required, student_performance_in_current_project,
                                  student_performance, completion_flag=0):
    if completion_flag == 1:
        mapping_student_performance = linear_mapping(5, map_skill(student_performance))
        mapping_project_performance_required = linear_mapping(5, map_skill(project_performance_required))
    else:
        mapping_student_performance = linear_mapping(5, student_performance)
        mapping_project_performance_required = linear_mapping(5, project_performance_required)
    a = 1.0
    b = 0.05
    n = student_profile.studentproject_set.count()
    K = a / (1.0 + b * n)
    print(K)
    p = 1 / (1 + math.exp(-(mapping_student_performance - mapping_project_performance_required))) * 100
    updated_performance = max(0, min(100, student_performance + K * (student_performance_in_current_project - p)))
    updated_project_performance_required = max(0, min(100, project_performance_required + 0.05 * (
            p - student_performance_in_current_project)))

    return updated_performance, updated_project_performance_required, (student_performance_in_current_project - p) / 100


def map_skill(skill):
    if skill <= 30:
        return 1
    elif 30 < skill <= 80:
        return 2
    elif 80 < skill <= 100:
        return 3


class EvaluateRecommend(APIView):
    def post(self, request):
        student_profile = get_profile(request)
        project = Project.objects.get(id=request.data['project_id'])
        recommend = Recommend.objects.filter(student=student_profile).last()
        if (project.id == recommend.project.id):
            recommend.good_recommend = request.data['good_recommend']
            recommend.save()
        response = {
            'message': 'SUCCESS',
        }
        return Response(response, content_type='application/json; charset=utf-8')


class AddProjectSolve(APIView):
    def post(self, request):
        student_profile = get_profile(request)
        project = Project.objects.get(id=request.data['project_id'])
        student_project, created = StudentProject.objects.get_or_create(
            student=student_profile,
            project=project
        )

        # currently const
        problem_xp = 40

        # student current solve
        student_project.solutionCode = request.data['solutionCode']
        student_project.used_concept_difficulty = request.data['used_concept_difficulty']
        student_project.hint_levels = request.data['hint_levels']
        student_project.solve_date = timezone.now()
        student_project.save()
        recommend = Recommend.objects.filter(student=student_profile).last()

        if recommend is not None and student_project.project.id == recommend.project.id and recommend.solved is None:
            recommend.solved = True
            recommend.solve_date = datetime.datetime.now()
            recommend.save()
        elif recommend is not None and student_project.project.id != recommend.project.id and recommend.solved is None:
            recommend.solved = False
            recommend.solve_date = datetime.datetime.now()
            recommend.save()
        solve_tryings = SolveTrying.objects.filter(student_project=student_project)
        student_total_time = solve_tryings.aggregate(total_time=Sum('time'))['total_time']
        if student_total_time is None:
            student_total_time = Decimal(request.data['solve_time'])
        else:
            student_total_time += Decimal(request.data['solve_time'])
        # student performance
        hint_performance = HintPerformance.objects.filter(student=student_profile).last()
        hint_performance_dic = eval(hint_performance.performance)
        hint_performance_dic = {k: hint_performance_dic[k] for k in sorted(hint_performance_dic.keys())}
        time_performances = TimePerformance.objects.filter(student=student_profile).last()
        difficulty_performances = DifficultyPerformance.objects.filter(student=student_profile).last()

        # project required
        time_required = ProjectTime.objects.filter(project=project).last()
        difficulty_required = ProjectDifficulty.objects.filter(project=project).last()
        project_hint = ProjectHint.objects.filter(project=project).last()
        project_hint_required = eval(project_hint.required_concept_hint)
        project_hint_required = {k: project_hint_required[k] for k in sorted(project_hint_required.keys())}
        project_hint_list = list(project_hint_required.values())
        # project_hint_list = [map_skill(value) for value in project_hint_list]
        hint_performance_list = []
        dp_list = []
        for concept in project_hint_required.keys():
            hint_performance_list.append(hint_performance_dic[concept])

        # Evaluating performance and calculating skills.
        # difficulty
        student_current_difficulty = student_concepts_difficulty(request.data['solutionCode'])
        new_performance_difficulty, new_required_difficulty, dp_difficulty = calculate_updated_performance(
            student_profile,
            float(difficulty_required.difficulty),
            student_current_difficulty,
            float(difficulty_performances.performance))
        dp_list.append(dp_difficulty)

        # difficulty_performances.performance = new_performance_difficulty
        # difficulty_performances.save()
        student_difficulty_performances = DifficultyPerformance.objects.create(student=student_profile,
                                                                               performance=new_performance_difficulty,
                                                                               date=datetime.datetime.now())
        # difficulty_required.difficulty = new_required_difficulty
        # difficulty_required.save()
        project_difficulty_required = ProjectDifficulty.objects.create(project=project,
                                                                       difficulty=new_required_difficulty,
                                                                       date=datetime.datetime.now())

        # time
        student_current_time = min(100., (student_total_time / 30) * 100)
        student_current_time = min(100., (float(time_required.time) / float(student_current_time)) * 100)
        new_performance_time, new_required_time, dp_time = calculate_updated_performance(student_profile,
                                                                                         float(time_required.time),
                                                                                         float(student_current_time),
                                                                                         float(
                                                                                             time_performances.performance))
        dp_list.append(dp_time)
        # time_performances.performance = new_performance_time
        # time_performances.save()
        student_time_performances = TimePerformance.objects.create(student=student_profile,
                                                                   performance=new_performance_time,
                                                                   date=datetime.datetime.now())
        # time_required.time = new_required_time
        # time_required.save()
        project_time_required = ProjectTime.objects.create(project=project,
                                                           time=new_required_time,
                                                           date=datetime.datetime.now())

        # hint
        new_performance_list = []
        new_required_list = []

        for concept_hint, student_hint in zip(project_hint_list, hint_performance_list):
            new_performance, new_required, dp = calculate_updated_performance(student_profile,
                                                                              float(concept_hint),
                                                                              student_hint / concept_hint * 100,
                                                                              float(student_hint))
            new_performance_list.append(new_performance)
            new_required_list.append(new_required)
            dp_list.append(dp)
        project_hint_required = {k: i for k, i in zip(project_hint_required.keys(), new_required_list)}
        # project_hint.required_concept_hint = str(project_hint_required)
        # project_hint.save()
        project_project_hint = ProjectHint.objects.create(project=project,
                                                          required_concept_hint=str(project_hint_required),
                                                          date=datetime.datetime.now())
        hint_performance_dic.update(
            (k, i) for k, i in zip(project_hint_required.keys(), new_performance_list) if k in hint_performance_dic)
        # hint_performance.performance = str(hint_performance_dic)
        # hint_performance.save()
        student_hint_performance = HintPerformance.objects.create(student=student_profile,
                                                                  performance=str(hint_performance_dic),
                                                                  date=datetime.datetime.now())

        dxp = problem_xp + problem_xp * (sum(dp_list) / len(dp_list))
        student_profile.xp += round(dxp)
        student_profile.save()
        response = {
            'message': 'SUCCESS',
            'added_xp': round(dxp),
            'new_xp': student_profile.xp
        }
        return Response(response, content_type='application/json; charset=utf-8')


def check_student_answers(answers_dict):
    true_solve_ids = []
    wrong_solve_ids = []
    # Iterate through the dictionary items (question_id, student_answer_id)
    for question_id, student_answer_id in answers_dict.items():
        try:
            # Retrieve the question and its correct answer from the database
            question = QuizzesQuestion.objects.get(id=question_id)
            correct_answer = question.correctAnswer

            # Retrieve the student's answer from the database
            student_answer = QuizzesAnswers.objects.get(id=student_answer_id)

            # Compare the student's answer with the correct answer
            if student_answer.answer == correct_answer:
                true_solve_ids.append(question.id)
            else:
                wrong_solve_ids.append(question.id)

        except (QuizzesQuestion.DoesNotExist, QuizzesAnswers.DoesNotExist):
            # Handle the case where the question or student answer does not exist
            pass

    return true_solve_ids, wrong_solve_ids


class CheckQuizSolve(APIView):
    def post(self, request):
        student_profile = get_profile(request)
        generalConcept = request.data['generalConcept']
        answers_dict = eval(request.data['answers_dict'])

        # Call check_student_answers function
        true_solve_ids, wrong_solve_ids = check_student_answers(answers_dict)
        # Calculate the success rate
        total_questions = len(true_solve_ids) + len(wrong_solve_ids)
        if total_questions > 0:
            success_rate = 100 * len(true_solve_ids) / total_questions
        else:
            success_rate = 0

        max_xp = 60

        # Determine the result
        if success_rate >= 60:
            result = 'pass'
            if TheoreticalSkill.objects.filter(student=student_profile, generalConcept=generalConcept,
                                               skill__gt=0).exists():
                # If the student has already solved the quiz, don't add XP or update the skill
                dxp = 0
            else:
                dxp = max_xp * success_rate / 100
                student_profile.xp += round(dxp)
                student_profile.save()
                theoreticalSkill = TheoreticalSkill.objects.filter(student=student_profile,
                                                                   generalConcept=generalConcept).first()
                theoreticalSkill.edit_date = datetime.datetime.now()
                theoreticalSkill.skill = round(success_rate)
                theoreticalSkill.availability = True
                theoreticalSkill.save()



        else:
            dxp = 0
            result = 'fail'

        # Prepare the response
        response = {
            'message': 'SUCCESS',
            'result': result,
            'success_rate': round(success_rate),
            'xp': {
                'added_xp': round(dxp),
                'new_xp': student_profile.xp
            }
        }
        # # Add question results if the success rate is available
        # if success_rate > 60:
        #     question_results = {}
        #     for question_id in true_solve_ids + wrong_solve_ids:
        #         question_results[question_id] = question_id in true_solve_ids
        #     response['question_results'] = question_results

        return Response(response, content_type='application/json; charset=utf-8')


class EditStreak(APIView):
    def get(self, request):
        student_profile = get_profile(request)
        current_date = timezone.now().today()
        streak = Streak.objects.filter(student_id=student_profile.id, streak_date=current_date).first()

        if streak:
            # If a streak exists, increment the interactions by one
            streak.interactions += 1
            streak.save()
        else:
            # If no streak exists, create a new streak with interactions set to 1
            streak = Streak.objects.create(student=student_profile, interactions=1, streak_date=current_date)

        response = {
            'message': 'SUCCESS',
            # 'date': [StreakSerializer(streak).data]
        }
        return Response(response, content_type='application/json; charset=utf-8')


class GetStreak(APIView):
    def get(self, request):
        student_profile = get_profile(request)
        current_date = date.today()
        streaks = Streak.objects.filter(student=student_profile, interactions__gt=0).order_by('-streak_date')
        current_streak = []
        if streaks:
            latest_streak_date = streaks.latest('streak_date').streak_date
            days_diff = (current_date - latest_streak_date).days
            next_date = latest_streak_date + timedelta(days=1)
            if days_diff <= 1:
                for streak in streaks:
                    print(streak.streak_date)
                    if streak.streak_date == next_date - timedelta(days=1):
                        current_streak.append(streak)
                    else:
                        break
                    next_date = streak.streak_date
        response = {
            'message': 'SUCCESS',
            'data': StreakSerializer(current_streak, many=True).data
        }
        return Response(response, content_type='application/json; charset=utf-8')


class GetProfile(APIView):
    def get(self, request):
        student_profile = get_profile(request)
        if student_profile.user.shown_name == 'username':
            displayed_name = student_profile.user.username
        elif student_profile.user.shown_name == 'nickname':
            displayed_name = student_profile.user.nickname
        else:
            displayed_name = ''

        profile_data = {
            'displayed_name': displayed_name,
            'name': student_profile.user.name,
            'xp': student_profile.xp,
        }
        response = {
            'message': 'SUCCESS',
            'data': profile_data,
        }
        return Response(response, content_type='application/json; charset=utf-8')
