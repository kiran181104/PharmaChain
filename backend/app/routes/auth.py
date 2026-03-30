"""
Authentication and User Management Routes
"""
from fastapi import APIRouter, HTTPException, Depends, status
from app.schemas import UserCreate, UserResponse, SuccessResponse
from app.database import get_database
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["Authentication"])


def check_database_connection():
    """Check if database is available"""
    db = get_database()
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available"
        )
    return db


@router.post("/register", response_model=SuccessResponse)
async def register_user(user: UserCreate, db=Depends(get_database)):
    """
    Register a new user in the system
    
    - **walletAddress**: Ethereum wallet address
    - **role**: User role (MANUFACTURER, DISTRIBUTOR, PHARMACY, CONSUMER, REGULATOR)
    - **name**: User or organization name
    """
    try:
        # Check database connection
        if db is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection not available. Please try again later."
            )
        
        # Check if user already exists
        existing_user = await db.users.find_one({"walletAddress": user.walletAddress})
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this wallet address already registered"
            )
        
        # Create user document
        user_doc = {
            "walletAddress": user.walletAddress,
            "role": user.role.value,
            "name": user.name,
            "isRegistered": True,
            "registrationTimestamp": None  # Will be set when registered on blockchain
        }
        
        # Insert into database
        result = await db.users.insert_one(user_doc)
        
        logger.info(f"User registered: {user.walletAddress} as {user.role}")
        
        return {
            "success": True,
            "message": "User registered successfully",
            "data": {
                "userId": str(result.inserted_id),
                "walletAddress": user.walletAddress,
                "role": user.role.value
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"User registration failed: {str(e)}"
        )


@router.get("/user/{wallet_address}", response_model=UserResponse)
async def get_user(wallet_address: str, db=Depends(get_database)):
    """
    Get user details by wallet address
    """
    try:
        # Check database connection
        if db is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection not available. Please try again later."
            )
        
        user = await db.users.find_one({"walletAddress": wallet_address})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "walletAddress": user["walletAddress"],
            "role": user["role"],
            "name": user["name"],
            "isRegistered": user["isRegistered"],
            "registrationTimestamp": user.get("registrationTimestamp")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user: {str(e)}"
        )


@router.get("/users", response_model=List[UserResponse])
async def get_all_users(db=Depends(get_database)):
    """
    Get all registered users (Admin/Regulator only in production)
    """
    try:
        users_cursor = db.users.find({})
        users = await users_cursor.to_list(length=100)
        
        return [
            {
                "walletAddress": user["walletAddress"],
                "role": user["role"],
                "name": user["name"],
                "isRegistered": user["isRegistered"],
                "registrationTimestamp": user.get("registrationTimestamp")
            }
            for user in users
        ]
        
    except Exception as e:
        logger.error(f"Get all users error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve users: {str(e)}"
        )
