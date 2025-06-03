import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")  # Recommended
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Microsoft OAuth2 config
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    REDIRECT_URI = os.getenv("REDIRECT_URI")
    # Azure B2C Configuration
    TENANT = "emailagentnew"
    POLICY = "B2C_1_signup_signin"
    AUTHORITY = f"https://{TENANT}.b2clogin.com/{TENANT}.onmicrosoft.com/{POLICY}"
    TOKEN_ENDPOINT = f"https://{TENANT}.b2clogin.com/{TENANT}.onmicrosoft.com/{POLICY}/oauth2/v2.0/token"
    AUTHORIZE_ENDPOINT = f"https://{TENANT}.b2clogin.com/{TENANT}.onmicrosoft.com/{POLICY}/oauth2/v2.0/authorize"
    SCOPE = [
        "openid",
        "offline_access",
        f"https://{TENANT}.onmicrosoft.com/emailagent-api/access_as_user"
    ]
    FRONT_END_BASE_URL = os.getenv("FRONT_END_BASE_URL")