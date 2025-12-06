"""
User Agent utilities for parsing and saving user device information
"""
from ua_parser.user_agent_parser import Parse
from apps.users.models import UserAgent
from django.utils import timezone


def get_user_agent_from_request(request):
    """
    Extract user agent string from request
    """
    return request.META.get('HTTP_USER_AGENT', '')


def get_client_ip(request):
    """
    Get client IP address from request
    Handles proxies and load balancers
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def parse_user_agent(user_agent_string):
    """
    Parse user agent string into components
    Returns dict with browser, os, device info
    """
    try:
        parsed = Parse(user_agent_string)
        
        return {
            'user_agent_string': user_agent_string,
            'browser': parsed.get('user_agent', {}).get('family', 'Unknown'),
            'browser_version': parsed.get('user_agent', {}).get('major', 'Unknown'),
            'os': parsed.get('os', {}).get('family', 'Unknown'),
            'os_version': parsed.get('os', {}).get('major', 'Unknown'),
            'device': parsed.get('device', {}).get('family', 'Unknown'),
            'device_type': get_device_type(parsed.get('device', {}).get('family', 'Unknown')),
        }
    except Exception as e:
        print(f"Error parsing user agent: {e}")
        return {
            'user_agent_string': user_agent_string,
            'browser': 'Unknown',
            'browser_version': 'Unknown',
            'os': 'Unknown',
            'os_version': 'Unknown',
            'device': 'Unknown',
            'device_type': 'unknown',
        }


def get_device_type(device_family):
    """
    Determine device type from device family
    """
    device_family_lower = device_family.lower()
    
    if 'iphone' in device_family_lower or 'android' in device_family_lower:
        return 'mobile'
    elif 'ipad' in device_family_lower or 'tablet' in device_family_lower:
        return 'tablet'
    elif device_family_lower == 'other':
        return 'desktop'
    else:
        return 'desktop'


def save_user_agent(user, request):
    """
    Extract, parse and save user agent information
    
    Args:
        user: User instance
        request: HTTP request object
    
    Returns:
        UserAgent instance
    """
    user_agent_string = get_user_agent_from_request(request)
    ip_address = get_client_ip(request)
    
    # Parse user agent
    parsed_data = parse_user_agent(user_agent_string)
    
    # Get or create UserAgent record
    user_agent_obj, created = UserAgent.objects.update_or_create(
        user=user,
        user_agent_string=user_agent_string,
        ip_address=ip_address,
        defaults={
            'browser': parsed_data['browser'],
            'browser_version': parsed_data['browser_version'],
            'os': parsed_data['os'],
            'os_version': parsed_data['os_version'],
            'device': parsed_data['device'],
            'device_type': parsed_data['device_type'],
            'is_active': True,
            'last_seen': timezone.now(),
        }
    )
    
    return user_agent_obj, created


def get_user_devices(user):
    """
    Get all active devices for a user
    
    Returns:
        QuerySet of UserAgent objects
    """
    return UserAgent.objects.filter(user=user, is_active=True).order_by('-last_seen')


def deactivate_user_device(user_agent_id, user):
    """
    Deactivate a specific device for a user
    Useful for logout from specific device
    
    Args:
        user_agent_id: ID of UserAgent to deactivate
        user: User instance (for security check)
    
    Returns:
        Boolean indicating success
    """
    try:
        user_agent = UserAgent.objects.get(id=user_agent_id, user=user)
        user_agent.is_active = False
        user_agent.save()
        return True
    except UserAgent.DoesNotExist:
        return False


def get_suspicious_logins(user, threshold_days=7):
    """
    Get recent logins from different locations/devices
    Useful for detecting suspicious activity
    
    Args:
        user: User instance
        threshold_days: Number of days to look back
    
    Returns:
        List of suspicious login objects
    """
    from datetime import timedelta
    
    recent_date = timezone.now() - timedelta(days=threshold_days)
    return UserAgent.objects.filter(
        user=user,
        last_seen__gte=recent_date
    ).distinct('ip_address', 'device_type').values(
        'ip_address', 'device_type', 'browser', 'os', 'last_seen'
    ).order_by('-last_seen')
