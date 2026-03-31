"""
Drug Management Routes
Handles drug registration and ownership transfer
"""
from fastapi import APIRouter, HTTPException, Depends, status
from app.schemas import (
    DrugRegistrationRequest,
    DrugRegistrationResponse,
    DrugInfo,
    OwnershipTransferRequest,
    OwnershipTransferResponse,
    CompositionValidationRequest,
    CompositionValidationResponse
)
from app.database import get_database
from app.utils import generate_composition_hash, blockchain_service, validate_composition
from datetime import datetime
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/drugs", tags=["Drugs"])


@router.post("/validate-composition", response_model=CompositionValidationResponse)
async def validate_drug_composition(
    request: CompositionValidationRequest,
    db=Depends(get_database)
):
    """
    Validate drug composition against standard dataset
    
    - **drugName**: Name of the drug
    - **composition**: Drug composition to validate
    """
    try:
        # Check if database is available
        if db is None:
            logger.error("Database connection not available for composition validation")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database service temporarily unavailable"
            )
        
        # Fetch standard composition from dataset (exact match)
        dataset_entry = await db.drug_composition_dataset.find_one(
            {"drugName": request.drugName}
        )

        # Fall back to case-insensitive match (handles minor naming mismatch)
        if not dataset_entry:
            dataset_entry = await db.drug_composition_dataset.find_one(
                {"drugName": {"$regex": f"^{request.drugName}$", "$options": "i"}}
            )

        if not dataset_entry:
            # Debug log the issue
            count = await db.drug_composition_dataset.count_documents({})
            logger.warning(f"Drug composition not found: {request.drugName} (dataset has {count} entries)")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No standard composition found for drug: {request.drugName}"
            )
        
        # Validate composition
        is_valid, message, details = await validate_composition(
            request.drugName,
            request.composition.dict(),
            dataset_entry.get("standardComposition", {})
        )
        
        return {
            "isValid": is_valid,
            "message": message,
            "matchPercentage": details.get("matchPercentage"),
            "missingIngredients": details.get("missingIngredients", []),
            "extraIngredients": details.get("extraIngredients", [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Composition validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Composition validation failed: {str(e)}"
        )


@router.get("/dataset/all")
async def list_standard_drugs(db=Depends(get_database)):
    """
    Get all standard drugs in the composition dataset
    Useful for verifying seeding and debugging
    """
    try:
        if db is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection not available"
            )
        
        drugs = await db.drug_composition_dataset.find({}).to_list(length=None)
        
        # Remove MongoDB _id field and return just the drug names and compositions
        result = [
            {
                "drugName": drug.get("drugName"),
                "standardComposition": drug.get("standardComposition")
            }
            for drug in drugs
        ]
        
        logger.info(f"Retrieved {len(result)} drugs from dataset")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve dataset: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve dataset: {str(e)}"
        )


@router.post("/register", response_model=DrugRegistrationResponse)
async def register_drug(
    drug_data: DrugRegistrationRequest,
    db=Depends(get_database)
    
):
    """
    Register a new drug batch on the blockchain
    
    Steps:
    1. Validate composition against dataset
    2. Generate composition hash (SHA-256)
    3. Store on blockchain
    4. Store full composition in MongoDB
    
    - **batchId**: Unique batch identifier
    - **drugName**: Name of the drug
    - **composition**: Full drug composition
    - **manufactureDate**: Manufacturing date (Unix timestamp)
    - **expiryDate**: Expiry date (Unix timestamp)
    - **manufacturerAddress**: Manufacturer's wallet address
    """
    try:
        # Check if batch ID already exists
        existing_batch = await db.drug_composition_storage.find_one(
            {"batchId": drug_data.batchId}
        )
        
        if existing_batch:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Batch ID already exists"
            )
        
        # Validate manufacturer
        manufacturer = await db.users.find_one(
            {"walletAddress": drug_data.manufacturerAddress}
        )
        
        if not manufacturer or manufacturer.get("role") != "MANUFACTURER":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only registered manufacturers can register drugs"
            )
        
        # Validate composition against dataset
        dataset_entry = await db.drug_composition_dataset.find_one(
            {"drugName": drug_data.drugName}
        )

        if not dataset_entry:
            dataset_entry = await db.drug_composition_dataset.find_one(
                {"drugName": {"$regex": f"^{drug_data.drugName}$", "$options": "i"}}
            )

        if dataset_entry:
            is_valid, message, _ = await validate_composition(
                drug_data.drugName,
                drug_data.composition.dict(),
                dataset_entry.get("standardComposition", {})
            )
            
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Composition validation failed: {message}"
                )
        
        # Generate composition hash
        composition_hash = generate_composition_hash(drug_data.composition.dict())
        
        # Register on blockchain (build transaction) - optional
        blockchain_available = blockchain_service.is_connected()
        blockchain_result = None
        
        if blockchain_available:
            blockchain_result = await blockchain_service.register_drug(
                batch_id=drug_data.batchId,
                drug_name=drug_data.drugName,
                composition_hash=composition_hash,
                manufacture_date=drug_data.manufactureDate,
                expiry_date=drug_data.expiryDate,
                manufacturer_address=drug_data.manufacturerAddress
            )
            
            if not blockchain_result.get("success"):
                logger.warning(f"Blockchain registration failed: {blockchain_result.get('error')}")
                blockchain_available = False
        else:
            logger.warning("Blockchain service unavailable - registering drug in database only")
        
        # Store full composition in MongoDB (off-chain)
        composition_doc = {
            "batchId": drug_data.batchId,
            "drugName": drug_data.drugName,
            "fullComposition": drug_data.composition.dict(),
            "compositionHash": composition_hash,
            "manufacturer": drug_data.manufacturerAddress,
            "manufactureDate": drug_data.manufactureDate,
            "expiryDate": drug_data.expiryDate,
            "registrationTimestamp": datetime.utcnow(),
            "blockchainRegistered": blockchain_available
        }
        
        await db.drug_composition_storage.insert_one(composition_doc)
        
        # Store batch master record
        await db.drug_batches.insert_one({
            "batchId": drug_data.batchId,
            "drugName": drug_data.drugName,
            "manufacturer": drug_data.manufacturerAddress.lower(),
            "currentOwner": drug_data.manufacturerAddress.lower(),
            "status": "ACTIVE",
            "manufactureDate": drug_data.manufactureDate,
            "expiryDate": drug_data.expiryDate,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
            "blockchainRegistered": blockchain_available
        })

        
        logger.info(f"Drug registered: {drug_data.batchId} by {drug_data.manufacturerAddress} (blockchain: {blockchain_available})")
        
        message = "Drug registered successfully"
        if not blockchain_available:
            message += " (Database only - blockchain unavailable)"
        else:
            message += ". Sign the transaction in MetaMask."
        
        return {
            "success": True,
            "message": message,
            "batchId": drug_data.batchId,
            "compositionHash": composition_hash,
            "transactionHash": None,  # Will be set after user signs in frontend
            "blockchainAvailable": blockchain_available
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Drug registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Drug registration failed: {str(e)}"
        )


@router.get("/all")
async def get_all_drugs(db=Depends(get_database)):
    """Get all registered drug batches"""
    try:
        drugs_cursor = db.drug_batches.find({})
        drugs = await drugs_cursor.to_list(length=1000)

        for drug in drugs:
            drug.pop("_id", None)

        return drugs
    except Exception as e:
        logger.error(f"Failed to retrieve all drugs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve all drugs: {str(e)}"
        )


@router.get("/batch/{batch_id}", response_model=DrugInfo)
async def get_drug_by_batch(batch_id: str, db=Depends(get_database)):
    """Get details of a drug batch by batch ID"""
    try:
        drug = await db.drug_composition_storage.find_one({"batchId": batch_id})
        if not drug:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Batch ID {batch_id} not found"
            )

        drug.pop("_id", None)
        return drug
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve drug batch {batch_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve drug batch: {str(e)}"
        )


@router.post("/transfer", response_model=OwnershipTransferResponse)
async def transfer_ownership(
    transfer_data: OwnershipTransferRequest,
    db=Depends(get_database)
):
    """
    Transfer drug ownership to another party
    
    - **batchId**: Batch identifier
    - **fromAddress**: Current owner's wallet address
    - **toAddress**: New owner's wallet address
    - **location**: Transfer location
    """
    try:
        batch = await db.drug_batches.find_one({"batchId": transfer_data.batchId})

        if not batch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Batch ID not found"
            )

        # Validate users
        from_address = transfer_data.fromAddress.lower()
        to_address = transfer_data.toAddress.lower()

        from_user = await db.users.find_one({"walletAddress": from_address})
        to_user = await db.users.find_one({"walletAddress": to_address})

        if not from_user or not to_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or both users not found"
            )

        # Validate transfer chain
        from_role = from_user.get("role")
        to_role = to_user.get("role")

        valid_transfers = ["MANUFACTURER->DISTRIBUTOR", "DISTRIBUTOR->PHARMACY", "PHARMACY->CONSUMER"]
        transfer_key = f"{from_role}->{to_role}"

        if transfer_key not in valid_transfers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid transfer route for roles"
            )

        # Update current owner in DB
        await db.drug_batches.update_one(
            {"batchId": transfer_data.batchId},
            {
                "$set": {
                    "currentOwner": to_address,
                    "updatedAt": datetime.utcnow()
                }
            }
        )

        # Potentially store transfer history on blockchain and in DB (if implemented)
        return {
            "success": True,
            "message": "Ownership transfer recorded successfully",
            "batchId": transfer_data.batchId,
            "transactionHash": None
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ownership transfer error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ownership transfer failed: {str(e)}"
        )



        

        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ownership transfer error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ownership transfer failed: {str(e)}"
        )


@router.get("/all")
async def get_all_drugs(db=Depends(get_database)):
    """
    Get all registered drugs
    """
    try:
        drugs = await db.drug_composition_storage.find({}).to_list(length=None)
        
        # Remove MongoDB _id field
        for drug in drugs:
            drug.pop("_id", None)
        
        return drugs
        
    except Exception as e:
        logger.error(f"Get all drugs error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve drugs: {str(e)}"
        )


@router.get("/batch/{batch_id}")
async def get_drug_info(batch_id: str, db=Depends(get_database)):
    """
    Get complete drug information from MongoDB
    """
    try:
        drug = await db.drug_composition_storage.find_one({"batchId": batch_id})
        
        if not drug:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Batch ID not found"
            )
        
        # Remove MongoDB _id field
        drug.pop("_id", None)
        
        return {
            "success": True,
            "data": drug
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get drug info error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve drug info: {str(e)}"
        )
