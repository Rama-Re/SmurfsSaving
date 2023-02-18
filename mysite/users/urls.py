from django.contrib import admin
from django.urls import path, include
from .views import RegisterView
from .views import LoginView
from .views import UserView
from .views import LogoutView
from .views import VerifyEmail

urlpatterns = [
    path('register', RegisterView.as_view()),
    path('login', LoginView.as_view()),
    path('user', UserView.as_view()),
    path('logout', LogoutView.as_view()),
    path('verify', VerifyEmail.as_view()),
]