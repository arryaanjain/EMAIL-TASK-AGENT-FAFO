import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")  # Recommended
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Microsoft OAuth2 config
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    REDIRECT_URI = os.getenv("REDIRECT_URI")
    AUTHORITY = "https://login.microsoftonline.com/common"
    SCOPE = ["User.Read", "Calendars.ReadWrite"]
