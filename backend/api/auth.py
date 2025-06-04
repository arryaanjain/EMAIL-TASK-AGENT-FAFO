from fastapi import APIRouter, HTTPException, Depends, Response
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config import Config


import urllib.parse
import requests
from typing import Optional
from jose import JWTError, jwt
from datetime import datetime, timedelta


# Add these near the top with other imports
security = HTTPBearer()

router = APIRouter()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Validate JWT token and return current user
    Args:
        credentials: HTTP Authorization credentials
    Returns:
        dict: User information from token
    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token, 
            Config.JWT_SECRET_KEY, 
            algorithms=[Config.JWT_ALGORITHM]
        )
        
        # Extract user information from token
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
            
        # You can add more user info here if needed
        user_data = {
            "email": email,
            "access_token": token,
            "token_expires": payload.get("exp")
        }
        
        return user_data
        
    except JWTError:
        raise credentials_exception
    except Exception:
        raise credentials_exception

@router.get("/login")
async def login():
    """Redirect to Microsoft login"""
    base_url = f"{Config.AUTHORITY}/oauth2/v2.0/authorize"
    params = {
        "client_id": Config.CLIENT_ID,
        "response_type": "code",
        "redirect_uri": Config.REDIRECT_URI,
        "response_mode": "query",
        "scope": " ".join(Config.SCOPE),
    }
    login_url = f"{base_url}?{urllib.parse.urlencode(params)}"
    return RedirectResponse(url=login_url)

@router.get("/callback")
async def auth_callback(code: Optional[str] = None):
    """Handle Microsoft OAuth callback"""
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code not found")
    
    token_data = {
        "grant_type": "authorization_code",
        "client_id": Config.CLIENT_ID,
        "client_secret": Config.CLIENT_SECRET,
        "code": code,
        "redirect_uri": Config.REDIRECT_URI,
        "scope": " ".join(Config.SCOPE),
    }

    response = requests.post(Config.TOKEN_ENDPOINT, data=token_data)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Token exchange failed")

    token_json = response.json()
    tokens = {
        "access_token": token_json.get("access_token"),
        "id_token": token_json.get("id_token")
    }
    
    redirect_url = f"{Config.FRONT_END_BASE_URL}/auth/callback?{urllib.parse.urlencode(tokens)}"
    return RedirectResponse(url=redirect_url)

@router.get("/logout")
async def logout():
    """Handle user logout"""
    logout_url = f"https://{Config.TENANT}.b2clogin.com/{Config.TENANT}.onmicrosoft.com/{Config.POLICY}/oauth2/v2.0/logout"
    params = {
        "post_logout_redirect_uri": f"{Config.FRONT_END_BASE_URL}/login"
    }
    return RedirectResponse(url=f"{logout_url}?{urllib.parse.urlencode(params)}")



# Replace the existing status endpoint
@router.get("/status")
async def auth_status(user = Depends(get_current_user)):
    """Check authentication status"""
    return {
        "isAuthenticated": True,
        "user": user
    }

