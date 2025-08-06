# backlog/middleware.py
from django.contrib.sites.models import Site
from django.utils.deprecation import MiddlewareMixin

class ForceSiteMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.site = Site.objects.get(id=2)
