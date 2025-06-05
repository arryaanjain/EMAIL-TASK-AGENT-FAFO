from fastapi import APIRouter, HTTPException, Depends, Request, status
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from config import Config
import urllib.parse
import requests
from typing import Optional
from jose import JWTError, jwt
from datetime import datetime, timedelta

from db.models.user import User
from db import get_db

# Security setup
security = HTTPBearer()
router = APIRouter()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Validate token and return current user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        # Find user by access token
        user = db.query(User).filter_by(access_token=token).first()
        
        if not user or user.token_expires < datetime.utcnow():
            raise credentials_exception
            
        return {
            "email": user.email,
            "name": user.name,
            "token_expires": user.token_expires.isoformat()
        }
        
    except Exception:
        raise credentials_exception

@router.get("/login")
async def login():
    """Redirect to Microsoft login"""
    base_url = Config.get_authorize_endpoint()
    params = {
        "client_id": Config.CLIENT_ID,
        "response_type": "code",
        "redirect_uri": Config.REDIRECT_URI,
        "response_mode": "query",
        "scope": Config.get_scopes(),
    }
    login_url = f"{base_url}?{urllib.parse.urlencode(params)}"
    return RedirectResponse(url=login_url)

@router.get("/callback")
async def auth_callback(
    code: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Handle Microsoft OAuth callback"""
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code not found")
    
    try:
        print("Starting callback process...")
        # Exchange code for tokens
        token_data = {
            "grant_type": "authorization_code",
            "client_id": Config.CLIENT_ID,
            "client_secret": Config.CLIENT_SECRET,
            "code": code,
            "redirect_uri": Config.REDIRECT_URI,
            "scope": Config.get_scopes()
        }

        print("Exchanging code for tokens...")
        response = requests.post(Config.get_token_endpoint(), data=token_data)
        
        if response.status_code != 200:
            print(f"Token exchange failed: {response.text}")
            raise HTTPException(
                status_code=400, 
                detail=f"Token exchange failed: {response.text}"
            )
            
        token_json = response.json()
        access_token = token_json.get("access_token")
        id_token = token_json.get("id_token")

        print("Tokens received, decoding ID token...")
        try:
            # Split the token to get the payload part
            token_parts = id_token.split('.')
            if len(token_parts) != 3:
                raise ValueError("Invalid token format")
                
            # Decode the payload part (second part)
            import base64
            import json
            
            # Fix padding for base64
            payload = token_parts[1] + '=' * (-len(token_parts[1]) % 4)
            decoded_payload = base64.b64decode(payload)
            user_info = json.loads(decoded_payload)
            
            print(f"Decoded user info: {user_info}")
        except Exception as e:
            print(f"Token decode error: {str(e)}")
            user_info = {}

        email = (
            user_info.get("emails", [None])[0] or
            user_info.get("email") or
            user_info.get("preferred_username")
        )
        print(f"Extracted email: {email}")
        
        if email:
            expires_in = token_json.get("expires_in", 3600)
            token_expires = datetime.utcnow() + timedelta(seconds=int(expires_in))
            
            print("Checking for existing user...")
            user = db.query(User).filter_by(email=email).first()
            if user:
                print(f"Updating existing user: {email}")
                user.access_token = access_token
                user.refresh_token = token_json.get("refresh_token")
                user.token_expires = token_expires
                user.name = user_info.get("name")
            else:
                print(f"Creating new user: {email}")
                user = User(
                    email=email,
                    name=user_info.get("name"),
                    access_token=access_token,
                    refresh_token=token_json.get("refresh_token"),
                    token_expires=token_expires
                )
                db.add(user)
            
            try:
                print("Committing to database...")
                db.commit()
                print("Database commit successful")
            except Exception as e:
                print(f"Database error: {str(e)}")
                db.rollback()
                raise HTTPException(
                    status_code=500,
                    detail="Failed to save user data"
                )
        else:
            raise HTTPException(
                status_code=400,
                detail="No email found in token"
            )

        # Redirect with tokens
        tokens = {"access_token": access_token, "id_token": id_token}
        redirect_url = f"{Config.FRONT_END_BASE_URL}/auth/callback?{urllib.parse.urlencode(tokens)}"
        print(f"Redirecting to: {redirect_url}")
        return RedirectResponse(url=redirect_url)
        
    except Exception as e:
        print(f"Callback error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Authentication failed: {str(e)}"
        )

@router.get("/status")
async def auth_status(request: Request, db: Session = Depends(get_db)):
    """Check authentication status"""
    try:
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return {"isAuthenticated": False, "user": None}
        
        token = auth_header.split(" ")[1]
        
        # Find user by access token
        user = db.query(User).filter_by(access_token=token).first()
        
        if not user or user.token_expires < datetime.utcnow():
            return {"isAuthenticated": False, "user": None}
            
        return {
            "isAuthenticated": True,
            "user": {
                "email": user.email,
                "name": user.name,
                "token_expires": user.token_expires.isoformat()
            }
        }
    except Exception as e:
        print(f"Status check error: {str(e)}")
        return {"isAuthenticated": False, "user": None}

@router.get("/logout")
async def logout():
    """Handle user logout"""
    logout_url = f"https://{Config.TENANT}.b2clogin.com/{Config.TENANT}.onmicrosoft.com/{Config.POLICY}/oauth2/v2.0/logout"
    params = {
        "post_logout_redirect_uri": f"{Config.FRONT_END_BASE_URL}/login"
    }
    return RedirectResponse(url=f"{logout_url}?{urllib.parse.urlencode(params)}")

@router.get("/test-db")
async def test_db(db: Session = Depends(get_db)):
    """Test database connection"""
    try:
        # Try to query users
        users = db.query(User).all()
        return {"message": "Database connection successful", "user_count": len(users)}
    except Exception as e:
        print(f"Database test error: {str(e)}")
        return {"message": f"Database error: {str(e)}"}