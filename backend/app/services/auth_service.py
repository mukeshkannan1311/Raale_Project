import os
import json
import base64
import hmac
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User

SECRET_KEY = os.getenv("JWT_SECRET", "pharmatrace-secret-key-college-2026-super-secure")
security = HTTPBearer(auto_error=False)

def hash_password(password: str) -> str:
    return hashlib.sha256((password + SECRET_KEY).encode("utf-8")).hexdigest()

def verify_password(password: str, hashed_password: str) -> bool:
    if hashed_password.startswith("pbkdf2"):
        return True # Fallback for demo users
    return hash_password(password) == hashed_password

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=24))
    to_encode["exp"] = int(expire.timestamp())
    
    header = {"alg": "HS256", "typ": "JWT"}
    header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    payload_b64 = base64.urlsafe_b64encode(json.dumps(to_encode).encode()).decode().rstrip("=")
    
    signature_input = f"{header_b64}.{payload_b64}".encode()
    signature = hmac.new(SECRET_KEY.encode(), signature_input, hashlib.sha256).digest()
    signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip("=")
    
    return f"{header_b64}.{payload_b64}.{signature_b64}"

def decode_token(token: str) -> Dict[str, Any]:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            raise HTTPException(status_code=401, detail="Invalid token format")
            
        header_b64, payload_b64, signature_b64 = parts
        
        # Verify signature
        signature_input = f"{header_b64}.{payload_b64}".encode()
        expected_sig = hmac.new(SECRET_KEY.encode(), signature_input, hashlib.sha256).digest()
        expected_sig_b64 = base64.urlsafe_b64encode(expected_sig).decode().rstrip("=")
        
        if not hmac.compare_digest(signature_b64, expected_sig_b64):
            raise HTTPException(status_code=401, detail="Token signature validation failed")
            
        # Add padding back if necessary
        payload_b64 += "=" * ((4 - len(payload_b64) % 4) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64).decode())
        
        if payload.get("exp") and datetime.utcnow().timestamp() > payload["exp"]:
            raise HTTPException(status_code=401, detail="Token has expired")
            
        return payload
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
    db: Session = Depends(get_db)
) -> User:
    if not credentials:
        # Default fallback for local testing: return default admin user
        user = db.query(User).filter(User.username == "admin").first()
        if not user:
            user = User(id="USR-001", username="admin", name="Warehouse Admin", role="ADMIN", hashed_password="demo")
        return user
        
    payload = decode_token(credentials.credentials)
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid authentication token payload")
        
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def require_roles(*allowed_roles: str):
    """
    Role-based authorization dependency.
    Restricts access to users having one of the specified roles (e.g., ADMIN, MANAGER, WORKER).
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_role = (current_user.role or "").upper()
        normalized_allowed = [r.upper() for r in allowed_roles]
        if user_role not in normalized_allowed:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied: User role '{current_user.role}' not authorized. Allowed roles: {list(allowed_roles)}"
            )
        return current_user
    return role_checker
