import React, { useState } from 'react';
import DrugRegistration from '../components/DrugRegistration';
import blockchainService from '../services/blockchain';
import './Dashboard.css';

const ManufacturerDashboard = ({ account }) => {
  const [transferData, setTransferData] = useState({ batchId: '', distributorAddress: '', location: '' });
  const [transferLoading, setTransferLoading] = useState(false);
  const [transferError, setTransferError] = useState('');
  const [transferSuccess, setTransferSuccess] = useState('');

  const handleRegister = async (drugData) => {
    return await blockchainService.registerDrugComplete(drugData);
  };

  const handleDistributorTransfer = async (e) => {
    e.preventDefault();
    setTransferLoading(true);
    setTransferError('');
    setTransferSuccess('');

    try {
      await blockchainService.transferOwnershipComplete(
        transferData.batchId,
        transferData.distributorAddress,
        transferData.location
      );
      setTransferSuccess('Batch transferred to distributor successfully.');
      setTransferData({ batchId: '', distributorAddress: '', location: '' });
    } catch (err) {
      setTransferError(err.message || 'Failed to transfer to distributor');
    } finally {
      setTransferLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="dashboard">
        <h2>🏭 Manufacturer Dashboard</h2>
        <p className="dashboard-subtitle">Register new drugs and manage your inventory</p>
        <DrugRegistration onRegister={handleRegister} />

        <div className="transfer-section">
          <h3>Transfer to Distributor</h3>
          <p>Add distributor address to route the batch from manufacturer → distributor</p>

          {transferError && <div className="error-message">{transferError}</div>}
          {transferSuccess && <div className="success-message">{transferSuccess}</div>}

          <form onSubmit={handleDistributorTransfer} className="transfer-form">
            <div className="form-group">
              <label>Batch ID</label>
              <input
                type="text"
                value={transferData.batchId}
                onChange={(e) => setTransferData({ ...transferData, batchId: e.target.value })}
                required
                placeholder="e.g., BATCH001"
              />
            </div>
            <div className="form-group">
              <label>Distributor Address</label>
              <input
                type="text"
                value={transferData.distributorAddress}
                onChange={(e) => setTransferData({ ...transferData, distributorAddress: e.target.value })}
                required
                placeholder="0x..."
              />
            </div>
            <div className="form-group">
              <label>Location</label>
              <input
                type="text"
                value={transferData.location}
                onChange={(e) => setTransferData({ ...transferData, location: e.target.value })}
                required
                placeholder="e.g., Mumbai Distribution Center"
              />
            </div>
            <button type="submit" className="btn" disabled={transferLoading}>
              {transferLoading ? 'Transferring...' : 'Transfer to Distributor'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ManufacturerDashboard;
