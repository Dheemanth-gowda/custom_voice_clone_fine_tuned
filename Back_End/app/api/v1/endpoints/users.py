from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from app.core.security import get_password_hash
from app.db.base import get_db
from app.db.models.user import User as UserDB
from app.schemas.user import User, UserCreate, UserUpdate
from app.services.auth import get_user_by_email, create_user, get_user_by_id, update_user, delete_user

router = APIRouter()

@router.get("/", response_model=List[User])
def get_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve users.
    """
    users = db.query(UserDB).offset(skip).limit(limit).all()
    return users

@router.get("/{user_id}", response_model=User)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
) -> Any:
    """
    Get user by ID.
    """
    user = get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user

@router.post("/", response_model=User)
def create_new_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """
    Create new user.
    """
    user = get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    user = create_user(db, user_in)
    return user

@router.put("/{user_id}", response_model=User)
def update_user_info(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    user_in: UserUpdate,
) -> Any:
    """
    Update user.
    """
    user = get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    user = update_user(db, db_user=user, user_in=user_in.dict(exclude_unset=True))
    return user

@router.delete("/{user_id}", response_model=User)
def delete_user_account(
    *,
    db: Session = Depends(get_db),
    user_id: int,
) -> Any:
    """
    Delete user.
    """
    user = get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    user = delete_user(db, user=user)
    return user 