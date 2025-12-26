from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from database import SessionDep
from models import User
from schemas import UserRegister, Token
from sqlmodel import select
import secrets

router = APIRouter(prefix='/auth', tags=['authentication'])

# This creates the lock button in Swagger
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

# Simple token storage (use Redis in production)
active_tokens = {}

# API 1: Register
@router.post('/register')
async def register(user: UserRegister, session: SessionDep):
    existing = session.exec(select(User).where(User.username == user.username)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    new_user = User(username=user.username, password=user.password)
    session.add(new_user)
    session.commit()
    return {"message": "User registered successfully"}

# API 2: Login - MUST use OAuth2PasswordRequestForm for Swagger to work
@router.post('/token', response_model=Token)
async def login(session: SessionDep, form_data: OAuth2PasswordRequestForm = Depends()):
    # OAuth2PasswordRequestForm uses form_data.username and form_data.password
    user = session.exec(
        select(User).where(
            User.username == form_data.username,
            User.password == form_data.password
        )
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate token
    token = secrets.token_urlsafe(32)
    active_tokens[token] = user.user_id
    
    return {"access_token": token, "token_type": "bearer"}

# Dependency to verify token - this is what makes routes protected
async def get_current_user(session: SessionDep, token: str = Depends(oauth2_scheme)):
    if token not in active_tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = active_tokens[token]
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user