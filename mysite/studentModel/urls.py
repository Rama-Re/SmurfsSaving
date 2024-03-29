from django.contrib import admin
from django.urls import path, include
from .views import *
from django.contrib.auth.middleware import AuthenticationMiddleware

urlpatterns = [
    path('private/addPersonality', AddPersonality.as_view()),
    path('private/getPersonality', GetPersonality.as_view()),
    # path('private/editPersonality', EditPersonality.as_view()),
    path('private/addTheoreticalSkill', AddTheoreticalSkill.as_view()),
    # path('private/editPracticalSkill', EditPracticalSkill.as_view()),
    path('private/addSolveTrying', AddSolveTrying.as_view()),
    path('private/addProjectSolve', AddProjectSolve.as_view()),
    path('private/checkQuizSolve', CheckQuizSolve.as_view()),
    path('private/addStudentKnowledge', AddStudentKnowledge.as_view()),
    path('private/editStreak', EditStreak.as_view()),
    path('private/getStreak', GetStreak.as_view()),
    path('private/getProfile', GetProfile.as_view()),
    path('private/evaluateRecommend', EvaluateRecommend.as_view()),
    path('public/students', GetAllStudents.as_view()),
    path('public/addPerformance', AddPerformance.as_view()),
]
