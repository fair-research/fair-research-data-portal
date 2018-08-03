from django.conf import settings


def globals(request):
    return {
        'server_url': settings.SERVER_URL
    }