from .models import SystemConfigKeyValues
from .models import User

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
        config_name_org = "Define config_name_org"  # Valor por defecto    

    return {
        "pagination_limit": pagination_limit,
        "default_archive_code": default_archive_code,
        "config_name_org": config_name_org
    }
    


def archive_responsible_area(request):
    """
    Adds the area of the archive responsible user whose deposit matches the logged-in user's deposit.

    Args:
        request (HttpRequest): The current HTTP request.

    Returns:
        dict: A dictionary containing the archive responsible's area or None.
    """
    if request.user.is_authenticated and hasattr(request.user, 'deposit'):
        try:
            archive_responsible = User.objects.filter(
                role='archive_responsible',
                deposit=request.user.deposit
            ).first()
            return {'archive_responsible_area': archive_responsible.area if archive_responsible else None}
        except Exception as e:
            # Optional: Log the exception if needed
            print(f"Error in archive_responsible_area context processor: {e}")
    return {'archive_responsible_area': None}
