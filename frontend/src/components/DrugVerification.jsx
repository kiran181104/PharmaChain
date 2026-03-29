import React, { useState } from 'react';
import Button from './common/Button';
import StatusBadge from './common/StatusBadge';
import { formatTimestamp, shortenAddress } from '../utils/helpers';
import { getDrugInfo, getAllDrugs, verifyDrug } from '../services/api';
import './DrugVerification.css';

const DrugVerification = ({ onVerify }) => {
  const [batchId, setBatchId] = useState('');
  const [drug, setDrug] = useState(null);
  const [verification, setVerification] = useState(null);
  const [loading, setLoading] = useState(false);
  const [verifying, setVerifying] = useState(false);
  const [error, setError] = useState('');
  const [allDrugs, setAllDrugs] = useState([]);

  const handleLookup = async () => {
    if (!batchId.trim()) {
      setError('Please enter a batch ID to search.');
      return;
    }

    setLoading(true);
    setError('');
    setDrug(null);
    setVerification(null);

    try {
      const response = await getDrugInfo(batchId.trim());
      // backend may return { success: true, data: ... } or direct object
      const drugData = response?.data ?? response;
      if (!drugData || !drugData.batchId) {
        throw new Error('Invalid drug data response');
      }
      setDrug(drugData);
    } catch (err) {
      console.error('Error fetching drug info:', err);

      if (err.response && err.response.status === 404) {
        setError(`Batch ID '${batchId.trim()}' not found.`);
      } else {
        setError('Failed to load drug details. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyClick = async () => {
    if (!batchId.trim()) {
      setError('Please enter a batch ID first.');
      return;
    }

    setVerifying(true);
    setError('');

    try {
      const result = onVerify ? await onVerify(batchId.trim()) : await verifyDrug(batchId.trim());
      setVerification(result);
    } catch (err) {
      console.error('Verification error:', err);
      setError('Verification request failed. Please check batch ID and try again.');
    } finally {
      setVerifying(false);
    }
  };

  const handleFetchAllDrugs = async () => {
    setError('');
    try {
      const response = await getAllDrugs();
      setAllDrugs(response || []);
    } catch (err) {
      console.error('Failed to fetch all drugs:', err);
      setError('Could not load registered drugs.');
    }
  };

  return (
    <div className="drug-verification">
      <h3>Verify Drug Authenticity</h3>

      <div className="verification-input">
        <label htmlFor="batchId">Batch ID</label>
        <input
          id="batchId"
          type="text"
          value={batchId}
          onChange={(e) => setBatchId(e.target.value)}
          placeholder="Enter batch ID (e.g., BATCH001)"
        />

        <div className="button-group">
          <Button onClick={handleLookup} loading={loading} size="small">
            {loading ? 'Searching...' : 'Load Drug Details'}
          </Button>
          <Button onClick={handleVerifyClick} loading={verifying} size="small">
            {verifying ? 'Verifying...' : 'Verify Drug'}
          </Button>
          <Button onClick={handleFetchAllDrugs} size="small">
            Show All Registered Drugs
          </Button>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      {drug && (
        <div className="drug-details-card">
          <h4>Drug Information</h4>
          <div className="detail-row">
            <span className="label">Batch ID:</span>
            <span className="value">{drug.batchId}</span>
          </div>
          <div className="detail-row">
            <span className="label">Drug Name:</span>
            <span className="value">{drug.drugName}</span>
          </div>
          <div className="detail-row">
            <span className="label">Manufacturer:</span>
            <span className="value" title={drug.manufacturer}>{shortenAddress(drug.manufacturer)}</span>
          </div>
          <div className="detail-row">
            <span className="label">Manufacture Date:</span>
            <span className="value">{formatTimestamp(drug.manufactureDate)}</span>
          </div>
          <div className="detail-row">
            <span className="label">Expiry Date:</span>
            <span className="value">{formatTimestamp(drug.expiryDate)}</span>
          </div>
          <div className="detail-row">
            <span className="label">Composition Hash:</span>
            <span className="value">{drug.compositionHash}</span>
          </div>
        </div>
      )}

      {allDrugs.length > 0 && (
        <div className="all-drugs-list">
          <h4>All Registered Drugs</h4>
          <div className="drugs-table">
            <div className="table-header">
              <span>Batch ID</span>
              <span>Drug Name</span>
              <span>Manufacturer</span>
              <span>Expiry Date</span>
            </div>
            {allDrugs.map((item) => (
              <div key={item.batchId} className="table-row">
                <span>{item.batchId}</span>
                <span>{item.drugName}</span>
                <span>{shortenAddress(item.manufacturer)}</span>
                <span>{item.expiryDate ? formatTimestamp(item.expiryDate) : 'N/A'}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {verification && (
        <div className="verification-result">
          <h3 className="verification-status">
            {verification.status === 'GENUINE' && '✔✔ GENUINE'}
            {verification.status === 'EXPIRED' && '⚠ EXPIRED'}
            {verification.status === 'INCOMPLETE_CHAIN' && '⚠ INCOMPLETE CHAIN'}
            {verification.status === 'FAKE' && '✖ FAKE'}
            {!['GENUINE','EXPIRED','INCOMPLETE_CHAIN','FAKE'].includes(verification.status) && '? UNKNOWN'}
          </h3>
          <div className="drug-information-card">
            <h4>Drug Information</h4>
            <div className="detail-row">
              <span className="label">Batch ID:</span>
              <span className="value">{batchId}</span>
            </div>
            <div className="detail-row">
              <span className="label">Drug Name:</span>
              <span className="value">{verification.drugName || drug?.drugName || 'N/A'}</span>
            </div>
            <div className="detail-row">
              <span className="label">Manufacturer:</span>
              <span className="value" title={verification.manufacturer || drug?.manufacturer || ''}>
                {verification.manufacturer ? shortenAddress(verification.manufacturer) : drug?.manufacturer ? shortenAddress(drug.manufacturer) : 'N/A'}
              </span>
            </div>
            <div className="detail-row">
              <span className="label">Current Owner:</span>
              <span className="value" title={verification.currentOwner || ''}>
                {verification.currentOwner ? shortenAddress(verification.currentOwner) : 'N/A'}
              </span>
            </div>
            <div className="detail-row">
              <span className="label">Manufacture Date:</span>
              <span className="value">{verification.manufactureDate ? formatTimestamp(verification.manufactureDate) : drug?.manufactureDate ? formatTimestamp(drug.manufactureDate) : 'N/A'}</span>
            </div>
            <div className="detail-row">
              <span className="label">Expiry Date:</span>
              <span className="value">{verification.expiryDate ? formatTimestamp(verification.expiryDate) : drug?.expiryDate ? formatTimestamp(drug.expiryDate) : 'N/A'}</span>
            </div>
            <div className="detail-row">
              <span className="label">Total Transfers:</span>
              <span className="value">{verification.transferCount ?? 'N/A'}</span>
            </div>
          </div>

          {verification.anomalies && verification.anomalies.length > 0 && (
            <div className="anomalies">
              <h5>Anomalies</h5>
              <ul>
                {verification.anomalies.map((item, i) => (
                  <li key={i}>{item}</li>
                ))}
              </ul>
            </div>
          )}

          {verification.ownershipHistory && verification.ownershipHistory.length > 0 && (
            <div className="ownership-history">
              <h4>Complete Ownership History (starts from MANUFACTURER)</h4>
              {verification.ownershipHistory.map((record, index) => (
                <div key={index} className="history-record">
                  <div className="history-row">
                    <span className="history-step">#{index + 1}</span>
                    <span className="history-source">{record.fromRole || 'UNKNOWN'}</span>
                    <span className="history-arrow">→</span>
                    <span className="history-target">{record.toRole || 'UNKNOWN'}</span>
                  </div>
                  <div className="history-details">
                    <span>From: {shortenAddress(record.from)}</span>
                    <span>To: {shortenAddress(record.to)}</span>
                    <span>Location: {record.location}</span>
                    <span>Date: {formatTimestamp(record.timestamp)}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default DrugVerification;


