from django.core.signing import TimestampSigner, BadSignature, SignatureExpired

signer = TimestampSigner()

def generate_magic_token(email):
    return signer.sign(email)

def validate_magic_token(token, max_age=600):  # 10 minutes by default
    try:
        email = signer.unsign(token, max_age=max_age)
        return email
    except (BadSignature, SignatureExpired):
        return None
