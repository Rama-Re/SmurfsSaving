from datetime import date
from decimal import Decimal

from users.views import *
from .serializers import *
from domainModel.models import *
from domainModel.views import *
from studentModel.views import *
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError
from django.db.models import F, Case, When, Value, CharField
from django.db.models.functions import Coalesce, TruncDate
from django.db.models import Count

TargetChoice = (
    ("Theoretical", "Th"), ("XP", "XP"), ("Projects", "P")
)


# Create your views here.
class PerformInteraction(APIView):
    def post(self, request):
        student_profile = get_profile(request)
        pp = StudentPersonality.objects.filter(studentProfile=student_profile).distinct()
        # pp = student_profile.studentPersonality.all()
        g = GamificationFeature.objects.get(feature_name=request.data['feature_name'])
        event = request.data['event']
        rr = FeaturePersonalityRelationship.objects.filter(gamificationFeature_id=g.id)
        s = request.data['s']
        for r in rr:
            matching_pp = pp.filter(personality=r.personality).last()
            if event == 'USE':
                updated_pp = min(matching_pp.pp + (1 - matching_pp.pp) * Decimal(s) * r.rr, 1)
                sp = StudentPersonality.objects.create(studentProfile=student_profile, pp=updated_pp,
                                                       personality=matching_pp.personality,
                                                       edit_date=datetime.datetime.now())
                print(matching_pp.personality)
            else:
                updated_pp = max(matching_pp.pp - matching_pp.pp * s * r.rr, 0)
                sp = StudentPersonality.objects.create(studentProfile=student_profile, pp=updated_pp,
                                                       personality=matching_pp.personality,
                                                       edit_date=datetime.datetime.now())
                print("else", matching_pp.personality)
        response = {
            'message': 'Success'
        }
        return Response(response, content_type='application/json; charset=utf-8')


class StudentGamificationFeatures(APIView):
    def get(self, request):
        student_profile = get_profile(request)
        gamification_feature_state = {}
        pp = StudentPersonality.objects.filter(studentProfile=student_profile)
        # pp = student_profile.studentPersonality.all()
        gfs = GamificationFeature.objects.all()
        print(gfs)
        for g in gfs:
            rr = FeaturePersonalityRelationship.objects.filter(gamificationFeature_id=g.id)
            sum_rng_pn = 0
            sum_rng = 0
            for rng in rr:
                pn = pp.filter(personality=rng.personality).last()
                sum_rng_pn += rng.rr * pn.pp
                sum_rng += rng.rr
            score = sum_rng_pn / sum_rng
            gamification_feature_state[g.feature_name] = score > g.threshold

        response = {
            'message': 'Success',
            'data': {
                'gamification_features': gamification_feature_state
            }
        }
        return Response(response, content_type='application/json; charset=utf-8')


class LeaderBoard(APIView):
    def get(self, request):
        student_profile = get_profile(request)
        profiles = StudentProfile.objects.all()
        # Retrieve sorted profiles with xp and username/nickname
        sorted_profiles = StudentProfile.objects.annotate(
            shown_name=Case(
                When(user__shown_name='username', then=F('user__username')),
                When(user__shown_name='nickname', then=F('user__nickname')),
                default=Value(''), output_field=CharField()
            )
        ).order_by('-xp')
        # Retrieve xp and shown_name for each profile
        profile_data = sorted_profiles.values('xp', 'shown_name')
        # Convert profile_data to a list of dictionaries
        data_list = list(profile_data)
        response = {
            'message': 'Success',
            'data': {
                'LeaderBoard': data_list
            }
        }
        return Response(response, content_type='application/json; charset=utf-8')


class GetTimer(APIView):
    def post(self, request):
        student_profile = get_profile(request)
        project = Project.objects.get(id=request.data['project_id'])
        timer = project.projecttime_set.values('time').first()

        response = {
            'message': 'Success',
            'data': {
                'timer': timer['time']
            }
        }
        return Response(response, content_type='application/json; charset=utf-8')


class AddCodeToReview(APIView):
    def post(self, request):
        try:
            student_profile = get_profile(request)
            project_id = request.data.get('project_id')
            description = request.data.get('description')

            if not project_id or not description:
                # raise ValidationError("Missing project_id or description")
                response = {
                    'message': 'Error',
                    'error': "Missing project_id or description"
                }
                return Response(response, status=404, content_type='application/json; charset=utf-8')

            project = Project.objects.get(id=project_id)
            studentProject = StudentProject.objects.get(project=project, student=student_profile)

            to_review = ToReview.objects.create(owner=student_profile, description=description,
                                                shared_project=studentProject,
                                                shared_date=datetime.datetime.now())

            response = {
                'message': 'Success'
            }
            return Response(response, content_type='application/json; charset=utf-8')

        except (Project.DoesNotExist, StudentProject.DoesNotExist) as e:
            error_message = "Project or StudentProject does not exist"
            response = {
                'message': 'Error',
                'error': error_message
            }
            return Response(response, status=404, content_type='application/json; charset=utf-8')

        except Exception as e:
            error_message = str(e)
            response = {
                'message': 'Error',
                'error': error_message
            }
            return Response(response, status=400, content_type='application/json; charset=utf-8')


class AddReview(APIView):
    def post(self, request):
        student_profile = get_profile(request)
        to_review = ToReview.objects.get(id=request.data['to_review_id'])
        review = Reviewed.objects.create(reviewer=student_profile, edited_code=request.data['edited_code'],
                                         review=to_review,
                                         reviewed_date=datetime.datetime.now())
        response = {
            'message': 'Success'
        }
        return Response(response, content_type='application/json; charset=utf-8')


class GetToReviews(APIView):
    def get(self, request):
        student_profile = get_profile(request)
        to_review = ToReview.objects.annotate(num_reviews=Count('reviewed'))

        response_data = []
        for review in to_review:
            review_data = {
                'id': review.id,
                'owner': review.owner.id,
                'description': review.description,
                'shared_project': review.shared_project.id,
                'shared_date': review.shared_date,
                'num_reviews': review.num_reviews
            }
            response_data.append(review_data)

        response = {
            'message': 'Success',
            'data': {
                'reviews': response_data
            }
        }
        return Response(response, content_type='application/json; charset=utf-8')


class GetToReview(APIView):
    def post(self, request):
        to_review_id = request.data['to_review_id']
        try:
            to_review = ToReview.objects.get(id=to_review_id)
        except ToReview.DoesNotExist:
            response = {
                'message': 'ToReview object does not exist.'
            }
            return Response(response, status=404)

        response = {
            'to_review_id': to_review.id,
            'description': to_review.description,
            'project_question': to_review.shared_project.project.question,
            'solution_code': to_review.shared_project.solutionCode,
            'reviewed': []
        }

        reviewed_instances = Reviewed.objects.filter(review=to_review)
        for reviewed in reviewed_instances:
            reviewer = reviewed.reviewer
            if reviewer.user.shown_name == 'username':
                reviewer_name = reviewer.user.username
            else:
                reviewer_name = reviewer.user.nickname

            reviewed_data = {
                'reviewer': reviewer_name,
                'reviewed_date': reviewed.reviewed_date,
                'edited_code': reviewed.edited_code
            }
            response['reviewed'].append(reviewed_data)

        return Response(response, content_type='application/json; charset=utf-8')


class GetMyToReview(APIView):
    def get(self, request):
        student_profile = get_profile(request)
        to_review = ToReview.objects.annotate(num_reviews=Count('reviewed', distinct=True)).filter(
            owner=student_profile)

        response_data = []
        for review in to_review:
            review_data = {
                'id': review.id,
                'owner': review.owner.id,
                'description': review.description,
                'shared_project': review.shared_project.id,
                'shared_date': review.shared_date,
                'num_reviews': review.num_reviews
            }
            response_data.append(review_data)

        response = {
            'message': 'Success',
            'data': {
                'reviews': response_data
            }
        }
        return Response(response, content_type='application/json; charset=utf-8')


class GetMyReviewed(APIView):
    def get(self, request):
        student_profile = get_profile(request)
        to_review = ToReview.objects.annotate(num_reviews=Count('reviewed', distinct=True)).filter(
            reviewed__reviewer=student_profile)

        response_data = []
        for review in to_review:
            review_data = {
                'id': review.id,
                'owner': review.owner.id,
                'description': review.description,
                'shared_project': review.shared_project.id,
                'shared_date': review.shared_date,
                'num_reviews': review.num_reviews
            }
            response_data.append(review_data)

        response = {
            'message': 'Success',
            'data': {
                'reviews': response_data
            }
        }
        return Response(response, content_type='application/json; charset=utf-8')


class GetChallenge(APIView):
    def get(self, request):
        student_profile = get_profile(request)
        challenge_type = ChoiceField(choices=TargetChoice)
        current_date = date.today()
        # Retrieve challenges of the current day
        theoretical_challenge = Challenge.objects.filter(challenger=student_profile, challenge_date=current_date,
                                                         challenge_type='Theoretical').first()
        project_challenge = Challenge.objects.filter(challenger=student_profile, challenge_date=current_date,
                                                     challenge_type='Projects').first()
        xp_challenge = Challenge.objects.filter(challenger=student_profile, challenge_date=current_date,
                                                challenge_type='XP').first()
        if theoretical_challenge is None:
            generalConcepts = GeneralConcept.objects.all()

            serializer = GeneralConceptSerializer(generalConcepts, many=True)
            first_available = None
            availability_data = [TheoreticalSkill.objects.filter
                                 (student=student_profile, generalConcept=concept).first().availability
                                 if TheoreticalSkill.objects.filter(student=student_profile,
                                                                    generalConcept=concept).exists()
                                 else False for concept in generalConcepts]

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
            first_available = next((item for item in sorted_data if item['state'] == 'available'), None)
            challenge_target = ''

            if first_available:
                if student_profile.learning_path == 'university_path':
                    challenge_target = 'أنجز مفهوم ' + first_available['name']
                    print(challenge_target)
                else:
                    challenge_target = 'أنجز مفهوما جديداً'
                    print(challenge_target)
            # else:
            #     # راجع المفهوم يلي عليه اقل عدد مسائل
            print('theoretical_challenge is None')
            challenge = Challenge.objects.get_or_create(
                challenger=student_profile,
                challenge_type=challenge_type.to_internal_value('Th'),
                challenge_target=challenge_target,
                challenge_state=False,
                challenge_date=current_date
            )

        # Projects
        if project_challenge is None:
            projects = StudentProject.objects.filter(solve_date__isnull=False, student=student_profile)
            average_daily_count = 1
            if projects:
                project_counts = projects.annotate(date=TruncDate('solve_date')).values('date').annotate(
                    count=Count('id'))
                num_days = (projects.latest('solve_date').solve_date.date() - projects.earliest(
                    'solve_date').solve_date.date()).days + 1
                average_daily_count = round(sum(count['count'] for count in project_counts) / num_days)

                print(average_daily_count)
            print('project_challenge is None')
            challenge = Challenge.objects.get_or_create(
                challenger=student_profile,
                challenge_type=challenge_type.to_internal_value('P'),
                challenge_target=str(round(average_daily_count)),
                challenge_state=False,
                challenge_date=current_date
            )

            # XP
            # if xp_challenge is None:
            challenge = Challenge.objects.get_or_create(
                challenger=student_profile,
                challenge_type=challenge_type.to_internal_value('XP'),
                challenge_target=str(int(average_daily_count * 40)),
                challenge_state=False,
                challenge_date=current_date
            )
        challenges = Challenge.objects.filter(challenger=student_profile, challenge_date=current_date)

        response = {
            'message': 'Success',
            # 'data': ChallengeSerializer(challenges, many=True).data
        }
        return Response(response, content_type='application/json; charset=utf-8')


class CheckingChallenges(APIView):
    def get(self, request):
        student_profile = get_profile(request)
        # Get the current date
        current_date = date.today()

        # Retrieve challenges of the current day
        theoretical_challenge = Challenge.objects.filter(challenger=student_profile, challenge_date=current_date,
                                                         challenge_type='Theoretical').first()
        project_challenge = Challenge.objects.filter(challenger=student_profile, challenge_date=current_date,
                                                     challenge_type='Projects').first()
        xp_challenge = Challenge.objects.filter(challenger=student_profile, challenge_date=current_date,
                                                challenge_type='XP').first()

        # Retrieve theoretical skills count for the current day
        theoretical_skills = TheoreticalSkill.objects.filter(edit_date__date=current_date,
                                                             student=student_profile, skill__gt=0).count()
        remaining_theoretical_challenge = 0 if theoretical_skills > 0 else 1
        if remaining_theoretical_challenge == 0:
            theoretical_challenge.challenge_state = True
            theoretical_challenge.save()

        # Retrieve student projects count for the current day
        student_projects = StudentProject.objects.filter(solve_date__date=current_date, student=student_profile).count()
        all_project_challenge = int(project_challenge.challenge_target)
        remaining_project_challenge = max(0, all_project_challenge - student_projects)

        if remaining_project_challenge == 0:
            project_challenge.challenge_state = True
            project_challenge.save()

        # XP
        all_xp_challenge = int(xp_challenge.challenge_target)
        remaining_xp_challenge = max(0, all_xp_challenge - student_projects * 40)
        if remaining_xp_challenge == 0:
            xp_challenge.challenge_state = True
            xp_challenge.save()

        response = {
            'message': 'Success',
            'data': [
                {
                    **ChallengeSerializer(theoretical_challenge).data,
                    'remaining': remaining_theoretical_challenge, },
                {
                    **ChallengeSerializer(project_challenge).data,
                    'remaining': remaining_project_challenge},
                {
                    **ChallengeSerializer(xp_challenge).data,
                    'remaining': remaining_xp_challenge}
            ]
        }
        return Response(response, content_type='application/json; charset=utf-8')


class GetMbtiTest(APIView):
    def get(self, request):
        questions = MbtiQuestions.objects.all()
        serializer = MbtiQuestionsSerializer(questions, many=True)
        response = {
            'message': 'Success',
            'data': serializer.data
        }
        return Response(response, content_type='application/json; charset=utf-8')


class AddMbtiTestResult(APIView):
    def post(self, request):
        student_profile = get_profile(request)
        personalities = Personality.objects.all()
        current_date = date.today()
        answers = request.data['answers']
        counts = {
            'Extravert': 0,
            'Introvert': 0,
            'Sensor': 0,
            'Intuitive': 0,
            'Thinker': 0,
            'Feeler': 0,
            'Judger': 0,
            'Perceiver': 0
        }
        for index, answer in enumerate(answers, start=1):
            category = index % 7
            if category == 1:
                counts['Extravert' if answer == 1 else 'Introvert'] += 1
            elif category == 2 or category == 3:
                counts['Sensor' if answer == 1 else 'Intuitive'] += 1
            elif category == 4 or category == 5:
                counts['Thinker' if answer == 1 else 'Feeler'] += 1
            elif category == 6 or category == 0:
                counts['Judger' if answer == 1 else 'Perceiver'] += 1

        percentages = {
            'Extravert': (counts['Extravert'] / (counts['Extravert'] + counts['Introvert'])) if len(
                answers) > 0 else .50,
            'Introvert': (counts['Introvert'] / (counts['Extravert'] + counts['Introvert'])) if len(
                answers) > 0 else .50,
            'Sensor': (counts['Sensor'] / (counts['Sensor'] + counts['Intuitive'])) if len(answers) > 0 else .50,
            'Intuitive': (counts['Intuitive'] / (counts['Sensor'] + counts['Intuitive'])) if len(answers) > 0 else .50,
            'Thinker': (counts['Thinker'] / (counts['Thinker'] + counts['Feeler'])) if len(answers) > 0 else .50,
            'Feeler': (counts['Feeler'] / (counts['Thinker'] + counts['Feeler'])) if len(answers) > 0 else .50,
            'Judger': (counts['Judger'] / (counts['Judger'] + counts['Perceiver'])) if len(answers) > 0 else .50,
            'Perceiver': (counts['Perceiver'] / (counts['Judger'] + counts['Perceiver'])) if len(answers) > 0 else .50
        }

        for key, value in percentages.items():
            personality_model, _ = Personality.objects.get_or_create(name=key)
            pp = Decimal(value)
            student_personality = StudentPersonality.objects.create(
                studentProfile=student_profile,
                personality=personality_model,
                pp=pp,
                edit_date=current_date
            )

        response = {
            'message': 'Success',
            "data": percentages
        }
        return Response(response, content_type='application/json; charset=utf-8')
