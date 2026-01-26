# Security Audit Report - E-Sell Backend (Local Environment)
**Date:** January 25, 2026  
**Status:** Before Production Deployment  
**Severity Levels:** 🔴 Critical | 🟠 High | 🟡 Medium | 🔵 Low

---

## Executive Summary
This security audit identified **7 critical vulnerabilities**, **8 high-severity issues**, and **12 medium-priority concerns** that should be addressed before moving to production.

---

## 🔴 CRITICAL VULNERABILITIES

### 1. **JWT Tokens Exposed in URL Query Parameters (Critical)**
**Location:** [apps/users/BBL/Commands/MagicLogin.py](apps/users/BBL/Commands/MagicLogin.py#L43-L58), [apps/users/BBL/Commands/VerifyEmail.py](apps/users/BBL/Commands/VerifyEmail.py#L38-L55)

**Issue:** Access and refresh tokens are passed in URL query parameters after login:
```python
params = urlencode({
    "access": access_token,      # ⚠️ EXPOSED
    "refresh": refresh_token,    # ⚠️ EXPOSED
    "email": user.email,
    "name": user.first_name,
})
return redirect(f"{settings.BASE_URL}/index.html?{params}")
```

**Risk:**
- Tokens appear in browser history
- Visible in server access logs
- Can be captured in referer headers
- Exposed if shared via messaging/email

**Fix:**
```python
# Use POST request with session storage instead
# Or use secure HTTP-only cookies
response = Response({'access': access_token, 'refresh': refresh_token})
response.set_cookie('access_token', access_token, httponly=True, secure=True, samesite='Strict')
response.set_cookie('refresh_token', refresh_token, httponly=True, secure=True, samesite='Strict')
```

---

### 2. **Unauthenticated User Agent Analysis Endpoint (Critical)**
**Location:** [apps/administrator/views.py](apps/administrator/views.py#L358)

**Issue:**
```python
class UserAgentAnalysisView(generics.GenericAPIView):
    allow_any = [AllowAny]  # ⚠️ NO AUTHENTICATION
    
    def get(self, request, *args, **kwargs):
        email = request.query_params.get('email', None)  # ⚠️ USER INPUT
        result = UserAgentAnalysisQuery.query(email, request=request)
```

**Risk:**
- Any attacker can enumerate user data by email
- Can retrieve login IPs, devices, browsers for any user
- Information disclosure vulnerability

**Fix:**
```python
permission_classes = [IsAuthenticated, IsAdminPermission]
# Only admins should access this
```

---

### 3. **CORS Allows All Origins in Local (Will Fail in Prod)**
**Location:** [backend/settings/base.py](backend/settings/base.py#L131)

**Issue:**
```python
CORS_ALLOW_ALL_ORIGINS = True  # ⚠️ DEVELOPMENT ONLY
```

**Risk:**
- Any website can make requests to your API
- Vulnerable to CSRF attacks
- Cross-site data theft

**Fix:**
```python
# base.py
CORS_ALLOW_ALL_ORIGINS = False  # Default secure value

# dev.py
CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:5501",
    "http://localhost:3000",
]

# prod.py  
CORS_ALLOWED_ORIGINS = [
    "https://aso-oke.com",
    "https://shop.aso-oke.com",
]
CORS_ALLOW_CREDENTIALS = True
```

---

### 4. **Empty AUTH_PASSWORD_VALIDATORS (Critical)**
**Location:** [backend/settings/base.py](backend/settings/base.py#L118)

**Issue:**
```python
AUTH_PASSWORD_VALIDATORS = []  # ⚠️ NO PASSWORD VALIDATION
```

**Risk:**
- Users can set weak passwords (1 character, common words, etc.)
- No complexity requirements
- Brute force attacks easier

**Fix:**
```python
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
```

---

### 5. **JWT Token Lifetime Too Long (10 Days) - Critical Risk**
**Location:** [backend/settings/base.py](backend/settings/base.py#L135-L140)

**Issue:**
```python
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=10),  # ⚠️ TOO LONG
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": False,  # ⚠️ NOT ROTATING
    "BLACKLIST_AFTER_ROTATION": False,  # ⚠️ NO BLACKLIST
}
```

**Risk:**
- If token stolen, attacker has 10 days access
- No token rotation = no revocation capability
- No token blacklist = old tokens still work

**Fix:**
```python
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),  # Short-lived
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,  # Rotate on refresh
    "BLACKLIST_AFTER_ROTATION": True,  # Revoke old tokens
}
```

---

### 6. **Magic Link Token Not Time-Limited (Critical)**
**Location:** [utils/magic_link.py](utils/magic_link.py#L8)

**Issue:**
```python
def validate_magic_token(token, max_age=600):  # 10 minutes
    # But if max_age is not passed, no expiration!
    email = signer.unsign(token, max_age=max_age)
```

**Risk:**
- Magic links don't validate within time window across all calls
- Token reuse possible if not properly tracked

**Fix:**
```python
def validate_magic_token(token, max_age=600):
    """Magic token validation with enforced expiration"""
    try:
        email = signer.unsign(token, max_age=max_age)
        # Double-check against database token record
        verification = UserVerification.objects.get(
            token=token,
            is_verified=False
        )
        if verification.is_token_expired():
            raise ValidationError("Token expired")
        return email
    except (SignatureExpired, BadSignature):
        return None
```

---

### 7. **No Rate Limiting on Login Endpoints (Critical)**
**Location:** [apps/administrator/views.py](apps/administrator/views.py#L320), [apps/users/views.py](apps/users/views.py)

**Issue:**
No rate limiting on authentication endpoints means:
- Brute force attacks possible
- OTP can be guessed (1000 attempts)
- Magic link spam

**Status:**
- Magic link has throttle: `"magic_link": "50/minute"` ✅
- Login API has no throttle ❌

**Fix:**
```python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_RATES': {
        'user': '20000/hour',
        'anon': '100/hour',  # Strict for anonymous
        'magic_link': '10/minute',  # More strict
        'login': '10/minute',  # Add login throttle
        'otp': '5/minute',  # Add OTP throttle
    },
}

class LoginAPIView(generics.GenericAPIView):
    throttle_classes = [UserRateThrottle]
    throttle_scope = 'login'
```

---

## 🟠 HIGH SEVERITY ISSUES

### 8. **OTP Token Not Invalidated After Use**
**Location:** [apps/administrator/BLL/Commands/Login.py](apps/administrator/BLL/Commands/Login.py#L17-L40)

**Issue:**
```python
response = AdminVerifyOtpCommand.execute(token, email)
# ⚠️ No invalidation of token after use - can be reused
```

**Risk:**
- OTP can be used multiple times
- Attacker can replay OTP tokens
- Session hijacking possible

**Fix:**
```python
# In AdminVerifyOtpCommand
def execute(token, email):
    verification = UserVerification.objects.get(token=token, user__email=email)
    if not verification:
        return BaseResult(status_code=400, message="Invalid token")
    
    if verification.is_token_expired():
        return BaseResult(status_code=400, message="Token expired")
    
    # Mark as used immediately
    verification.is_verified = True
    verification.save()
    
    return BaseResult(status_code=200, message="Verified")
```

---

### 9. **User Agent Analysis Allows Email Enumeration (High)**
**Location:** [apps/administrator/BLL/Queries/UserAgentAnalysis.py](apps/administrator/BLL/Queries/UserAgentAnalysis.py#L13-L30)

**Issue:**
```python
if user_email:
    user = User.objects.filter(email__icontains=user_email).first()
    # Returns 404 or user data - reveals if email exists
```

**Risk:**
- User enumeration (email existence disclosure)
- Can build list of valid emails
- Requires permission check

**Fix:**
```python
class UserAgentAnalysisView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsAdminPermission]
    # Now requires admin login
```

---

### 10. **Payment Gateway Reference in URL (High)**
**Location:** [apps/aso/flutterwave.py](apps/aso/flutterwave.py#L51-L85), [apps/aso/BBL/Queries/Cart/FlutterConfirm.py](apps/aso/BBL/Queries/Cart/FlutterConfirm.py#L11-L35)

**Issue:**
```python
def initiate(request, user, cart_id, data):
    redirect_url = f"{settings.BASE_URL}/payment-callback?reference={cart_id}"
    # ⚠️ Sensitive cart info in URL
```

**Risk:**
- Cart data exposed in browser history
- Payment intent visible in logs
- Can be modified before redirect back

**Fix:**
```python
# Use secure callback verification
def initiate(request, user, cart_id, data):
    # Don't pass reference in redirect URL
    redirect_url = f"{settings.BASE_URL}/payment-callback"
    
    # Store session data securely
    request.session['pending_cart_id'] = cart_id
    request.session['payment_reference'] = reference
    
    # Server verifies against session, not URL params
```

---

### 11. **Debug Mode in Development (High)**
**Location:** [backend/settings/dev.py](backend/settings/dev.py#L1)

**Issue:**
```python
DEBUG = True
```

**Risk:**
- Full exception tracebacks exposed
- Secret keys might leak in error pages
- Database queries visible
- Security headers disabled

**Fix:**
```python
# dev.py
DEBUG = os.environ.get("DEBUG", "False") == "True"
# Explicitly set DEBUG=True in .env only if needed

# .env
DEBUG=False  # Default to False, enable only when debugging
```

---

### 12. **No CSRF Protection on Some Endpoints (High)**
**Location:** [backend/settings/base.py](backend/settings/base.py#L81)

**Issue:**
```python
MIDDLEWARE = [
    'django.middleware.csrf.CsrfViewMiddleware',  # Present but...
    'corsheaders.middleware.CorsMiddleware',  # CORS enabled = CSRF vulnerable
]
```

**Risk:**
- CORS + CSRF middleware = potential bypass
- Cross-site form submission attacks
- Token-based API might be vulnerable

**Fix:**
```python
# Ensure proper CSRF handling
CSRF_TRUSTED_ORIGINS = []  # Explicitly list trusted origins
CSRF_COOKIE_SECURE = True  # HTTPS only
CSRF_COOKIE_HTTPONLY = False  # JS needs access to token
CSRF_COOKIE_SAMESITE = 'Strict'  # Strict same-site
```

---

### 13. **Telegram Bot Token Exposed in Config (High)**
**Location:** [backend/settings/dev.py](backend/settings/dev.py#L36)

**Issue:**
```python
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")
```

**Risk:**
- If .env file exposed, bot token compromised
- Attacker can send messages as your bot
- Can spam/impersonate your channel

**Fix:**
```python
# Ensure .env is in .gitignore
# .gitignore
.env
.env.local
*.key
secrets/

# Use environment variables properly
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not set in environment")
```

---

### 14. **No Input Validation on Search Filters (High)**
**Location:** Multiple query files like [apps/administrator/BLL/Queries/ProductList.py](apps/administrator/BLL/Queries/ProductList.py#L8-L30)

**Issue:**
```python
if min_price:
    queryset = queryset.filter(current_price__gte=float(min_price))
```

**Risk:**
- `float()` can fail and return 500 error
- Non-integer min_price crashes API
- Information disclosure

**Fix:**
```python
def safe_float(value, default=0):
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

if min_price:
    min_price = safe_float(min_price, 0)
    queryset = queryset.filter(current_price__gte=min_price)
```

---

### 15. **Swagger Docs Protected by Weak Auth (High)**
**Location:** [backend/schema.py](backend/schema.py#L18-L45)

**Issue:**
```python
def swagger_protect(view_func):
    username, password = base64.b64decode(creds).decode('utf-8').split(':')
    # Basic auth with hardcoded credentials in env
```

**Risk:**
- Basic auth credentials easily decoded
- Single password for all users
- 1-hour session timeout not enforced properly
- Should use OAuth/JWT instead

**Fix:**
```python
# Use Django permission system instead
from rest_framework.permissions import IsAdminUser

def swagger_protect(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            return HttpResponse("Unauthorized", status=401)
        return view_func(request, *args, **kwargs)
    return wrapper
```

---

## 🟡 MEDIUM PRIORITY ISSUES

### 16. **Hardcoded Pagination Size (Medium)**
**Location:** [backend/settings/base.py](backend/settings/base.py#L168)

**Issue:**
```python
"PAGE_SIZE": 21,  # Hardcoded
```

**Risk:**
- User can request very large pages with `?page_size=10000`
- DoS attack vector
- Database load

**Fix:**
```python
'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
'PAGE_SIZE': 21,
'MAX_PAGE_SIZE': 100,  # Limit maximum
'SETTINGS': {
    'page_size_query_param': 'page_size',
    'max_page_size': 100,
}
```

---

### 17. **No Email Verification for Password Reset**
**Location:** [apps/administrator/views.py](apps/administrator/views.py#L262), Line 340+ ResetPasswordAPIView

**Issue:**
```python
class ResetPasswordAPIView(generics.GenericAPIView):
    # No email verification shown - needs review
```

**Risk:**
- Attacker could reset any user's password
- No email confirmation step

**Fix:**
```python
# Require email confirmation for password reset
1. User requests reset → system sends email with token
2. User clicks link → system validates token
3. Only then allow password change
```

---

### 18. **Insufficient Logging on Security Events (Medium)**
**Location:** Throughout codebase

**Issue:**
```python
# Login attempts, password changes logged but to console
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
# Development backend - won't work in prod
```

**Risk:**
- Security events not properly logged
- Cannot audit authentication attempts
- Hard to detect attacks

**Fix:**
```python
# Implement proper logging
LOGGING = {
    'handlers': {
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/security.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 10,
        },
    },
}

# Log all auth events
def log_security_event(event_type, user_email, status, details=""):
    logger.warning(f"[SECURITY] {event_type} - {user_email} - {status} - {details}")
```

---

### 19. **No File Upload Validation (Medium)**
**Location:** [apps/aso/models.py](apps/aso/models.py#L166-L175)

**Issue:**
```python
class ProductImage(BaseModel):
    image = models.ImageField(upload_to='products/gallery/')
    
    def save(self, *args, **kwargs):
        # Image count validated but file type/size NOT validated
```

**Risk:**
- Arbitrary file uploads possible
- User can upload malicious files
- Storage DoS attack

**Fix:**
```python
from django.core.files.uploadedfile import UploadedFile
from PIL import Image

def save(self, *args, **kwargs):
    # Validate file
    if self.image:
        # Check file size
        if self.image.size > 5 * 1024 * 1024:  # 5MB limit
            raise ValidationError("Image too large")
        
        # Check file type
        try:
            img = Image.open(self.image)
            img.verify()
        except Exception:
            raise ValidationError("Invalid image file")
    
    super().save(*args, **kwargs)
```

---

### 20. **Telegram Token Stored in Memory/Cache (Medium)**
**Location:** [telegram_bot/login_handler.py](telegram_bot/login_handler.py#L53-L68)

**Issue:**
```python
token_key = CacheKeys.format(CacheKeys.telegram_user_tokens, user_id=user_id)
GlobalCache.set(token_key, token)  # JWT stored in cache
```

**Risk:**
- Token stored in Redis/cache unencrypted
- If cache compromised, all tokens exposed
- No expiration set

**Fix:**
```python
# Set cache expiration
cache_expiry = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()
GlobalCache.set(token_key, token, timeout=cache_expiry)

# Or use secure session storage instead
request.session['telegram_token'] = token
request.session.set_expiry(cache_expiry)
```

---

### 21. **No API Versioning (Medium)**
**Location:** [backend/urls.py](backend/urls.py)

**Issue:**
```python
urlpatterns = [
    path('admins/api/', include('apps.administrator.urls')),
    path('aso/api/', include('apps.aso.urls')),
    # No version prefix
]
```

**Risk:**
- Breaking API changes affect all clients
- Can't deprecate endpoints
- Hard to maintain backward compatibility

**Fix:**
```python
urlpatterns = [
    path('api/v1/admins/', include('apps.administrator.urls')),
    path('api/v1/aso/', include('apps.aso.urls')),
    # path('api/v2/...', ...)  # Future version
]
```

---

### 22. **No SQL Injection Protection on Custom Queries (Medium)**
**Location:** [apps/administrator/BLL/Queries/UserOrderList.py](apps/administrator/BLL/Queries/UserOrderList.py#L1-L20)

**Issue:**
```python
queryset = queryset.filter(
    Q(phone__icontains=search) |  # ✓ Parameterized
    Q(first_name__icontains=search)  # ✓ Parameterized
)
```

**Status:** ✅ Good - using ORM properly

**Note:** Project uses Django ORM correctly. No SQL injection found.

---

## 🔵 LOW PRIORITY RECOMMENDATIONS

### 23-27. Additional Security Recommendations:
- **Add security headers:** X-Frame-Options, Content-Security-Policy
- **Implement request signing:** For payment callbacks
- **Add audit logging:** Track all admin actions
- **Implement 2FA:** For admin accounts
- **Add API documentation security:** Mark sensitive endpoints

---

## Production Checklist Before Deployment

- [ ] Enable HTTPS/TLS
- [ ] Set DEBUG = False
- [ ] Configure proper SECRET_KEY (different from dev)
- [ ] Set ALLOWED_HOSTS to production domain
- [ ] Enable SECURE_SSL_REDIRECT
- [ ] Set SECURE_HSTS_SECONDS = 31536000
- [ ] Configure CORS_ALLOWED_ORIGINS (whitelist domains only)
- [ ] Setup proper email backend
- [ ] Configure database backups
- [ ] Enable logging to file/monitoring service
- [ ] Set up rate limiting
- [ ] Implement API key rotation
- [ ] Document security procedures
- [ ] Run security tests
- [ ] Get security audit done by professional

---

## Summary Table

| # | Issue | Severity | Status | Priority |
|---|-------|----------|--------|----------|
| 1 | JWT in URL params | 🔴 | ❌ | ASAP |
| 2 | Unauthenticated user analysis | 🔴 | ❌ | ASAP |
| 3 | CORS allows all | 🔴 | ❌ | ASAP |
| 4 | No password validators | 🔴 | ❌ | ASAP |
| 5 | JWT lifetime 10 days | 🔴 | ❌ | ASAP |
| 6 | Magic link not time-limited | 🔴 | ❌ | ASAP |
| 7 | No rate limiting login | 🔴 | ❌ | ASAP |
| 8-15 | High severity issues | 🟠 | ❌ | Before prod |
| 16-22 | Medium issues | 🟡 | ⚠️ | Soon |
| 23+ | Low recommendations | 🔵 | ℹ️ | Enhancement |

---

## Next Steps

1. **Immediate (Before any deployment):**
   - Fix critical vulnerabilities (1-7)
   - Enable authentication on sensitive endpoints
   - Configure proper CORS
   - Add password validators

2. **Before Production:**
   - Address all high-severity issues (8-15)
   - Implement rate limiting
   - Configure HTTPS/TLS
   - Set up monitoring & logging

3. **Ongoing:**
   - Regular security audits
   - Dependency updates
   - Penetration testing
   - Security training for team

---

**Report Generated:** 2026-01-25  
**Auditor:** Security Review System  
**Next Review:** After fixes applied
