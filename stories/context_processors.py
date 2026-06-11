from django.conf import settings


def public_settings(request):
    return {
        'yandex_maps_api_key': settings.YANDEX_MAPS_API_KEY,
    }
