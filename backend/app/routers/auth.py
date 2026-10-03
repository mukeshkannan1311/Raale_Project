from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User, AuditLog
from app.schemas.schemas import UserLoginRequest, TokenResponse, UserResponse
from app.services.auth_service import verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication & Access Control"])

@router.post("/login", response_model=TokenResponse)
def login(payload: UserLoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
        
    token = create_access_token({"sub": user.username, "role": user.role, "name": user.name})
    
    db.add(AuditLog(
        id=f"AUD-{int(datetime.utcnow().timestamp())}",
        timestamp=datetime.utcnow(),
        user_id=user.id,
        action="LOGIN",
        entity="USER",
        details_json={"username": user.username, "role": user.role}
    ))
    db.commit()
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "name": user.name,
            "role": user.role
        }
    }

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return current_user
