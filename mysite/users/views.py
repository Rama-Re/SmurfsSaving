from rest_framework.views import APIView
from .serializers import UserSerializer
from studentModel.serializers import *
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .models import User
from studentModel.models import *

import jwt, datetime



# Create your views here.

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # response = {
        #     'message': 'SUCCESS',
        #     'data': serializer.data
        # }
        return Response(serializer.data)



class LoginView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed('User Not Found!')
        if user.is_verified is False:
            raise AuthenticationFailed('Email Not Verified!')
        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect Password')

        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=60),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')

        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'jwt': token
        }
        return response


def userId(request):
    token = request.COOKIES.get('jwt')

    if not token:
        raise AuthenticationFailed('Unauthenticated!')
    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        return payload['id']
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Unauthenticated!')


class UserView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated!')
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        user = User.objects.filter(id=payload['id']).first()
        serializer = UserSerializer(user)
        response = {
            'message': 'SUCCESS',
            'data' : serializer.data
        }
        return Response(response)


class LogoutView(APIView):
    def post(self):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'SUCCESS'
        }
        return response


class VerifyEmail(APIView):
    def post(self, request):
        code = request.data.get('code')
        email = request.data['email']
        user = User.objects.filter(email=email).first()

        if user.verification_code == code:
            user.is_verified = True
            user.save()
            return Response({'message': 'Email verified'})
        else:
            return Response({'message': 'Invalid verification code'})




