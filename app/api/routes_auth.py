import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
# from project_management_core.domain.services.user_service import (
#     UserNotFoundError,
#     UserService,
# )

from project_management_core.domain.services.user_service import UserService, UserNotFoundError

from project_management_core.infrastructure.repositories.db.connection import (
    get_async_session,
)
from project_management_core.infrastructure.repositories.db.user_repository_impl import (
    UserRepositoryImpl,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import UserCreate, UserLogin

router = APIRouter(prefix="", tags=["Auth"])

def get_user_service(session: AsyncSession = Depends(get_async_session)) -> UserService:
    """
    Dependency provider that returns a UserService instance.

    Args:
        session (AsyncSession): SQLAlchemy asynchronous session, injected by FastAPI.

    Returns:
        UserService: Service class providing user-related business logic.
    """
    repo = UserRepositoryImpl(session)
    return UserService(repo)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
SECRET_KEY = secrets.token_hex(32)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/login')

def create_access_token(user_id: int, email: str, 
expires_delta: timedelta | None = None) -> str:
    """
    Generate a JWT access token for a given user.

    Args:
        user_id (int): The unique ID of the user.
        email (str): User's email address.
        expires_delta (timedelta | None, optional): Custom expiration time. Defaults to 60 minutes.

    Returns:
        str: Encoded JWT access token.
    """
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {
        "sub": str(user_id),
        "email": email,
        "iat": datetime.now(timezone.utc),
        "exp": expire,
    }
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    service: UserService = Depends(get_user_service)):
    """
    Decode a JWT token and return the authenticated user.

    Args:
        token (str): JWT access token, injected via OAuth2 scheme.
        service (UserService): User service dependency.

    Returns:
        User: The authenticated user object.

    Raises:
        HTTPException: If token is invalid, expired, or user is inactive.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        email: str = payload.get('email')
        if user_id is None or email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid token payload")
        user = await service.user_repository.get_by_id(int(user_id))
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Inactive or unknown user")
        return user
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
        detail="Invalid token")


@router.post("/auth")
async def register_user(payload: UserCreate, 
service: UserService = Depends(get_user_service)):
    """
    Register a new user in the system.

    Args:
        payload (UserCreate): User data containing email and password.
        service (UserService): User service dependency.

    Returns:
        User: The newly created user.

    Raises:
        HTTPException: If user creation fails.
    """
    user = await service.register_user(payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=400, detail="User could not be created")
    return user

@router.post('/login')
async def login_user(payload: UserLogin, 
service: UserService = Depends(get_user_service)):
    """
    Authenticate a user with email and password, returning a JWT token.

    Args:
        payload (UserLogin): User credentials (email, password).
        service (UserService): User service dependency.

    Returns:
        dict: A dictionary containing the access token and token type.

    Raises:
        HTTPException: If user is not found, inactive, or credentials are invalid.
    """
    """Login with email and password - returns JWT access token"""
    try:
        user = await service.get_by_email(payload.email)
        if not user.is_active:
            raise HTTPException(status_code= 401, detail="User is not active")

        # Verify password: compare provided plaintext against stored bcrypt hash
        provided_password_bytes = payload.password.encode()
        stored_hash_bytes = user.password_hash if isinstance(user.password_hash, 
        bytes) else user.password_hash.encode()
        if not bcrypt.checkpw(provided_password_bytes, stored_hash_bytes):
            raise HTTPException(status_code= 401, detail="Invalid email or password")

        # Generate JWT token
        access_token = create_access_token(user.id, user.email)
        return {"access_token": access_token, "token_type": "bearer"}
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) 
