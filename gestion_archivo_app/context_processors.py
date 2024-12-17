from .models import SystemConfigKeyValues

def system_config(request):
    try:
        pagination_limit = int(SystemConfigKeyValues.objects.get(key="pagination_limit").value)
    except SystemConfigKeyValues.DoesNotExist:
        pagination_limit = 10  # Valor por defecto

    try:
        default_archive_code = SystemConfigKeyValues.objects.get(key="default_archive_code").value
    except SystemConfigKeyValues.DoesNotExist:
        default_archive_code = "AADE_ARCHIVE"  # Valor por defecto
        
    try:
        config_name_org = SystemConfigKeyValues.objects.get(key="config_name_org").value
    except SystemConfigKeyValues.DoesNotExist:
        config_name_org = "Define"  # Valor por defecto    

    return {
        "pagination_limit": pagination_limit,
        "default_archive_code": default_archive_code,
        "config_name_org": config_name_org
    }
    