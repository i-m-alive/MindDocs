from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr,Field
from app.utils.database import get_db
from app.auth.models import User
from app.auth.utils import hash_password, verify_password
from app.auth.auth import create_access_token
from typing import Literal

router = APIRouter()

# 📦 Schema for user registration input
class RegisterInput(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    domain: Literal["retail", "medical", "finance", "legal"]

# 👤 Register a new user
@router.post("/register", status_code=201)
def register(data: RegisterInput, db: Session = Depends(get_db)):
    # ✅ Check for missing fields (optional, since Pydantic usually handles this)
    if not data.username or not data.email or not data.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="All fields are required."
        )

    # ✅ Check if username or email already exists
    existing_user = db.query(User).filter(
        (User.email == data.email) | (User.username == data.username)
    ).first()

    if existing_user:
        if existing_user.email == data.email:
            detail_msg = "Email is already registered."
        else:
            detail_msg = "Username is already taken."
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail_msg
        )

    try:
        # ✅ Create new user instance
        user = User(
            username=data.username,
            email=data.email,
            hashed_password=hash_password(data.password),
            domain=data.domain
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return {"message": "User registered successfully", "user_id": user.id}

    except Exception as e:
        print("❌ Registration error:", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error. Please try again later."
        )

# 🔑 User login
@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    try:
        user = db.query(User).filter(User.username == form_data.username).first()

        if not user or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"}
            )

        # ✅ Create JWT access token
        token = create_access_token(data={"sub": user.username})
        return {
            "access_token": token,
            "token_type": "bearer",
            "username": user.username
        }

    except Exception as e:
        print("❌ Login error:", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login."
        )

# 🛠️ Optional: Manually update a user's domain
@router.post("/set-domain")
def set_domain(
    user_id: int = Form(...),
    domain: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.domain = domain
    db.commit()
    return {"message": "Domain updated successfully"}
