from django.contrib import admin
from django.urls import path, include
from .views import *
from django.contrib.auth.middleware import AuthenticationMiddleware

urlpatterns = [
    path('private/performInteraction', PerformInteraction.as_view()),
    path('private/studentGamificationFeatures', StudentGamificationFeatures.as_view()),
    path('private/leaderBoard', LeaderBoard.as_view()),
    path('private/getTimer', GetTimer.as_view()),
    path('private/addCodeToReview', AddCodeToReview.as_view()),
    path('private/addReview', AddReview.as_view()),
    path('private/getToReviews', GetToReviews.as_view()),
    path('private/getToReview', GetToReview.as_view()),
    path('private/getMyToReview', GetMyToReview.as_view()),
    path('private/getMyReviewed', GetMyReviewed.as_view()),
]
