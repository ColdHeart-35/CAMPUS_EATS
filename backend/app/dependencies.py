# backend/app/dependencies.py
"""FastAPI dependencies for authentication and role checking.
All routes can depend on ``get_current_user`` which returns the decoded JWT payload.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from .auth import security

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = security.decode_access_token(token)
        return payload
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")

def require_role(required_role: str):
    async def role_checker(user: dict = Depends(get_current_user)):
        if user.get("role") != required_role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user
    return role_checker
