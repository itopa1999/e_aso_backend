# 🔒 Input Validation Utilities
# Provides safe type conversion functions with error handling

def safe_float(value, default=0.0):
    """
    Safely convert a value to float.
    
    Args:
        value: The value to convert (string, int, float, etc.)
        default: The default value to return if conversion fails
        
    Returns:
        float: The converted value or default if conversion fails
        
    Example:
        >>> safe_float("12.5")
        12.5
        >>> safe_float("invalid")
        0.0
        >>> safe_float("invalid", -1)
        -1
    """
    try:
        if value is None:
            return default
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_int(value, default=0):
    """
    Safely convert a value to integer.
    
    Args:
        value: The value to convert (string, float, int, etc.)
        default: The default value to return if conversion fails
        
    Returns:
        int: The converted value or default if conversion fails
        
    Example:
        >>> safe_int("42")
        42
        >>> safe_int("invalid")
        0
        >>> safe_int("invalid", -1)
        -1
    """
    try:
        if value is None:
            return default
        return int(float(value))  # Convert via float to handle "42.5" -> 42
    except (ValueError, TypeError):
        return default


def safe_bool(value, default=False):
    """
    Safely convert a value to boolean.
    
    Args:
        value: The value to convert (string, bool, int, etc.)
        default: The default value to return if conversion fails
        
    Returns:
        bool: The converted value or default if conversion fails
        
    Example:
        >>> safe_bool("true")
        True
        >>> safe_bool("false")
        False
        >>> safe_bool("1")
        True
        >>> safe_bool("0")
        False
        >>> safe_bool("invalid")
        False
    """
    if isinstance(value, bool):
        return value
    
    if isinstance(value, str):
        return value.lower() in ('true', '1', 'yes', 'on')
    
    try:
        return bool(value)
    except (ValueError, TypeError):
        return default
