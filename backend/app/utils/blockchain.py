"""
Blockchain Interaction Utilities using Web3.py
Handles all smart contract interactions
"""
from web3 import Web3
from web3.middleware import geth_poa_middleware
from typing import Dict, Any, List, Optional
import json
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class BlockchainService:
    """
    Service for interacting with Ethereum blockchain and smart contracts
    """
    
    def __init__(self):
        """Initialize Web3 connection and contract"""
        self.w3 = None
        self.contract = None
        self.contract_address = None
        self.account = None
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialize Web3 connection to blockchain"""
        try:
            # Connect to blockchain provider (Ganache/local node)
            self.w3 = Web3(Web3.HTTPProvider(settings.BLOCKCHAIN_PROVIDER_URL))
        
            # Add PoA middleware for Ganache / PoA chains
            from web3.middleware import geth_poa_middleware
            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
            
            # Check connection (handle both Web3.py version differences)
            try:
                is_connected = self.w3.is_connected()
            except AttributeError:
                # Fallback for older Web3 versions
                is_connected = self.w3.isConnected()
            
            if not is_connected:
                raise ConnectionError("Failed to connect to blockchain")
            
            logger.info(f"Connected to blockchain at {settings.BLOCKCHAIN_PROVIDER_URL}")
            
            # Set contract address
            self.contract_address = settings.CONTRACT_ADDRESS
            
            # Load contract ABI and initialize contract
            if self.contract_address:
                self._load_contract()
            
        except Exception as e:
            logger.error(f"Blockchain initialization error: {str(e)}")
            raise

    
    def _load_contract(self):
        """Load smart contract ABI and create contract instance"""
        try:
            # Contract ABI (simplified - load from file in production)
            contract_abi = self._get_contract_abi()
            
            # Create contract instance
            self.contract = self.w3.eth.contract(
                address=Web3.toChecksumAddress(self.contract_address),
                abi=contract_abi
            )
            
            logger.info(f"Contract loaded at address: {self.contract_address}")
            
        except Exception as e:
            logger.error(f"Contract loading error: {str(e)}")
            raise
    
    def _get_contract_abi(self) -> List[Dict]:
        """
        Get contract ABI
        Load from the truffle build file
        """
        import json
        import os
        
        try:
            # Path to the contract build file
            contract_build_path = os.path.join(
                os.path.dirname(__file__), 
                '..', '..', '..', 'blockchain', 'build', 'contracts', 'DrugTraceability.json'
            )
            
            with open(contract_build_path, 'r') as f:
                contract_data = json.load(f)
                return contract_data['abi']
                
        except Exception as e:
            logger.error(f"Failed to load contract ABI: {str(e)}")
            # Fallback to minimal ABI if file not found
            return [
                {
                    "inputs": [{"internalType": "string", "name": "_batchId", "type": "string"}],
                    "name": "verifyDrug",
                    "outputs": [
                        {"internalType": "bool", "name": "isGenuine", "type": "bool"},
                        {"internalType": "string", "name": "drugName", "type": "string"},
                        {"internalType": "address", "name": "manufacturer", "type": "address"},
                        {"internalType": "string", "name": "compositionHash", "type": "string"},
                        {"internalType": "uint256", "name": "manufactureDate", "type": "uint256"},
                        {"internalType": "uint256", "name": "expiryDate", "type": "uint256"},
                        {"internalType": "address", "name": "currentOwner", "type": "address"},
                        {"internalType": "uint256", "name": "transferCount", "type": "uint256"}
                    ],
                    "stateMutability": "view",
                    "type": "function"
                }
            ]
    
    async def register_user(
        self,
        wallet_address: str,
        role: str,
        name: str
    ) -> Dict[str, Any]:
        """
        Register a user on the blockchain using contract owner's account
        
        Args:
            wallet_address: User's wallet address
            role: User's role (MANUFACTURER=1, DISTRIBUTOR=2, PHARMACY=3, CONSUMER=4, REGULATOR=5)
            name: User's name or organization name
            
        Returns:
            Transaction receipt dictionary
        """
        try:
            # Map role string to enum value
            role_map = {
                "MANUFACTURER": 1,
                "DISTRIBUTOR": 2,
                "PHARMACY": 3,
                "CONSUMER": 4,
                "REGULATOR": 5
            }
            role_enum = role_map.get(role.upper(), 0)
            
            if role_enum == 0:
                return {
                    'success': False,
                    'error': f'Invalid role: {role}'
                }
            
            # Get contract owner account from private key
            if not settings.PRIVATE_KEY:
                return {
                    'success': False,
                    'error': 'Contract owner private key not configured'
                }
            
            contract_owner = self.w3.eth.account.from_key(settings.PRIVATE_KEY)
            
            # Build transaction from contract owner's account
            transaction = self.contract.functions.registerUser(
                Web3.toChecksumAddress(wallet_address),
                role_enum,
                name
            ).build_transaction({
                'from': contract_owner.address,
                'nonce': self.w3.eth.get_transaction_count(contract_owner.address),
                'gas': 300000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            # Sign transaction with contract owner's private key
            signed_tx = self.w3.eth.account.sign_transaction(transaction, settings.PRIVATE_KEY)
            
            # Send signed transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # Wait for transaction receipt
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)
            
            logger.info(f"User registered on blockchain: {wallet_address} as {role}")
            
            return {
                'success': True,
                'transactionHash': tx_receipt['transactionHash'].hex(),
                'blockNumber': tx_receipt['blockNumber'],
                'message': 'User registered on blockchain'
            }
            
        except Exception as e:
            logger.error(f"User blockchain registration error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def is_user_registered(self, wallet_address: str) -> bool:
        """
        Check if user is registered on the blockchain
        
        Args:
            wallet_address: User's wallet address
            
        Returns:
            True if registered, False otherwise
        """
        try:
            result = self.contract.functions.getUser(
                Web3.toChecksumAddress(wallet_address)
            ).call()
            
            # result[3] is the isRegistered boolean
            return result[3]
            
        except Exception as e:
            logger.error(f"User registration check error: {str(e)}")
            return False
    
    async def register_drug(
        self,
        batch_id: str,
        drug_name: str,
        composition_hash: str,
        manufacture_date: int,
        expiry_date: int,
        manufacturer_address: str
    ) -> Dict[str, Any]:
        """
        Register a new drug on the blockchain
        
        Args:
            batch_id: Unique batch identifier
            drug_name: Name of the drug
            composition_hash: SHA-256 hash of composition
            manufacture_date: Manufacturing date (Unix timestamp)
            expiry_date: Expiry date (Unix timestamp)
            manufacturer_address: Manufacturer's wallet address
            
        Returns:
            Transaction receipt dictionary
        """
        try:
            # Build transaction
            transaction = self.contract.functions.registerDrug(
                batch_id,
                drug_name,
                composition_hash,
                manufacture_date,
                expiry_date
            ).build_transaction({
                'from': Web3.toChecksumAddress(manufacturer_address),
                'nonce': self.w3.eth.get_transaction_count(
                    Web3.toChecksumAddress(manufacturer_address)
                ),
                'gas': 3000000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            return {
                'success': True,
                'transaction': transaction,
                'message': 'Transaction built successfully'
            }
            
        except Exception as e:
            logger.error(f"Drug registration error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def transfer_ownership(
        self,
        batch_id: str,
        new_owner: str,
        location: str,
        current_owner: str
    ) -> Dict[str, Any]:
        """
        Transfer drug ownership on the blockchain
        
        Args:
            batch_id: Batch identifier
            new_owner: New owner's wallet address
            location: Transfer location
            current_owner: Current owner's wallet address
            
        Returns:
            Transaction receipt dictionary
        """
        try:
            # Build transaction
            transaction = self.contract.functions.transferOwnership(
                batch_id,
                Web3.toChecksumAddress(new_owner),
                location
            ).build_transaction({
                'from': Web3.toChecksumAddress(current_owner),
                'nonce': self.w3.eth.get_transaction_count(
                    Web3.toChecksumAddress(current_owner)
                ),
                'gas': 2000000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            return {
                'success': True,
                'transaction': transaction,
                'message': 'Transaction built successfully'
            }
            
        except Exception as e:
            logger.error(f"Ownership transfer error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def verify_drug(self, batch_id: str) -> Dict[str, Any]:
        """
        Verify drug authenticity from blockchain
        
        Args:
            batch_id: Batch identifier
            
        Returns:
            Verification result dictionary
        """
        try:
            # Call contract view function
            result = self.contract.functions.verifyDrug(batch_id).call()
            
            return {
                'success': True,
                'isGenuine': result[0],
                'drugName': result[1],
                'manufacturer': result[2],
                'compositionHash': result[3],
                'manufactureDate': result[4],
                'expiryDate': result[5],
                'currentOwner': result[6],
                'transferCount': result[7]
            }
            
        except Exception as e:
            logger.error(f"Drug verification error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_drug_history(self, batch_id: str) -> Dict[str, Any]:
        """
        Get complete ownership history from blockchain
        
        Args:
            batch_id: Batch identifier
            
        Returns:
            Ownership history list
        """
        try:
            # Call contract view function
            history = self.contract.functions.getDrugHistory(batch_id).call()
            
            # Convert to readable format
            formatted_history = []
            for record in history:
                formatted_history.append({
                    'from': record[0],
                    'to': record[1],
                    'timestamp': record[2],
                    'location': record[3],
                    'fromRole': self._role_enum_to_string(record[4]),
                    'toRole': self._role_enum_to_string(record[5])
                })
            
            return {
                'success': True,
                'history': formatted_history
            }
            
        except Exception as e:
            logger.error(f"History retrieval error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _role_enum_to_string(self, role_num: int) -> str:
        """Convert role enum number to string"""
        roles = {
            0: "NONE",
            1: "MANUFACTURER",
            2: "DISTRIBUTOR",
            3: "PHARMACY",
            4: "CONSUMER",
            5: "REGULATOR"
        }
        return roles.get(role_num, "UNKNOWN")


# Global blockchain service instance
blockchain_service = BlockchainService()
