"""
auth.py
JWT-based authentication for FastAPI.

Features:
- Password hashing using Argon2 (passlib[argon2])
- OAuth2 password flow and /token endpoint
- create_access_token() and token verification
- get_current_user dependency to protect routes
- example register/login endpoints
- role check helper (is_admin)
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, FastAPI
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from db_config import get_db, engine
from db_model import Base, User
from model import Token, TokenData, UserCreate, UserRead
   

# ----------------- Security setup -----------------
# Use Argon2 via passlib to avoid bcrypt 72-byte limits
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# OAuth2 scheme (token endpoint path)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# Use environment variables in production for the SECRET_KEY!
SECRET_KEY = "change-me-to-a-random-secret-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # adjust as needed

# ----------------- Utility functions -----------------
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    # Argon2 supports long passwords; no need to truncate.
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ----------------- DB helpers -----------------
def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user_in: UserCreate, is_superuser: bool = False) -> User:
    hashed = get_password_hash(user_in.password)
    db_user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed,
        is_active=True,
        is_superuser=is_superuser
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# ----------------- Authentication dependencies -----------------
def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        is_super: bool = payload.get("is_superuser", False)
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username, is_superuser=is_super)
    except JWTError:
        raise credentials_exception

    user = get_user_by_username(db, token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def require_admin(current_user: User = Depends(get_current_user)):
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return current_user

# ----------------- FastAPI router / app -----------------
router = APIRouter()

@router.post("/register", response_model=UserRead, status_code=201)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = get_user_by_username(db, user_in.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")
    user = create_user(db, user_in)
    return user

@router.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password",
                            headers={"WWW-Authenticate": "Bearer"})
    token_data = {"sub": user.username, "is_superuser": user.is_superuser}
    access_token = create_access_token(token_data)
    return {"access_token": access_token, "token_type": "bearer"}

# Example protected route
@router.get("/me", response_model=UserRead)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

# Example admin-only route
@router.get("/admin-only")
def admin_only_route(current_user: User = Depends(require_admin)):
    return {"msg": f"Hello {current_user.username}, you are an admin."}

# ----------------- Init DB & include router if run as main app -----------------
def init_db():
    Base.metadata.create_all(bind=engine)

# Optional: quick test app
#app = FastAPI()
#app.include_router(router)

#@app.on_event("startup")
#def on_startup():
#    init_db()

# If you want to run this file directly:
# uvicorn auth:app --reload
