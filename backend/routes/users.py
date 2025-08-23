from fastapi import APIRouter, HTTPException
from typing import List, Optional
from database import fetch_rows, fetch_row, execute_query

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/")
async def get_users():
    """Get all users"""
    try:
        users = await fetch_rows("SELECT id, name, email, created_at FROM users ORDER BY created_at DESC")
        return {"users": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/{user_id}")
async def get_user(user_id: int):
    """Get a specific user by ID"""
    try:
        user = await fetch_row("SELECT id, name, email, created_at FROM users WHERE id = $1", user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.post("/")
async def create_user(name: str, email: str):
    """Create a new user"""
    try:
        result = await execute_query(
            "INSERT INTO users (name, email) VALUES ($1, $2) RETURNING id, name, email, created_at",
            name, email
        )
        return {"message": "User created successfully", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
