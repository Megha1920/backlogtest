from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.shortcuts import get_current_site

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_app(self, request, provider, client_id=None):
        site = get_current_site(request)
        apps = SocialApp.objects.filter(provider=provider, sites=site)
        if apps.count() == 1:
            return apps.first()
        if apps.count() == 0:
            raise SocialApp.DoesNotExist(f"No SocialApp for provider '{provider}' configured for site '{site.domain}'")
        for app in apps:
            print(f"Multiple SocialApps found: ID={app.id}, Name={app.name}, ClientID={app.client_id}")
        raise SocialApp.MultipleObjectsReturned(f"Multiple SocialApps for provider '{provider}' found for site '{site.domain}'")

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        if not user.role:
            user.role = 'admin'  # or 'manager' based on your logic
            user.save()
        return user
