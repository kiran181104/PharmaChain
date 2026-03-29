import Web3 from 'web3';

const CONTRACT_ADDRESS = process.env.REACT_APP_CONTRACT_ADDRESS;
const NETWORK_ID = process.env.REACT_APP_BLOCKCHAIN_NETWORK_ID || '5777';

// Minimal contract ABI - add more functions as needed
const CONTRACT_ABI = [
  {
    "inputs": [
      {"internalType": "string", "name": "_batchId", "type": "string"},
      {"internalType": "string", "name": "_drugName", "type": "string"},
      {"internalType": "string", "name": "_compositionHash", "type": "string"},
      {"internalType": "uint256", "name": "_manufactureDate", "type": "uint256"},
      {"internalType": "uint256", "name": "_expiryDate", "type": "uint256"}
    ],
    "name": "registerDrug",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {"internalType": "string", "name": "_batchId", "type": "string"},
      {"internalType": "address", "name": "_newOwner", "type": "address"},
      {"internalType": "string", "name": "_location", "type": "string"}
    ],
    "name": "transferOwnership",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
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
  },
  {
    "inputs": [{"internalType": "string", "name": "_batchId", "type": "string"}],
    "name": "getDrugHistory",
    "outputs": [
      {
        "components": [
          {"internalType": "address", "name": "from", "type": "address"},
          {"internalType": "address", "name": "to", "type": "address"},
          {"internalType": "uint256", "name": "timestamp", "type": "uint256"},
          {"internalType": "string", "name": "location", "type": "string"},
          {"internalType": "uint8", "name": "fromRole", "type": "uint8"},
          {"internalType": "uint8", "name": "toRole", "type": "uint8"}
        ],
        "internalType": "struct DrugTraceability.OwnershipRecord[]",
        "name": "",
        "type": "tuple[]"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [{"internalType": "string", "name": "_batchId", "type": "string"}],
    "name": "getDrug",
    "outputs": [
      {"internalType": "string", "name": "batchId", "type": "string"},
      {"internalType": "string", "name": "drugName", "type": "string"},
      {"internalType": "address", "name": "manufacturer", "type": "address"},
      {"internalType": "string", "name": "compositionHash", "type": "string"},
      {"internalType": "uint256", "name": "manufactureDate", "type": "uint256"},
      {"internalType": "uint256", "name": "expiryDate", "type": "uint256"},
      {"internalType": "address", "name": "currentOwner", "type": "address"},
      {"internalType": "uint256", "name": "registrationTimestamp", "type": "uint256"}
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [{"internalType": "string", "name": "_batchId", "type": "string"}],
    "name": "doesBatchExist",
    "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
    "stateMutability": "view",
    "type": "function"
  }
];

class Web3Service {
  constructor() {
    this.web3 = null;
    this.contract = null;
    this.account = null;
  }

  /**
   * Initialize Web3 and connect to MetaMask
   */
  async init() {
    if (!window.ethereum) {
      throw new Error('MetaMask is not installed. Please install MetaMask.');
    }

    try {
      this.web3 = new Web3(window.ethereum);
      
      // Request account access
      const accounts = await window.ethereum.request({ 
        method: 'eth_requestAccounts' 
      });
      
      if (accounts.length === 0) {
        throw new Error('No accounts found. Please unlock MetaMask.');
      }
      
      this.account = accounts[0];
      console.log('Web3 initialized with account:', this.account);

      // Initialize contract
      if (CONTRACT_ADDRESS) {
        this.contract = new this.web3.eth.Contract(
          CONTRACT_ABI,
          CONTRACT_ADDRESS
        );
        console.log('Contract initialized at:', CONTRACT_ADDRESS);
      } else {
        console.warn('Contract address not set in environment variables');
      }

      return {
        web3: this.web3,
        contract: this.contract,
        account: this.account
      };
    } catch (error) {
      console.error('Web3 initialization error:', error);
      throw error;
    }
  }

  /**
   * Get current account
   */
  getAccount() {
    return this.account;
  }

  /**
   * Register drug on blockchain
   */
  async registerDrug(batchId, drugName, compositionHash, manufactureDate, expiryDate) {
  if (!this.contract) {
    console.warn("Contract not initialized, initializing now...");
    await this.init();
  }

  const tx = await this.contract.methods
    .registerDrug(
      batchId,
      drugName,
      compositionHash,
      manufactureDate,
      expiryDate
    )
    .send({ from: this.account });

  return {
    success: true,
    transactionHash: tx.transactionHash,
    blockNumber: tx.blockNumber
  };
}


  /**
   * Transfer drug ownership
   */
  async transferOwnership(batchId, newOwner, location) {
    if (!this.contract) {
      throw new Error('Contract not initialized');
    }

    try {
      const tx = await this.contract.methods
        .transferOwnership(batchId, newOwner, location)
        .send({ from: this.account });
      
      return {
        success: true,
        transactionHash: tx.transactionHash,
        blockNumber: tx.blockNumber
      };
    } catch (error) {
      console.error('Transfer ownership error:', error);
      throw error;
    }
  }

  /**
   * Check if batch exists on blockchain
   */
  async doesBatchExist(batchId) {
    try {
      if (!this.contract) {
        await this.init();
        if (!this.contract) {
          return false;
        }
      }

      const exists = await this.contract.methods.doesBatchExist(batchId).call();
      return exists;
    } catch (error) {
      console.error('doesBatchExist error:', error);
      return false;
    }
  }

  /**
   * Verify drug on blockchain
   */
  async verifyDrug(batchId) {
    try {
      if (!this.contract) {
        // Try to initialize if not set
        await this.init();
        if (!this.contract) {
          return {
            isGenuine: false,
            drugName: null,
            manufacturer: null,
            compositionHash: null,
            manufactureDate: 0,
            expiryDate: 0,
            currentOwner: null,
            transferCount: 0,
            error: 'Contract not initialized'
          };
        }
      }

      const exists = await this.doesBatchExist(batchId);
      if (!exists) {
        return {
          isGenuine: false,
          drugName: null,
          manufacturer: null,
          compositionHash: null,
          manufactureDate: 0,
          expiryDate: 0,
          currentOwner: null,
          transferCount: 0,
          error: 'Drug batch does not exist on-chain'
        };
      }

      const result = await this.contract.methods
        .verifyDrug(batchId)
        .call();

      return {
        isGenuine: result[0],
        drugName: result[1],
        manufacturer: result[2],
        compositionHash: result[3],
        manufactureDate: parseInt(result[4]),
        expiryDate: parseInt(result[5]),
        currentOwner: result[6],
        transferCount: parseInt(result[7])
      };
    } catch (error) {
      console.error('Verify drug error:', error);
      return {
        isGenuine: false,
        drugName: null,
        manufacturer: null,
        compositionHash: null,
        manufactureDate: 0,
        expiryDate: 0,
        currentOwner: null,
        transferCount: 0,
        error: error.message || 'Blockchain call failed'
      };
    }
  }

  /**
   * Get drug ownership history
   */
  async getDrugHistory(batchId) {
    if (!this.contract) {
      throw new Error('Contract not initialized');
    }

    try {
      const history = await this.contract.methods
        .getDrugHistory(batchId)
        .call();
      
      return history.map(record => ({
        from: record.from || record[0],
        to: record.to || record[1],
        timestamp: parseInt(record.timestamp || record[2]),
        location: record.location || record[3],
        fromRole: this.getRoleName(record.fromRole || record[4]),
        toRole: this.getRoleName(record.toRole || record[5])
      }));
    } catch (error) {
      console.error('Get drug history error:', error);
      throw error;
    }
  }

  /**
   * Get drug details from blockchain
   */
  async getDrug(batchId) {
    if (!this.contract) {
      throw new Error('Contract not initialized');
    }

    try {
      const result = await this.contract.methods
        .getDrug(batchId)
        .call();
      
      return {
        batchId: result[0],
        drugName: result[1],
        manufacturer: result[2],
        compositionHash: result[3],
        manufactureDate: parseInt(result[4]),
        expiryDate: parseInt(result[5]),
        currentOwner: result[6],
        registrationTimestamp: parseInt(result[7])
      };
    } catch (error) {
      console.error('Get drug error:', error);
      throw error;
    }
  }

  /**
   * Check if batch exists
   */
  async doesBatchExist(batchId) {
    if (!this.contract) {
      throw new Error('Contract not initialized');
    }

    try {
      return await this.contract.methods
        .doesBatchExist(batchId)
        .call();
    } catch (error) {
      console.error('Check batch existence error:', error);
      return false;
    }
  }

  /**
   * Convert role enum to string
   */
  getRoleName(roleNum) {
    const roles = {
      0: 'NONE',
      1: 'MANUFACTURER',
      2: 'DISTRIBUTOR',
      3: 'PHARMACY',
      4: 'CONSUMER',
      5: 'REGULATOR'
    };
    return roles[roleNum] || 'UNKNOWN';
  }

  /**
   * Format timestamp to readable date
   */
  formatTimestamp(timestamp) {
    return new Date(timestamp * 1000).toLocaleString();
  }

  /**
   * Shorten address for display
   */
  shortenAddress(address) {
    if (!address) return '';
    return `${address.substring(0, 6)}...${address.substring(address.length - 4)}`;
  }
}

// Export singleton instance
const web3Service = new Web3Service();
export default web3Service;