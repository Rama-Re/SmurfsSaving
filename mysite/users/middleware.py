from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin
from django.urls import resolve
import re
import jwt

from users.models import *

class ProcessRequestMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, *view_args, **view_kwargs):
        pattern = r'^private/'
        match = re.match(pattern, resolve(request.path_info).route)
        if match:
            token = request.COOKIES.get('jwt')
            if not token:
                return HttpResponse('Unauthenticated!', status=401)
            try:
                payload = jwt.decode(token, 'secret', algorithms=['HS256'])
                user = User.objects.filter(id=payload['id']).first()
                if user is None:
                    return HttpResponse('UserNotExist!', status=401)
                if user.is_verified:
                    return None
                else:
                    return HttpResponse('Unverified!', status=401)
            except jwt.ExpiredSignatureError:
                return HttpResponse('Unauthenticated!', status=401)
        else:
            return None
