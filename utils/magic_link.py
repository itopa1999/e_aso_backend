from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.core.exceptions import ValidationError

signer = TimestampSigner()

def generate_magic_token(email):
    """Generate a time-signed magic token"""
    return signer.sign(email)

def validate_magic_token(token, max_age=600):  # 10 minutes by default
    """
    Validate magic token with triple-layer security:
    1. Check cryptographic signature and age
    2. Verify against database MagicLoginToken record
    3. Ensure token hasn't been used already
    
    Args:
        token: The signed token to validate
        max_age: Maximum age in seconds (default 10 minutes)
    
    Returns:
        str: Email if valid, None if invalid/expired
    """
    try:
        # ✅ First check: Verify signature and timestamp
        email = signer.unsign(token, max_age=max_age)
        
        # ✅ Second check: Verify against database record
        from apps.users.models import MagicLoginToken, User
        
        user = User.objects.filter(email=email, is_deleted=False).first()
        if not user:
            return None
        
        # Check if magic login token exists and hasn't been used
        magic_token = MagicLoginToken.objects.filter(
            user=user,
            signed_token=token,
            is_used=False  # Token must not already be used
        ).first()
        
        if not magic_token:
            return None
        
        # ✅ Third check: Verify expiration on database record
        if magic_token.is_token_expired():
            return None
        
        return email
        
    except (BadSignature, SignatureExpired):
        return None
    except Exception:
        return None
