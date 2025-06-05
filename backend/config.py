import os
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_env_variable(var_name: str, default=None, required=True) -> str:
    """Get environment variable or raise an exception if required"""
    value = os.getenv(var_name, default)
    if required and not value:
        raise ValueError(f"Environment variable {var_name} is not set")
    return value

class Config:
    """Application configuration"""
    
    # Database configuration
    DB_USER = get_env_variable("DB_USER", default="postgres")
    DB_PASSWORD = get_env_variable("DB_PASSWORD", default="password")
    DB_HOST = get_env_variable("DB_HOST", default="localhost")
    DB_PORT = get_env_variable("DB_PORT", default="5432")
    DB_NAME = get_env_variable("DB_NAME", default="postgres")
    
    # JWT Configuration
    JWT_SECRET_KEY = get_env_variable("JWT_SECRET_KEY")
    JWT_ALGORITHM = "HS256"
    JWT_ACCESS_TOKEN_EXPIRES = 30  # minutes
    
    # Microsoft OAuth2 configuration
    CLIENT_ID = get_env_variable("CLIENT_ID")
    CLIENT_SECRET = get_env_variable("CLIENT_SECRET")
    REDIRECT_URI = get_env_variable("REDIRECT_URI")
    FRONT_END_BASE_URL = get_env_variable("FRONT_END_BASE_URL")
    
    # Azure B2C Configuration
    TENANT = "emailagentnew"
    POLICY = "B2C_1_signup_signin"

    @classmethod
    def get_authority(cls) -> str:
        return f"https://{cls.TENANT}.b2clogin.com/{cls.TENANT}.onmicrosoft.com/{cls.POLICY}"
    
    @classmethod
    def get_token_endpoint(cls) -> str:
        return f"{cls.get_authority()}/oauth2/v2.0/token"

    @classmethod
    def get_scopes(cls) -> str:
        """Get properly formatted scope string for Azure B2C"""
        scopes = [
            "openid",
            "offline_access",
            f"https://{cls.TENANT}.onmicrosoft.com/emailagent-api/access_as_user"
        ]
        return ' '.join(scopes)
    @classmethod
    def get_token_endpoint(cls) -> str:
        return f"{cls.get_authority()}/oauth2/v2.0/token"
    
    @classmethod
    def get_authorize_endpoint(cls) -> str:
        return f"{cls.get_authority()}/oauth2/v2.0/authorize"
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return self.get_database_url()
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    @property
    def AUTHORITY(self) -> str:
        return f"https://{self.TENANT}.b2clogin.com/{self.TENANT}.onmicrosoft.com/{self.POLICY}"
    
    @property
    def TOKEN_ENDPOINT(self) -> str:
        return f"{self.AUTHORITY}/oauth2/v2.0/token"
    
    @property
    def AUTHORIZE_ENDPOINT(self) -> str:
        return f"{self.AUTHORITY}/oauth2/v2.0/authorize"
    
    @classmethod
    def get_database_url(cls) -> str:
        """Get database URL as string"""
        return f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"

    @classmethod
    def validate(cls) -> None:
        """Validate all required configuration is set"""
        required_vars = [
            "DB_USER",
            "DB_PASSWORD",
            "DB_HOST",
            "DB_PORT",
            "DB_NAME",
            "JWT_SECRET_KEY",
            "CLIENT_ID",
            "CLIENT_SECRET",
            "REDIRECT_URI",
            "FRONT_END_BASE_URL"
        ]
        
        missing = []
        for var in required_vars:
            if not getattr(cls, var, None):
                missing.append(var)
        
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")

        try:
            db_url = cls.SQLALCHEMY_DATABASE_URI
            print(f"Database URL configured as: {db_url}")
        except Exception as e:
            raise ValueError(f"Failed to construct database URL: {str(e)}")

# Validate configuration on import
Config.validate()