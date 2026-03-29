"""
Drug Verification Routes
Handles drug authenticity verification and traceability
"""
from fastapi import APIRouter, HTTPException, Depends, status
from app.schemas import DrugVerificationResponse, OwnershipRecord
from app.database import get_database
from app.utils import blockchain_service, verify_composition_hash
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/verify", tags=["Verification"])


@router.get("/{batch_id}", response_model=DrugVerificationResponse)
async def verify_drug(batch_id: str, db=Depends(get_database)):
    """
    Verify drug authenticity and get complete traceability
    
    Checks:
    - Drug exists on blockchain
    - Composition hash matches
    - Ownership chain is complete
    - Drug is not expired
    - No transfer anomalies
    
    Returns:
    - GENUINE: All checks passed
    - FAKE: Failed verification
    - EXPIRED: Drug past expiry date
    - INCOMPLETE_CHAIN: Missing ownership transfers
    """
    try:
        # Verify on blockchain
        blockchain_result = await blockchain_service.verify_drug(batch_id)
        
        if not blockchain_result.get("success"):
            return {
                "isGenuine": False,
                "status": "FAKE",
                "batchId": batch_id,
                "drugName": "Unknown",
                "manufacturer": "Unknown",
                "compositionHash": "",
                "currentOwner": "",
                "manufactureDate": 0,
                "expiryDate": 0,
                "transferCount": 0,
                "ownershipHistory": [],
                "anomalies": ["Batch ID not found on blockchain"]
            }
        
        # Get ownership history
        history_result = await blockchain_service.get_drug_history(batch_id)
        ownership_history = history_result.get("history", []) if history_result.get("success") else []
        
        # Get composition from MongoDB
        composition_data = await db.drug_composition_storage.find_one({"batchId": batch_id})
        
        # Analyze results
        anomalies = []
        status_text = "GENUINE"
        
        # Check if expired
        import time
        current_timestamp = int(time.time())
        
        if blockchain_result["expiryDate"] < current_timestamp:
            anomalies.append("Drug has expired")
            status_text = "EXPIRED"
        
        # Check ownership chain completeness
        if blockchain_result["transferCount"] < 2:
            anomalies.append("Incomplete ownership chain (expected: Manufacturer → Distributor → Pharmacy)")
        
        # Verify composition hash if available
        if composition_data:
            stored_hash = composition_data.get("compositionHash", "")
            blockchain_hash = blockchain_result.get("compositionHash", "")
            
            if stored_hash.lower() != blockchain_hash.lower():
                anomalies.append("Composition hash mismatch - possible tampering")
                status_text = "FAKE"
        
        # Check for role sequence anomalies
        for i in range(1, len(ownership_history)):
            if ownership_history[i]["fromRole"] == ownership_history[i]["toRole"]:
                anomalies.append(f"Suspicious transfer: same role transfer at index {i}")
        
        # Check for zero address transfers
        for record in ownership_history:
            if record["to"] == "0x0000000000000000000000000000000000000000":
                anomalies.append("Suspicious transfer to zero address detected")
                status_text = "FAKE"
        
        # Determine final status
        if len(anomalies) > 0 and status_text == "GENUINE":
            status_text = "INCOMPLETE_CHAIN"
        
        # Treat incomplete chain as still authentic (not overtly fake), but requiring transfer completion.
        is_genuine = status_text in ["GENUINE", "INCOMPLETE_CHAIN"]
        for record in ownership_history:
            formatted_history.append({
                "from": record["from"],
                "to": record["to"],
                "timestamp": record["timestamp"],
                "location": record["location"],
                "fromRole": record["fromRole"],
                "toRole": record["toRole"]
            })
        
        return {
            "isGenuine": is_genuine,
            "status": status_text,
            "batchId": batch_id,
            "drugName": blockchain_result.get("drugName", "Unknown"),
            "manufacturer": blockchain_result.get("manufacturer", "Unknown"),
            "compositionHash": blockchain_result.get("compositionHash", ""),
            "currentOwner": blockchain_result.get("currentOwner", ""),
            "manufactureDate": blockchain_result.get("manufactureDate", 0),
            "expiryDate": blockchain_result.get("expiryDate", 0),
            "transferCount": blockchain_result.get("transferCount", 0),
            "ownershipHistory": formatted_history,
            "composition": composition_data.get("fullComposition") if composition_data else None,
            "anomalies": anomalies
        }
        
    except Exception as e:
        logger.error(f"Drug verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Verification failed: {str(e)}"
        )


@router.get("/history/{batch_id}")
async def get_ownership_history(batch_id: str):
    """
    Get detailed ownership history for a drug batch
    """
    try:
        history_result = await blockchain_service.get_drug_history(batch_id)
        
        if not history_result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Batch ID not found or history unavailable"
            )
        
        return {
            "success": True,
            "batchId": batch_id,
            "history": history_result.get("history", [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get ownership history error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve ownership history: {str(e)}"
        )


@router.post("/batch-verify")
async def batch_verify_drugs(batch_ids: List[str], db=Depends(get_database)):
    """
    Verify multiple drug batches at once
    Useful for pharmacy bulk verification
    """
    try:
        results = []
        
        for batch_id in batch_ids:
            try:
                verification = await verify_drug(batch_id, db)
                results.append({
                    "batchId": batch_id,
                    "isGenuine": verification.isGenuine,
                    "status": verification.status
                })
            except Exception as e:
                results.append({
                    "batchId": batch_id,
                    "isGenuine": False,
                    "status": "ERROR",
                    "error": str(e)
                })
        
        return {
            "success": True,
            "totalBatches": len(batch_ids),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Batch verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch verification failed: {str(e)}"
        )
