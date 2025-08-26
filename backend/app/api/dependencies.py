from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from app.core.database import get_db, get_redis
import redis

# Security
security = HTTPBearer()

def get_current_user(token: str = Depends(security)):
    """
    For MVP, we'll use a simple token validation.
    In production, implement proper JWT validation.
    """
    # MVP: Accept any token for now
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return {"user_id": 1, "username": "admin"}  # Mock user

def get_database() -> Generator:
    """Get database session"""
    try:
        db = next(get_db())
        yield db
    finally:
        db.close()

def get_redis_client() -> redis.Redis:
    """Get Redis client"""
    return get_redis()
