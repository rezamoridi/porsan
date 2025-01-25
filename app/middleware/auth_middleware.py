from datetime import datetime, timedelta, timezone
from fastapi.security import HTTPBearer, OAuth2PasswordBearer
from fastapi import Depends, HTTPException, Request
import jwt
from passlib.context import CryptContext
from dotenv import load_dotenv
from os import getenv
load_dotenv()

# Configuration
SECRET_KEY = getenv("SECRET_KEY")
ALGORITHM = getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 1
REFRESH_TOKEN_EXPIRE_DAYS = 7

api_oauth_scheme = OAuth2PasswordBearer(tokenUrl="user/auth")


# Initialize components
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer()

class AuthService:
    @staticmethod
    def create_access_token(user_id: int, expires_delta: timedelta = None) -> str:
        """
        Create a JWT access token.
        """
        payload = {
            "sub": str(user_id), 
            "token_type": "access",     
            "exp": datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def create_refresh_token(user_id: int, expires_delta: timedelta = None) -> str:
        """
        Create a JWT refresh token.
        """
        payload = {
            "sub": str(user_id),  
            "token_type": "refresh",   
            "exp": datetime.now(timezone.utc) + (expires_delta or timedelta(days=7))
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def create_tokens(user_id: int):
        """
        Create both access and refresh tokens.
        """
        access_token = AuthService.create_access_token(
            user_id,
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        refresh_token = AuthService.create_refresh_token(
            user_id,
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
    

def create_tokens(user_id: int
):
    access_expires = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_expires = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    access_token = AuthService.create_access_token(
        data = {"sub": str(user_id)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    refresh_token = AuthService.create_refresh_token(
        data={"sub": str(user_id)},
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "access_expires": access_expires,
        "refresh_expires": refresh_expires
    }


def auth_middleware(x_auth_token = Depends(api_oauth_scheme)
):
    try:
        if not x_auth_token:
            raise HTTPException(status_code=401, detail="No auth token, access denied")
        
        verified_token = jwt.decode(jwt=x_auth_token, key=SECRET_KEY, algorithms=ALGORITHM)
        if verified_token:
            user_id = verified_token.get("sub")
            token_type = verified_token.get("token_type")
            exp = verified_token.get("exp")

            return {
                "user_id": user_id,
                "token_type":token_type,
                "exp":exp,
            }
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token is not valid , auth proccess faile!")  