from datetime import datetime, timedelta, timezone
from fastapi.security import HTTPBearer, OAuth2PasswordBearer
from fastapi import Depends, HTTPException, Request, status
import jwt
from passlib3.context import CryptContext
from dotenv import load_dotenv
from os import getenv
from typing import Optional, Dict, Any, List

# Load environment variables
load_dotenv()

# Configuration
SECRET_KEY = getenv("SECRET_KEY")
ALGORITHM = getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Initialize components
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer()
api_oauth_scheme = OAuth2PasswordBearer(tokenUrl="user")


class AuthService:
    @staticmethod
    def create_access_token(user_id: int, role_id: int, expires_delta: timedelta = None) -> str:
        """
        Create a JWT access token.
        """
        payload = {
            "sub": str(user_id),
            "token_type": "access",
            "role_id": role_id,
            "exp": datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def create_refresh_token(user_id: int, role_id: int, expires_delta: timedelta = None) -> str:
        """
        Create a JWT refresh token.
        """
        payload = {
            "sub": str(user_id),
            "token_type": "refresh",
            "role_id": role_id ,
            "exp": datetime.now(timezone.utc) + (expires_delta or timedelta(days=7))
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def create_tokens(user_id: int, role_id: int):
        """
        Create both access and refresh tokens.
        """
        access_token = AuthService.create_access_token(
            user_id,
            role_id,
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        refresh_token = AuthService.create_refresh_token(
            user_id,
            role_id,
            expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "access_expires": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
            "refresh_expires": datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        }

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain password against a hashed password.
        """
        return pwd_context.verify(plain_password, hashed_password)




async def auth_middleware(request: Request, call_next):
    """
    Async middleware to handle authentication and token refreshing.
    """
    refresh_token = request.cookies.get("refresh_token")
    new_access_token = None

    try:
        # Validate access token from Authorization header
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            request.state.user_id = payload.get("sub")
            request.state.token_type = payload.get("token_type")

    except jwt.ExpiredSignatureError:
        # Attempt to refresh the access token using the refresh token
        if refresh_token:
            try:
                payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
                if payload.get("token_type") == "refresh":
                    new_access_token = AuthService.create_access_token(payload.get("sub"))
                    request.state.user_id = payload.get("sub")
                    request.state.token_type = "access"
            except jwt.PyJWTError:
                pass

    except jwt.PyJWTError:
        pass

    # Call the next middleware or route handler
    response = await call_next(request)

    # Attach new access token to the response headers if refreshed
    if new_access_token:
        response.headers["X-New-Access-Token"] = new_access_token

    return response


async def get_current_user(token: str = Depends(api_oauth_scheme)) -> Dict[str, Any]:
    """
    Dependency to get the current user from the JWT token.
    """
    try:
        if not token:
            raise HTTPException(status_code=401, detail="No auth token, access denied")

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        role_id = payload.get("role_id")
        token_type = payload.get("token_type")
        exp = payload.get("exp")

        if not user_id or token_type != "access":
            raise HTTPException(status_code=401, detail="Invalid token")

        return {
            "user_id": user_id,
            "role_id": role_id,
            "token_type": token_type,
            "exp": exp
        }

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")

    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    


    


# Need to work on #----------------------------------------------------------------------------
def require_role(required_role_ids: List[int]):
    """
    Decorator for role-based access control.
    
    Args:
        required_role_ids (List[int]): List of role IDs that have access.

    Returns:
        Callable: A dependency function for use in FastAPI routes.
    """
    required_roles_set = set(required_role_ids)  # Optimized for quick lookups
    
    async def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        """
        Verifies if the current user's role is authorized.
        
        Args:
            current_user (Dict[str, Any]): The user object, typically from a dependency.

        Raises:
            HTTPException: If the user lacks sufficient permissions.

        Returns:
            Dict[str, Any]: The validated user object.
        """
        if not current_user or "role_id" not in current_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user data"
            )
        if current_user["role_id"] not in required_roles_set:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="higher role permissions needed"
            )
        return current_user

    return role_checker

get_admin = require_role([2, 3])   # Admin (2) or Super Admin (3)
get_super_admin = require_role([3])  # Only Super Admin (3)