from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import UserCreate, UserLogin, UserResponse
from project_management_core.domain.services.user_service import UserService
from project_management_core.infrastructure.repositories.db.user_repository_impl import UserRepositoryImpl
from project_management_core.infrastructure.repositories.db.connection import get_async_session
from project_management_core.domain.services.user_service import UserNotFoundError
import bcrypt
import secrets
import jwt
from datetime import datetime, timedelta, timezone

router = APIRouter(prefix="", tags=["Auth"])

def get_user_service(session: AsyncSession = Depends(get_async_session)) -> UserService:
    repo = UserRepositoryImpl(session)
    return UserService(repo)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
SECRET_KEY = secrets.token_hex(32)


def create_access_token(user_id: int, email: str, expires_delta: timedelta | None = None) -> str:
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {
        "sub": str(user_id),
        "email": email,
        "iat": datetime.now(timezone.utc),
        "exp": expire,
    }
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/auth")
async def register_user(payload: UserCreate, service: UserService = Depends(get_user_service)):
    user = await service.register_user(payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=400, detail="User could not be created")
    return user

@router.post('/login')
async def login_user(payload: UserLogin, service: UserService = Depends(get_user_service)):
    """Login with email and password - returns JWT access token"""
    try:
        user = await service.get_by_email(payload.email)
        if not user.is_active:
            raise HTTPException(status_code= 401, detail="User is not active")

        # Verify password: compare provided plaintext against stored bcrypt hash
        provided_password_bytes = payload.password.encode()
        stored_hash_bytes = user.password_hash if isinstance(user.password_hash, bytes) else user.password_hash.encode()
        if not bcrypt.checkpw(provided_password_bytes, stored_hash_bytes):
            raise HTTPException(status_code= 401, detail="Invalid email or password")

        # Generate JWT token
        access_token = create_access_token(user.id, user.email)
        return {"access_token": access_token, "token_type": "bearer"}
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) 
