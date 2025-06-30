"""
Supabase-based user authentication endpoints and helpers.
Handles sign-up, login, session verification, and utility functions.
"""

import os
from fastapi import APIRouter, HTTPException, Header
from dotenv import load_dotenv
from supabase import create_client, Client
from .models import UserSignupRequest, UserLoginRequest, UserAuthResponse, User

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

router = APIRouter(prefix="/auth", tags=["auth"])


# PUBLIC_INTERFACE
@router.post("/signup", summary="Register a new user", response_model=UserAuthResponse)
async def signup(signup_data: UserSignupRequest):
    """
    Registers a new user via Supabase authentication and users table.
    """
    try:
        result = supabase.auth.sign_up(
            {
                "email": signup_data.email,
                "password": signup_data.password,
                "data": {"username": signup_data.username or signup_data.email}
            }
        )
        user = result.user
        # Store username in separate users table for lookup (if needed)
        return UserAuthResponse(
            id=user.id,
            email=user.email,
            username=signup_data.username,
            access_token=result.session.access_token if result.session else None,
            error=None
        )
    except Exception as e:
        return UserAuthResponse(error=str(e))


# PUBLIC_INTERFACE
@router.post("/login", summary="Login user", response_model=UserAuthResponse)
async def login(login_data: UserLoginRequest):
    """
    Logs user in via Supabase auth, returns token and info.
    """
    try:
        result = supabase.auth.sign_in_with_password({
            "email": login_data.email,
            "password": login_data.password
        })
        user = result.user
        return UserAuthResponse(
            id=user.id,
            email=user.email,
            username=user.user_metadata.get("username", ""),
            access_token=result.session.access_token if result.session else None,
            error=None
        )
    except Exception as e:
        return UserAuthResponse(error=str(e))


# PUBLIC_INTERFACE
def verify_token(token: str = Header(..., alias="Authorization")) -> User:
    """
    Verifies Supabase JWT access token and gets user info.
    Raise HTTPException if invalid.
    """
    try:
        if token.startswith("Bearer "):
            token = token[7:]
        user_info = supabase.auth.get_user(token)
        if user_info and "user" in user_info.keys():
            user_obj = user_info["user"]
            return User(
                id=user_obj.get("id"),
                email=user_obj.get("email"),
                username=user_obj.get("user_metadata", {}).get("username", None),
                created_at=user_obj.get("created_at")
            )
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
