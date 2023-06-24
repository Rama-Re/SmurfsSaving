from decimal import Decimal

from users.views import *
from .serializers import *
from domainModel.models import *
from studentModel.views import *
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError
from django.db.models import F, Case, When, Value, CharField
from django.db.models.functions import Coalesce
from django.db.models import Count

# Create your views here.
class PerformInteraction(APIView):
    def post(self, request):
        student_profile = get_profile(request)
        pp = StudentPersonality.objects.filter(studentProfile=student_profile)
        # pp = student_profile.studentPersonality.all()
        g = GamificationFeature.objects.get(feature_name=request.data['feature_name'])
        rr = FeaturePersonalityRelationship.objects.filter(gamificationFeature_id=g.id)
        s = request.data['s']
        for r in rr:
            matching_pp = pp.get(personality=r.personality)
            if s > 0:
                updated_pp = matching_pp.pp + (1 - matching_pp.pp) * Decimal(s) * r.rr
                matching_pp.pp = updated_pp
                matching_pp.save()
            else:
                updated_pp = matching_pp.pp - matching_pp.pp * s * r.rr
                matching_pp.pp = updated_pp
                matching_pp.save()
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
        for g in gfs:
            rr = FeaturePersonalityRelationship.objects.filter(gamificationFeature_id=g.id)
            sum_rng_pn = 0
            sum_rng = 0
            for rng in rr:
                pn = pp.get(personality=rng.personality)
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
        to_review = ToReview.objects.annotate(num_reviews=Count('reviewed', distinct=True)).filter(owner=student_profile)

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
        to_review = ToReview.objects.annotate(num_reviews=Count('reviewed', distinct=True)).filter(reviewed__reviewer=student_profile)

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