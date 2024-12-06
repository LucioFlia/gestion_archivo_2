from .models import SystemConfigKeyValues

def system_config(request):
    try:
        pagination_limit = SystemConfigKeyValues.objects.get(key="pagination_limit").value
    except SystemConfigKeyValues.DoesNotExist:
        pagination_limit = 10  # default value

    return {"pagination_limit": pagination_limit}

