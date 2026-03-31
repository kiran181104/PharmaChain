"""
Audit and Monitoring Routes (Regulator Only)
Handles system-wide auditing and anomaly detection
"""
from fastapi import APIRouter, HTTPException, Depends, status
from app.schemas import AuditResult, AuditStatistics
from app.database import get_database
from app.utils import blockchain_service
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/audit", tags=["Audit"])


@router.get("/statistics", response_model=AuditStatistics)
async def get_audit_statistics(db=Depends(get_database)):
    """
    Get system-wide statistics for regulators
    
    Returns:
    - Total drugs registered
    - Total users
    - Total transfers
    - Drugs with anomalies
    - Expired drugs
    """
    try:
        # Get total counts from MongoDB
        total_drugs_db = await db.drug_composition_storage.count_documents({})
        total_users = await db.users.count_documents({})
        
        # Get all drug batches and check for anomalies
        drugs_cursor = db.drug_composition_storage.find({})
        drugs = await drugs_cursor.to_list(length=1000)
        
        drugs_with_anomalies = 0
        expired_drugs = 0
        
        import time
        current_timestamp = int(time.time())
        
        for drug in drugs:
            batch_id = drug.get("batchId")
            
            # Check expiry
            if drug.get("expiryDate", 0) < current_timestamp:
                expired_drugs += 1
            
            # Verify on blockchain to check for anomalies
            try:
                verification = await blockchain_service.verify_drug(batch_id)
                
                if verification.get("success"):
                    # Check for incomplete chain
                    if verification.get("transferCount", 0) < 2:
                        drugs_with_anomalies += 1
                else:
                    error_msg = verification.get("error", "")
                    if "service unavailable" in error_msg.lower() or "cannot connect" in error_msg.lower() or "connection" in error_msg.lower():
                        # Skip anomaly when blockchain is temporarily unavailable
                        continue
                    drugs_with_anomalies += 1
            except Exception as e:
                # If blockchain is unreachable, continue and don't count as anomaly.
                logger.warning(f"Blockchain check failed for {batch_id}: {str(e)}")
                continue
        
        return {
            "totalDrugs": total_drugs_db,
            "totalUsers": total_users,
            "totalTransfers": 0,  # Would need to sum from blockchain
            "drugsWithAnomalies": drugs_with_anomalies,
            "expiredDrugs": expired_drugs
        }
        
    except Exception as e:
        logger.error(f"Get audit statistics error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve audit statistics: {str(e)}"
        )


@router.get("/anomalies", response_model=List[AuditResult])
async def get_drugs_with_anomalies(db=Depends(get_database)):
    """
    Get all drugs with detected anomalies
    
    Anomalies include:
    - Expired drugs
    - Incomplete ownership chains
    - Suspicious transfers
    - Hash mismatches
    """
    try:
        anomalous_drugs = []
        
        # Get all drugs
        drugs_cursor = db.drug_composition_storage.find({})
        drugs = await drugs_cursor.to_list(length=1000)
        
        import time
        current_timestamp = int(time.time())
        
        for drug in drugs:
            batch_id = drug.get("batchId")
            has_anomaly = False
            anomaly_type = "None"
            
            # Check expiry
            if drug.get("expiryDate", 0) < current_timestamp:
                has_anomaly = True
                anomaly_type = "Expired"
            
            # Verify on blockchain
            try:
                verification = await blockchain_service.verify_drug(batch_id)
                
                if verification.get("success"):
                    transfer_count = verification.get("transferCount", 0)
                    
                    # Check for incomplete chain (but only if batch has been transferred at least once)
                    if transfer_count > 0 and transfer_count < 2 and not has_anomaly:
                        has_anomaly = True
                        anomaly_type = "Incomplete ownership chain"
                    
                    if has_anomaly:
                        anomalous_drugs.append({
                            "batchId": batch_id,
                            "hasAnomalies": True,
                            "anomalyType": anomaly_type,
                            "ownershipCount": transfer_count,
                            "drugName": drug.get("drugName", "Unknown"),
                            "manufacturer": drug.get("manufacturer", "Unknown"),
                            "currentOwner": verification.get("currentOwner", "Unknown")
                        })
                else:
                    # Skip marking as anomaly on blockchain service unavailability
                    error_msg = verification.get("error", "")
                    if "service unavailable" in error_msg.lower() or "cannot connect" in error_msg.lower() or "connection" in error_msg.lower():
                        logger.info(f"Blockchain unavailable, skipping anomaly for {batch_id}: {error_msg}")
                        continue

                    # Skip newly registered batches (not yet on blockchain) - only flag as anomaly if they should exist on blockchain
                    # Check if batch has been transferred (should have records in ownership history)
                    batch_record = await db.drug_batches.find_one({"batchId": batch_id})
                    if batch_record and batch_record.get("transferCount", 0) == 0:
                        # Batch exists but hasn't been transferred yet - this is normal, skip it
                        logger.info(f"Batch {batch_id} is newly registered with no transfers, skipping anomaly")
                        continue

                    anomalous_drugs.append({
                        "batchId": batch_id,
                        "hasAnomalies": True,
                        "anomalyType": "Blockchain verification failed",
                        "ownershipCount": 0,
                        "drugName": drug.get("drugName", "Unknown"),
                        "manufacturer": drug.get("manufacturer", "Unknown"),
                        "currentOwner": "Unknown"
                    })
            except Exception as verify_error:
                logger.warning(f"Verification error for {batch_id}: {str(verify_error)}")
                continue
        
        return anomalous_drugs
        
    except Exception as e:
        logger.error(f"Get anomalies error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve anomalies: {str(e)}"
        )


@router.get("/expired-drugs")
async def get_expired_drugs(db=Depends(get_database)):
    """
    Get list of all expired drugs
    """
    try:
        import time
        current_timestamp = int(time.time())
        
        # Find expired drugs
        expired_drugs_cursor = db.drug_composition_storage.find({
            "expiryDate": {"$lt": current_timestamp}
        })
        
        expired_drugs = await expired_drugs_cursor.to_list(length=1000)
        
        result = []
        for drug in expired_drugs:
            drug.pop("_id", None)
            result.append({
                "batchId": drug.get("batchId"),
                "drugName": drug.get("drugName"),
                "manufacturer": drug.get("manufacturer"),
                "expiryDate": drug.get("expiryDate"),
                "daysExpired": (current_timestamp - drug.get("expiryDate", 0)) // 86400
            })
        
        return {
            "success": True,
            "count": len(result),
            "expiredDrugs": result
        }
        
    except Exception as e:
        logger.error(f"Get expired drugs error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve expired drugs: {str(e)}"
        )


@router.get("/user-activity/{wallet_address}")
async def get_user_activity(wallet_address: str, db=Depends(get_database)):
    """
    Get activity log for a specific user (for auditing)
    """
    try:
        user = await db.users.find_one({"walletAddress": wallet_address})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Find all drugs registered by this manufacturer
        if user.get("role") == "MANUFACTURER":
            drugs_cursor = db.drug_composition_storage.find({
                "manufacturer": wallet_address
            })
            drugs = await drugs_cursor.to_list(length=1000)
            
            return {
                "success": True,
                "walletAddress": wallet_address,
                "role": user.get("role"),
                "totalDrugsRegistered": len(drugs),
                "drugs": [
                    {
                        "batchId": d.get("batchId"),
                        "drugName": d.get("drugName"),
                        "registrationTimestamp": d.get("registrationTimestamp")
                    }
                    for d in drugs
                ]
            }
        else:
            return {
                "success": True,
                "walletAddress": wallet_address,
                "role": user.get("role"),
                "message": "Activity tracking for this role not yet implemented"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user activity error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user activity: {str(e)}"
        )
