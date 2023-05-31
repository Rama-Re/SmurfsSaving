from django.contrib import admin
from django.urls import path, include
from .views import *
from django.contrib.auth.middleware import AuthenticationMiddleware

urlpatterns = [
    path('public/generalConcepts', GeneralConcepts.as_view()),
    path('public/subConcepts', SubConcepts.as_view()),
    path('public/theoreticalData', GetTheoreticalData.as_view()),
    path('public/codeDump', CodeDump.as_view()),
    path('public/getProject', GetProject.as_view()),
    path('public/getProjectGeneralConcepts', GetProjectGeneralConcepts.as_view()),
    path('public/getProjectsByIds', GetProjectsByIds.as_view()),
    path('public/getQuiz', GetQuiz.as_view()),
    path('public/getRecommendedProjects', GetRecommendedProjects.as_view()),
    path('public/checkQuizSolve', CheckQuizSolve.as_view()),
]