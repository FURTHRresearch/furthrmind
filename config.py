import os

SECRET_KEY = os.getenv("SECRET_KEY", "<your_secret_key_here>")
MONGODB_DB = os.getenv("MONGODB_DB", "furthrmind")
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/furthrmind")

ROOT_URL = os.getenv("ROOT_URL", "http://localhost:5000")
CALLBACK_URL = os.getenv("CALLBACK_URL", None)

GLITCHTIP_DSN = os.getenv("GLITCHTIP_DSN", None)

SERVER_VERSION = "1.31.1"

WEBDATACALC_API = os.getenv("WEBDATACALC_API", "https://webdatacalc.furthrmind.app")
WEBDATACALC_API_KEY = os.getenv("WEBDATACALC_API_KEY", "<your_webdatacalc_key_here>")
WEBDATACALC_CALLBACK_URL = os.getenv("WEBDATACALC_CALLBACK_URL", None)

REQUESTS_CA_BUNDLE = os.getenv("REQUESTS_CA_BUNDLE", None)


DEFAULT_ADMIN = os.getenv("DEFAULT_ADMIN", "")
S3_KEY = os.getenv("S3_KEY", "")
S3_SECRET = os.getenv("S3_SECRET", "")
S3_BUCKET = os.getenv("S3_BUCKET", "furthrmind")
S3_REGION = os.getenv("S3_REGION", "")
S3_ENDPOINT = os.getenv("S3_ENDPOINT", "")

ONLY_OFFICE_DOC_SERVER = os.getenv(
    "ONLY_OFFICE_DOC_SERVER", "https://onlyoffice.example.com"
)
ONLY_OFFICE_JWT_SECRET = os.getenv(
    "ONLY_OFFICE_JWT_SECRET", "<your_onlyoffice_jwt_here>"
)
ONLY_OFFICE_CALLBACK_URL = os.getenv("ONLY_OFFICE_CALLBACK_URL", None)

SESSION_COOKIE_SECURE = True
REMEMBER_COOKIE_SECURE = True

LDAP_LOGIN = os.getenv("LDAP_LOGIN", False)
LDAP_URL = os.getenv("LDAP_URL", "")
LDAP_PORT = os.getenv("LDAP_PORT", 389)
LDAP_DOMAIN_PREFIX = os.getenv("LDAP_DOMAIN_PREFIX", "")
LDAP_BASE_DN = os.getenv("LDAP_BASE_DN", "")

WELCOME_USERNAME_TEXT = os.getenv("WELCOME_USERNAME_TEXT", "Email")
SIGNUP_TEXT = os.getenv("SIGNUP_TEXT", "")

ALLOWED_SIGNUP_DOMAIN = os.getenv("ALLOWED_SIGNUP_DOMAIN", "example.com")

# rq and cache
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
REDIS_DB = os.getenv("REDIS_DB", "furthrmind")
REDIS_QUEUE_ENABLED = os.getenv("REDIS_QUEUE_ENABLED", True)


# Spreadsheet Calculator
SPREADSHEET_CALCULATOR_URL = os.getenv(
    "SPREADSHEET_CALCULATOR_URL", "https://spreadsheet-calc.furthrmind.app"
)
SPREADSHEET_CALCULATOR_ACCESS_KEY = os.getenv(
    "SPREADSHEET_CALCULATOR_ACCESS_KEY", "<your_spreadsheet_calculator_key_here>"
)


# Apps
ENABLED_APPS = os.getenv("ENABLED_APPS", None)
WEBAPP_CALLBACK_URL = os.getenv("WEBAPP_CALLBACK_URL", None)

# db session
DEMO_SESSION = os.getenv("DEMO_SESSION", False)

# Num worker
NUM_WORKER = os.getenv("NUM_WORKER", 4)
DEV_SESSION = os.getenv("DEV_SESSION", False)
