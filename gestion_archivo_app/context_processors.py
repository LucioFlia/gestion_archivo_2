from .models import SystemConfigKeyValues

def system_config(request):
    try:
        pagination_limit = SystemConfigKeyValues.objects.get(key="pagination_limit").value
        default_archive_code = SystemConfigKeyValues.objects.get(key="default_archive_code").value
    except SystemConfigKeyValues.DoesNotExist:
        pagination_limit = 10  # default value
        default_archive_code = "AADE_ARCHIVE"

    return {
            "default_archive_code": default_archive_code,
            "pagination_limit": pagination_limit,
            
            }

