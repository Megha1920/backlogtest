from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.shortcuts import get_current_site

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_app(self, request, provider, client_id=None):
        site = get_current_site(request)
        apps = SocialApp.objects.filter(provider=provider, sites=site)
        if apps.count() == 1:
            return apps.first()
        elif apps.count() == 0:
            raise SocialApp.DoesNotExist(
                f"No SocialApp for provider '{provider}' configured for site '{site.domain}'"
            )
        else:
            # DEBUGGING: Print them out before raising
            print("Multiple apps found:")
            for app in apps:
                print(f"App ID: {app.id}, Name: {app.name}, Client ID: {app.client_id}")
            raise SocialApp.MultipleObjectsReturned(
                f"Multiple SocialApps for provider '{provider}' found for site '{site.domain}'"
            )
