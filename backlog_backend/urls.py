from django.contrib import admin
from django.urls import path, include
from backlog.views import CustomRegisterView
from allauth.account.views import confirm_email

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView

import logging

logger = logging.getLogger(__name__)

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter

    def get_serializer(self, *args, **kwargs):
        # Accept id_token from frontend and map it to access_token
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        data = kwargs.get('data', {})
        if 'access_token' not in data and 'id_token' in data:
            data['access_token'] = data['id_token']
        kwargs['data'] = data
        return serializer_class(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        logger.debug(f"Incoming Google social login POST data: {request.data}")
        return super().post(request, *args, **kwargs)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('backlog.urls')),
    path('auth/', include('dj_rest_auth.urls')),
    # path('auth/registration/', include('dj_rest_auth.registration.urls')),
    path('auth/social/login/', GoogleLogin.as_view(), name='google_login'),  # ✅ manual path
    path('auth/registration/', CustomRegisterView.as_view(), name='custom_registration'),
    path('auth/confirm-email/<str:key>/', confirm_email, name='account_confirm_email'),
    path('auth/', include('allauth.socialaccount.urls')),
]
