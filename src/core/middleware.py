from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.shortcuts import HttpResponsePermanentRedirect


class NoTrailingSlashPathMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if getattr(settings, 'REMOVE_SLASH', False):
            if '/admin' not in request.path and request.path != '/':
                if request.path.endswith('/'):
                    return HttpResponsePermanentRedirect(request.path[:-1])
