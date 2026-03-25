from .base import *  # noqa

DEBUG = False

# ── Security ──────────────────────────────────────────────────────────────────
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# ── Cloudflare R2 static + media ──────────────────────────────────────────────
AWS_ACCESS_KEY_ID = env("R2_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env("R2_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = env("R2_BUCKET_NAME")
AWS_S3_ENDPOINT_URL = f"https://{env('R2_ACCOUNT_ID')}.r2.cloudflarestorage.com"
AWS_S3_CUSTOM_DOMAIN = env("R2_PUBLIC_DOMAIN", default=None)
AWS_DEFAULT_ACL = "public-read"
AWS_S3_FILE_OVERWRITE = False

STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

# ── Sentry (optional but recommended even on free tier) ───────────────────────
SENTRY_DSN = env("SENTRY_DSN", default=None)
if SENTRY_DSN:
    import sentry_sdk
    sentry_sdk.init(dsn=SENTRY_DSN, traces_sample_rate=0.2)