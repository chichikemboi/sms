from django.conf import settings


def school_info(request):
    return {
        'SCHOOL_NAME': settings.SCHOOL_NAME,
        'SCHOOL_SHORT': settings.SCHOOL_SHORT,
        'SCHOOL_MOTTO': settings.SCHOOL_MOTTO,
    }
