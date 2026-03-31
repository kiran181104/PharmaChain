import React from 'react';
import DrugVerification from '../components/DrugVerification';
import blockchainService from '../services/blockchain';
import './ConsumerPage.css';

const ConsumerPage = ({ account }) => {
  const handleVerify = async (batchId) => {
    return await blockchainService.verifyDrugComplete(batchId);
  };

  return (
    <div className="consumer-page">
      <div className="consumer-header">
        <h1>🔍 Verify Your Medicine</h1>
        <p>Check if your medicine is genuine and safe to use</p>
      </div>

      <div className="container">
        <>
          <DrugVerification onVerify={handleVerify} />

          <div className="info-section">
            <h3>How to Verify</h3>
            <ol>
              <li>Find the batch ID on your medicine packaging.</li>
              <li>Enter the batch ID in the form on the left.</li>
              <li>Click "Verify Drug" and wait for results.</li>
              <li>Read status and history to ensure authenticity.</li>
            </ol>

            <div className="status-guide">
              <h4>Status Guide</h4>

              <div className="status-item">
                <span className="status-badge-sample genuine">✓ Genuine</span>
                <span>Authentic product from the supply chain.</span>
              </div>

              <div className="status-item">
                <span className="status-badge-sample fake">✗ Fake</span>
                <span>Counterfeit product. Do not consume.</span>
              </div>

              <div className="status-item">
                <span className="status-badge-sample expired">⚠ Expired</span>
                <span>Batch has exceeded expiry date.</span>
              </div>
            </div>

          </div>
        </>
      </div>
    </div>
  );
};

export default ConsumerPage;
