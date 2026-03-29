"""
Pydantic Schemas for Request/Response Validation
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from enum import Enum


class RoleEnum(str, Enum):
    """User roles in the system"""
    NONE = "NONE"
    MANUFACTURER = "MANUFACTURER"
    DISTRIBUTOR = "DISTRIBUTOR"
    PHARMACY = "PHARMACY"
    CONSUMER = "CONSUMER"
    REGULATOR = "REGULATOR"


# ============ User Schemas ============

class UserBase(BaseModel):
    """Base user schema"""
    walletAddress: str = Field(..., description="Ethereum wallet address")
    role: RoleEnum = Field(..., description="User role")
    name: str = Field(..., min_length=1, description="User or organization name")


class UserCreate(UserBase):
    """Schema for creating a new user"""
    pass


class UserResponse(UserBase):
    """Schema for user response"""
    isRegistered: bool
    registrationTimestamp: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============ Drug Composition Schemas ============

class DrugIngredient(BaseModel):
    """Individual drug ingredient"""
    name: str = Field(..., description="Ingredient name")
    quantity: str = Field(..., description="Quantity with unit")
    percentage: Optional[float] = Field(None, description="Percentage of total composition")


class DrugComposition(BaseModel):
    """Complete drug composition"""
    ingredients: List[DrugIngredient] = Field(..., description="List of ingredients")
    
    @validator('ingredients')
    def validate_ingredients(cls, v):
        if not v or len(v) == 0:
            raise ValueError("At least one ingredient is required")
        return v


class DrugCompositionDataset(BaseModel):
    """Standard drug composition from dataset"""
    drugName: str = Field(..., description="Drug name")
    standardComposition: DrugComposition = Field(..., description="Standard composition")


# ============ Drug Registration Schemas ============

class DrugRegistrationRequest(BaseModel):
    """Schema for drug registration request"""
    batchId: str = Field(..., min_length=1, description="Unique batch identifier")
    drugName: str = Field(..., min_length=1, description="Drug name")
    composition: DrugComposition = Field(..., description="Drug composition")
    manufactureDate: int = Field(..., description="Manufacturing date (Unix timestamp)")
    expiryDate: int = Field(..., description="Expiry date (Unix timestamp)")
    manufacturerAddress: str = Field(..., description="Manufacturer wallet address")
    
    @validator('expiryDate')
    def validate_expiry_date(cls, v, values):
        if 'manufactureDate' in values and v <= values['manufactureDate']:
            raise ValueError("Expiry date must be after manufacture date")
        return v


class DrugRegistrationResponse(BaseModel):
    """Schema for drug registration response"""
    success: bool
    message: str
    batchId: str
    compositionHash: str
    transactionHash: Optional[str] = None


class DrugInfo(BaseModel):
    """Schema for drug information"""
    batchId: str
    drugName: str
    fullComposition: dict
    compositionHash: str
    manufacturer: str
    manufactureDate: int
    expiryDate: int
    registrationTimestamp: datetime


# ============ Ownership Transfer Schemas ============

class OwnershipTransferRequest(BaseModel):
    """Schema for ownership transfer request"""
    batchId: str = Field(..., description="Batch identifier")
    fromAddress: str = Field(..., description="Current owner address")
    toAddress: str = Field(..., description="New owner address")
    location: str = Field(..., min_length=1, description="Transfer location")


class OwnershipTransferResponse(BaseModel):
    """Schema for ownership transfer response"""
    success: bool
    message: str
    batchId: str
    transactionHash: Optional[str] = None


# ============ Verification Schemas ============

class OwnershipRecord(BaseModel):
    """Single ownership transfer record"""
    from_address: str = Field(..., alias="from")
    to_address: str = Field(..., alias="to")
    timestamp: int
    location: str
    fromRole: str
    toRole: str
    
    class Config:
        populate_by_name = True


class DrugVerificationResponse(BaseModel):
    """Schema for drug verification response"""
    isGenuine: bool
    status: str  # "GENUINE", "FAKE", "EXPIRED", "INCOMPLETE_CHAIN"
    batchId: str
    drugName: str
    manufacturer: str
    compositionHash: str
    currentOwner: str
    manufactureDate: int
    expiryDate: int
    transferCount: int
    ownershipHistory: List[OwnershipRecord]
    composition: Optional[DrugComposition] = None
    anomalies: List[str] = []


# ============ Audit Schemas ============

class AuditResult(BaseModel):
    """Schema for audit result"""
    batchId: str
    hasAnomalies: bool
    anomalyType: str
    ownershipCount: int
    drugName: str
    manufacturer: str
    currentOwner: str


class AuditStatistics(BaseModel):
    """Schema for audit statistics"""
    totalDrugs: int
    totalUsers: int
    totalTransfers: int
    drugsWithAnomalies: int
    expiredDrugs: int


# ============ Composition Validation Schemas ============

class CompositionValidationRequest(BaseModel):
    """Schema for composition validation request"""
    drugName: str = Field(..., description="Drug name")
    composition: DrugComposition = Field(..., description="Drug composition to validate")


class CompositionValidationResponse(BaseModel):
    """Schema for composition validation response"""
    isValid: bool
    message: str
    matchPercentage: Optional[float] = None
    missingIngredients: List[str] = []
    extraIngredients: List[str] = []


# ============ Common Response Schemas ============

class SuccessResponse(BaseModel):
    """Generic success response"""
    success: bool
    message: str
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    """Generic error response"""
    success: bool = False
    error: str
    details: Optional[str] = None
