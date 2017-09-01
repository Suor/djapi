from funcy import compose, decorator

import django
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.middleware.csrf import CsrfViewMiddleware
from django.utils.module_loading import import_string

from .response import json


# Changed from method to property
if django.VERSION >= (1, 10):
    is_authenticated = lambda user: user.is_authenticated
else:
    is_authenticated = lambda user: user.is_authenticated()

def attempt_auth(request):
    # Prevent contrib.auth authentication, save user
    request.user, request._user = AnonymousUser(), request.user
    # Try hooks, allow contribauth when DEBUG = True by default
    hooks = getattr(settings, 'DJAPI_AUTH', ['djapi.auth.use_contribauth'])
    for hook in hooks:
        request.user = import_string(hook)(request)
        if is_authenticated(request.user):
            if not getattr(request.user, 'is_active', True):
                raise PermissionDenied('User inactive')
            break

# Hack borrowed from Django Rest Framework
class CSRFCheck(CsrfViewMiddleware):
    def _reject(self, request, reason):
        # Return the failure reason instead of an HttpResponse
        return reason

def use_contribauth(request):
    user = request._user
    if is_authenticated(user):
        # NOTE: we need to check here because CSRF is turned off,
        #       which is ok for all other authentication methods
        reason = CSRFCheck().process_view(request, None, (), {})
        if reason:
            raise PermissionDenied(reason)
    return user


# View decorators

def user_passes_test(test, message='Permission required', status=403):
    @decorator
    def deco(call):
        try:
            attempt_auth(call.request)
        except PermissionDenied as e:
            return json(status, detail=unicode(e))
        # Check test
        if test(call.request.user):
            return call()
        else:
            return json(status, detail=message)

    def csrf_exempt(func):
        func.csrf_exempt = True
        return func

    return compose(csrf_exempt, deco)

auth_required = user_passes_test(is_authenticated, status=401, message='Authorization required')
