# backend/app/routes/auth.py
"""Authentication routes for CampusEats.
Provides:
- POST /register : student registration (admin can create staff/admin via DB seed)
- POST /login    : returns JWT access token
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from ..auth import schemas, security
from ..database import get_db
from ..services import user

router = APIRouter()

@router.post("/register", response_model=schemas.Token)
async def register(user_in: schemas.UserCreate, db=Depends(get_db)):
    # Check if email already exists
    existing = await user.get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    hashed = security.get_password_hash(user_in.password)
    new_user = await user.create_user(db, email=user_in.email, hashed_password=hashed,
                                      full_name=user_in.full_name, role=user_in.role)
    access_token = security.create_access_token({"sub": str(new_user["id"]), "role": new_user["role"]})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    db_user = await user.get_user_by_email(db, form_data.username)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    if not security.verify_password(form_data.password, db_user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    access_token = security.create_access_token({"sub": str(db_user["id"]), "role": db_user["role"]})
    return {"access_token": access_token, "token_type": "bearer"}
